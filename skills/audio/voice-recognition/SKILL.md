---
name: 本地语音识别
description: >
  为 Electron / 网页 / Python 桌面应用添加本地语音识别功能。
  支持四种录音方案（naudiodon、SoX、Python sounddevice、MediaRecorder），
  后端使用 funasr SenseVoiceSmall 本地模型识别。
  当用户提出以下意图时触发：添加语音功能、语音识别、麦克风录音、
  语音转文字、speech-to-text、STT 等。
---

# 本地语音识别技能

为应用添加本地语音识别：录音 → 发送到后端 → funasr 本地模型识别 → 返回文本。

## 能力概览

| 能力 | 后端端点 | 说明 |
|------|----------|------|
| 语音转文本 | `POST /api/voice/transcribe` | FormData 上传 WAV/webm，返回 `{"text": "..."}` |
| 获取语音配置 | `GET /api/voice/config` | 返回当前设备配置 |
| 更新语音配置 | `POST /api/voice/config` | 更新麦克风设备选择 |

## 录音方案选择

**按以下条件判断，选择方案：**

```
IF 用户有 Python 环境:
    → 方案三（Python sounddevice）— 门槛最低，跨平台，最稳定
ELSE IF 用户有 Visual Studio Build Tools + 愿意编译:
    → 方案一（naudiodon）— 纯 Node.js，性能最好
ELSE IF 用户有 SoX 或愿意装:
    → 方案二（SoX）— 最简单，patch 后直接用
ELSE:
    → 方案四（MediaRecorder）— 零依赖兜底
```

| 你的情况 | 推荐方案 |
|----------|----------|
| 有 Python 环境 | 方案三 |
| 纯 Node.js，愿意编译 | 方案一 |
| 有 SoX | 方案二 |
| 什么都不想装 | 方案四 |

---

## Agent 执行规范

### 核心约束

- **先检查再安装**：执行前必须检查依赖是否已安装，已安装则跳过
- **验证每一步**：安装 funasr 后验证 import，编译后验证 require
- **不要重复安装**：如果用户说"已经装了"，相信用户，直接进入下一步
- **不要猜测路径**：让用户告诉你实际安装路径，不要假设
- **记录遇到的问题**：如果某一步失败，记录错误信息，不要静默跳过

### 平台规则

| 平台 | 录音方案 | 执行方式 |
|------|----------|----------|
| Electron | naudiodon / SoX / Python / MediaRecorder | IPC 调用主进程 |
| 网页 | MediaRecorder | 浏览器 API |
| Python 桌面端 | sounddevice | 直接调用 |

### 设备匹配规则

**关键概念**：浏览器 `enumerateDevices()` 返回：
- `deviceId`：随机 GUID，每次会话不同，**不能跨进程使用**
- `label`：设备名称（如 `Microphone (Realtek Audio) (aa:bb:cc)`），**可以跨进程匹配**

**渲染进程传 `label` 给主进程，主进程用 `label` 匹配系统设备名。**

**label 末尾 `(aa:bb:cc)` 是 vendor ID，PortAudio/SoX 设备名里没有这部分，匹配时必须去掉：**

```typescript
// TypeScript
const cleanLabel = label.replace(/\s*\([0-9a-fA-F:]+\)\s*$/, '').trim();

// Python
import re
clean_label = re.sub(r'\s*\([0-9a-fA-F:]+\)\s*$', '', device_label).strip()
```

---

## 通用准备（所有方案共用）

### Step 1：安装 funasr

```powershell
<Python路径>\python.exe -m pip install funasr
```

> ⚠️ Python 必须 3.12，3.14+ 不兼容。

**验证**：
```powershell
<Python路径>\python.exe -c "from funasr import AutoModel; print('OK')"
```

### Step 2：下载模型

| 依赖 | 下载地址 | 大小 |
|------|----------|------|
| SenseVoiceSmall | https://github.com/FunAudioLLM/SenseVoice | ~450MB |

### Step 3：修改后端路径

找到 `voice.py`，修改：

```python
MODEL_DIR = r"用户的模型路径\SenseVoiceSmall"
ffmpeg_path = r"用户的ffmpeg路径\bin\ffmpeg.exe"  # 方案四需要
```

### Step 4：启动后端

```powershell
cd <项目目录>/python
<Python路径>\python.exe -m uvicorn api.main:app --host 0.0.0.0 --port 17451
```

**验证**：
```powershell
curl http://127.0.0.1:17451/health
# 应返回 {"status": "healthy", "uptime": ...}
```

> **Electron 应用集成**：后端不应手动启动，应在主进程用 `child_process.spawn` 启动 uvicorn，应用退出时 `process.kill()` 杀掉后端进程。参考 `lifecycle.ts` 的实现。

---

## 方案一：naudiodon（PortAudio）

**适配**：纯 Node.js，有 Visual Studio Build Tools

**版本**：naudiodon@2.x

**安装**：
```powershell
npm install naudiodon@2
```

**为 Electron 编译**：
```powershell
$env:GYP_MSVS_VERSION="2022"
$env:msvs_version="2022"
$env:npm_config_disturl="https://electronjs.org/headers"
$env:npm_config_runtime="electron"
$env:npm_config_target="<Electron版本>"  # 如 28.3.3

cd node_modules/naudiodon && npx node-gyp rebuild
cd ../segfault-handler && npx node-gyp rebuild
```

**验证**：
```powershell
node -e "const pa = require('naudiodon'); console.log(pa.getDevices().filter(d=>d.maxInputChannels>0).length)"
# 应输出设备数量（> 0）
```

**IPC Handler**：
```typescript
const portAudio = require('naudiodon');

// 录音
const ai = new portAudio.AudioIO({
  inOptions: {
    channelCount: 1,
    sampleFormat: portAudio.SampleFormat16Bit,
    sampleRate: 16000,
    deviceId: deviceIndex,  // -1 为默认
    closeOnError: true,
  }
});
ai.on('data', (chunk: Buffer) => { wavChunks.push(chunk); });
ai.start();

// 停止
ai.quit();

// 手动写 WAV 头（44 字节 RIFF）
function buildWavHeader(dataLength: number): Buffer {
  const h = Buffer.alloc(44);
  h.write('RIFF', 0); h.writeUInt32LE(36 + dataLength, 4);
  h.write('WAVE', 8); h.write('fmt ', 12); h.writeUInt32LE(16, 16);
  h.writeUInt16LE(1, 20); h.writeUInt16LE(1, 22); h.writeUInt32LE(16000, 24);
  h.writeUInt32LE(32000, 28); h.writeUInt16LE(2, 32); h.writeUInt16LE(16, 34);
  h.write('data', 36); h.writeUInt32LE(dataLength, 40);
  return h;
}
```

---

## 方案二：node-record-lpcm16 + SoX

**适配**：已有 SoX 或愿意装 SoX

**版本**：node-record-lpcm16@1.0.1，SoX 14.4.2+

**安装**：
```powershell
npm install node-record-lpcm16@1.0.1
winget install SoX
```

**必须 patch**：替换 `node_modules/node-record-lpcm16/recorders/sox.js`：

```javascript
module.exports = (options) => {
  const cmd = 'sox'
  let args = []
  if (options.device) {
    args = ['-t', 'waveaudio', options.device]
  } else {
    args = ['--default-device']
  }
  args = args.concat([
    '--no-show-progress', '--rate', options.sampleRate,
    '--channels', options.channels, '--encoding', 'signed-integer',
    '--bits', '16', '--type', options.audioType, '-',
  ])
  return { cmd, args, spawnOptions: {} }
}
```

**验证**：
```powershell
sox -t waveaudio "设备名" -r 16000 -c 1 -b 16 test.wav trim 0 3
# 检查 test.wav 是否 > 1000 bytes
```

---

## 方案三：Python sounddevice 子进程

**适配**：有 Python 环境，跨平台，最稳

**版本**：Python 3.12，sounddevice@0.4+

**安装**：
```powershell
pip install sounddevice numpy
```

**录音脚本 voice_recorder.py**：
```python
import sys, os, wave, time, json, re
import numpy as np

def find_device(label):
    import sounddevice as sd
    clean = re.sub(r'\s*\([0-9a-fA-F:]+\)\s*$', '', label).strip()
    for i, d in enumerate(sd.query_devices()):
        if d['max_input_channels'] > 0:
            if d['name'] == label or d['name'] == clean:
                return i
    return None

def record(output_path, device_id=None):
    import sounddevice as sd
    marker = output_path + '.recording'
    with open(marker, 'w') as f:
        f.write('recording')
    frames = []
    def cb(indata, fc, ti, s): frames.append(indata.copy())
    idx = find_device(device_id) if device_id else None
    with sd.InputStream(device=idx, samplerate=16000, channels=1, dtype='int16', callback=cb):
        while os.path.exists(marker): time.sleep(0.1)
    if frames:
        audio = np.concatenate(frames, axis=0)
        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(16000)
            wf.writeframes(audio.tobytes())

if __name__ == '__main__':
    if sys.argv[1] == '--list':
        import sounddevice as sd
        print(json.dumps([{'id': i, 'name': d['name']} for i, d in enumerate(sd.query_devices()) if d['max_input_channels'] > 0]))
        sys.exit(0)
    record(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
```

**验证**：
```powershell
python voice_recorder.py --list  # 应列出设备
```

---

## 方案四：浏览器 MediaRecorder

**适配**：零依赖兜底，能接受有损格式

**不需要 IPC**，直接在渲染进程调用：

> ⚠️ **Electron 中使用 MediaRecorder 需要主进程放行麦克风权限**。在 `main/index.ts` 中添加：
> ```typescript
> session.defaultSession.setPermissionRequestHandler((webContents, permission, callback) => {
>   if (['media', 'microphone', 'camera'].includes(permission)) {
>     callback(true);
>   } else {
>     callback(false);
>   }
> });
> ```

```typescript
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const mr = new MediaRecorder(stream, { mimeType: 'audio/webm' });
mr.ondataavailable = (e) => chunks.push(e.data);
mr.onstop = async () => {
  const blob = new Blob(chunks, { type: 'audio/webm' });
  const fd = new FormData();
  fd.append('audio', blob, 'recording.webm');
  await fetch('http://localhost:17451/api/voice/transcribe', { method: 'POST', body: fd });
};
mr.start();
mr.stop();
```

**后端需要 ffmpeg 转换 webm → wav。**

---

## 通用发送逻辑

```typescript
const FormData = require('form-data');
const http = require('http');
const formData = new FormData();
formData.append('audio', fs.createReadStream(wavFilePath), 'recording.wav');
const result = await new Promise<string>((resolve, reject) => {
  const req = http.request({
    hostname: '127.0.0.1', port: 17451, path: '/api/voice/transcribe', method: 'POST',
    headers: formData.getHeaders(),
  }, res => { let body = ''; res.on('data', c => body += c); res.on('end', () => resolve(body)); });
  req.on('error', reject);
  formData.pipe(req);
});
return JSON.parse(result);
// 成功: {"text": "识别文本"}
// 失败: {"error": "错误信息"}
```

---

## 问题排查

### 按顺序排查，每步确认后再进入下一步：

**第一步：确认录音正常**
```powershell
# 方案一
node -e "const pa = require('naudiodon'); console.log(pa.getDevices().filter(d=>d.maxInputChannels>0).length)"
# 方案二
sox -t waveaudio "设备名" -r 16000 -c 1 -b 16 test.wav trim 0 3
# 方案三
python voice_recorder.py --list
```

**第二步：确认后端识别正常**
```powershell
curl -X POST -F "audio=@test.wav" http://127.0.0.1:17451/api/voice/transcribe
```

**第三步：确认 IPC 通信正常**
- 检查 Electron 主进程日志
- 没有日志 → rebuild dist + 重启 Electron

**第四步：确认设备匹配正确**
- 检查是否选到了错误的麦克风

**第五步：确认构建生效**
```powershell
npx vite build
```

---

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `portAudio.AudioInput is not a constructor` | naudiodon API 版本不对 | 用 `new portAudio.AudioIO({ inOptions: {...} })`，确认 naudiodon@2.x |
| `录音库 naudiodon 未安装` | 未为 Electron 编译 | node-gyp + Electron 头文件重新编译 |
| `MODULE_VERSION 119 vs 137` | segfault-handler 未编译 | 编译 segfault-handler |
| SoX `no default audio device` | AUDIODEV 不生效 | patch sox.js，用 `-t waveaudio <device>` |
| SoX 录音 0 字节 | 设备名不匹配 | 去掉 vendor ID |
| `OverconstrainedError` | deviceId 不匹配 | 用 label 匹配，不要用浏览器 deviceId |
| `No handler registered` | IPC 未注册 | rebuild dist + 重启 |
| `ModuleNotFoundError: funasr` | funasr 未安装 | `pip install funasr`（Python 3.12） |
| 识别结果为空 | 音频太短 | WAV > 1000 bytes |

---

## 依赖

| 依赖 | 版本 | 必需 |
|------|------|------|
| Python | 3.12 | ✅ |
| funasr | 最新 | ✅ |
| SenseVoiceSmall | 模型文件 | ✅ |
| naudiodon | @2.x | 方案一 |
| node-record-lpcm16 | @1.0.1 | 方案二 |
| SoX | 14.4.2+ | 方案二 |
| sounddevice | @0.4+ | 方案三 |
| ffmpeg | 最新 | 方案四 |
| Visual Studio Build Tools | 2022+ | 方案一 |
