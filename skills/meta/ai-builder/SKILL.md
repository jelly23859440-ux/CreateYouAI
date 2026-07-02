---
name: AI 构建器
layer: meta
category: ai-builder
description: >
  帮用户从 Skill 仓库中挑选合适的 Skill，组合成自己的 AI。
  当用户想要构建 AI、搭建智能体、创建自动化工作流、
  或描述"我想做一个能做 X 的 AI"时触发。
  关键词：构建 AI、搭建智能体、做 AI、自动化、工作流、组合 skill。
---

# AI 构建器

用户描述想要什么 AI，你帮他从仓库挑选 Skill 并组合。

## 执行流程

### Step 1：了解用户需求

问用户以下问题（如果用户已经说清楚了就跳过）：

1. **你想做什么？**（一句话描述目标）
2. **什么平台？**（桌面应用 / 网页 / Python 脚本 / 不确定）
3. **有什么技术偏好？**（有 Python 环境 / 纯 Node.js / 都行）

如果用户说"不确定"或"帮我想想"，用下方的「构建 AI 需要考虑的内容」框架帮他梳理：从输入→处理→输出→安全→人格五个维度引导。

### Step 2：扫描可用 Skill

列出仓库中所有 Skill：

```bash
find skills/ -name "SKILL.md" -type f
```

读取每个 SKILL.md 的 frontmatter，获取 name、layer、category、description。

### Step 3：推荐 Skill 组合

根据用户需求，从仓库中匹配 Skill。

**匹配逻辑**：
- 读每个 SKILL.md 的 description，判断是否与用户需求相关
- 读 layer 和 category，按能力层组织推荐
- 优先推荐 core 层（核心能力），再补充 action/identity 层

**输出格式**：

```markdown
根据你的需求，推荐以下 Skill 组合：

| Skill | 能力层 | 用途 | 为什么选它 |
|-------|--------|------|-----------|
| voice-recognition | action/device | 语音输入 | 你说需要语音交互 |
| file-manager | action/file | 文件操作 | 你说需要读写文件 |

**不需要的 Skill**：
- code-review（你说不需要代码审查）

**下一步**：
1. 先安装第一个 Skill 的依赖
2. 再配置第二个 Skill
3. 我帮你逐步集成
```

### Step 4：生成构建方案

帮用户生成一个构建计划：

```markdown
# 你的 AI 构建计划

## 目标
<用户描述>

## 需要的 Skill
1. <skill-1> — <能力层> — <用途>
2. <skill-2> — <能力层> — <用途>

## 安装顺序
1. 先装 <skill-1>（core 层基础能力）
2. 再装 <skill-2>（action 层执行能力）
3. 最后配 <skill-3>（identity 层身份设定）

## 预估时间
- <skill-1>：<X 分钟>
- <skill-2>：<X 分钟>
- 总计：<X 分钟>
```

### Step 5：逐步执行

按计划逐个安装 Skill，每个 Skill 安装后验证。

## 示例对话

**用户**：我想做一个能语音控制电脑的 AI

**AI**：
1. 扫描仓库，找到 voice-recognition（action/device — 语音输入）
2. 推荐：voice-recognition + file-manager（action/file — 语音控制文件操作）
3. 生成构建计划
4. 逐步安装

## 注意事项

- 如果仓库里没有用户需要的 Skill，告诉用户可以自己写一个（参考 meta/contribute）
- 不要推荐太多 Skill（3-5 个为宜），太多会复杂
- 优先推荐经过验证的 Skill（标记为 ✅ Ready 的）

---

## 附录：构建 AI 应用需要考虑的内容

当用户不确定要做什么 AI 时，用以下框架帮他梳理思路。

### 1. 输入：AI 怎么接收信息？

| 类型 | 说明 | 对应 Skill |
|------|------|-----------|
| 文字输入 | 用户打字对话 | core/conversation |
| 语音输入 | 用户说话 | action/device |
| 文件输入 | 上传文档/图片 | action/file |
| 数据输入 | CSV/JSON/API 数据 | action/file |
| 实时输入 | 传感器/摄像头/麦克风 | action/device, action/tool |

### 2. 处理：AI 怎么思考和行动？

| 类型 | 说明 | 对应 Skill |
|------|------|-----------|
| 记忆 | 记住之前的对话和偏好 | core/memory |
| 推理 | 分析问题、做决策 | core/reasoning |
| 任务 | 规划步骤、执行任务 | core/reasoning |
| 工具 | 调用 API、操作文件、执行命令 | action/tool |
| 学习 | 从反馈中改进 | meta/skill-learn |

### 3. 输出：AI 怎么反馈？

| 类型 | 说明 | 对应 Skill |
|------|------|-----------|
| 文字回复 | 对话形式 | core/conversation |
| 语音回复 | 朗读回答 | action/device |
| 文件输出 | 生成文档/代码/图片 | action/code, action/file |
| 操作执行 | 自动执行任务 | core/reasoning, action/tool |
| 界面展示 | 显示结果/图表 | action/web |

### 4. 安全：AI 需要什么保护？

| 类型 | 说明 | 对应 Skill |
|------|------|-----------|
| 内容过滤 | 屏蔽有害内容 | identity/safety |
| 权限控制 | 限制能做什么 | identity/safety |
| 审计日志 | 记录操作历史 | identity/safety |
| 人机协作 | 关键操作需人确认 | identity/safety |

### 5. 人格：AI 是什么样的？

| 类型 | 说明 | 对应 Skill |
|------|------|-----------|
| 角色定位 | 是助手/老师/伙伴？ | identity/personality |
| 语气风格 | 正式/友好/幽默？ | identity/personality |
| 专业领域 | 擅长什么？ | identity/knowledge |