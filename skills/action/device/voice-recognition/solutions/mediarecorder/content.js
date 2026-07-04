(function() {
    'use strict';

    const VOICE_API = 'http://localhost:17451/api/voice/transcribe';
    let recording = false;
    let duration = 0;
    let mr = null;
    let timer = null;
    let selectedDeviceId = '';

    function log(msg) {
        console.log('[Voice Input]', msg);
    }

    function updateButton() {
        const btn = document.querySelector('.mimo-voice-btn');
        if (!btn) return;
        if (recording) {
            btn.classList.add('recording');
            btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><rect x="3" y="3" width="10" height="10" rx="2"/></svg>';
            btn.style.color = '#ff4d4f';
            btn.title = '录音中 ' + duration + 's';
        } else {
            btn.classList.remove('recording');
            btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="5.5" y="1.5" width="5" height="9" rx="2.5"/><path d="M2 7.5a5 5 0 0110 0"/><path d="M8 12.5v2"/></svg>';
            btn.style.color = '#8b949e';
            btn.title = '语音输入';
        }
    }

    function stopRecording() {
        if (timer) { clearInterval(timer); timer = null; }
        if (mr?.state === 'recording') mr.stop();
        recording = false;
        duration = 0;
        updateButton();
    }

    function insertTextToInput(text) {
        let inputArea = document.querySelector('[contenteditable]');
        
        if (!inputArea) {
            inputArea = document.querySelector('[placeholder*="问"]');
        }
        
        if (!inputArea) {
            inputArea = document.querySelector('.flex-1');
        }
        
        if (!inputArea) {
            inputArea = document.querySelector('textarea');
        }
        
        if (!inputArea) {
            log('input area not found!');
            alert('未找到输入框，请刷新页面重试');
            return;
        }

        inputArea.focus();
        
        if (inputArea.tagName === 'TEXTAREA' || inputArea.tagName === 'INPUT') {
            inputArea.value = (inputArea.value || '') + text.trim();
        } else {
            const selection = window.getSelection();
            
            if (selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                range.deleteContents();
                const textNode = document.createTextNode(text);
                range.insertNode(textNode);
                range.collapse(false);
                selection.removeAllRanges();
                selection.addRange(range);
            } else {
                const currentText = inputArea.textContent || '';
                inputArea.textContent = currentText.trim() + ' ' + text.trim();
            }
        }

        const events = ['input', 'change'];
        events.forEach(evt => {
            inputArea.dispatchEvent(new InputEvent(evt, { bubbles: true, cancelable: true, inputType: 'insertText', data: text }));
        });
        log('text inserted: ' + text.slice(0, 20) + '...');
    }

    function doRecording(deviceId) {
        const constraints = deviceId ? { audio: { deviceId: { exact: deviceId } } } : { audio: true };
        
        navigator.mediaDevices.getUserMedia(constraints)
            .then(stream => {
                const track = stream.getAudioTracks()[0];
                log('using microphone:', track.label, track.getSettings());
                mr = new MediaRecorder(stream, { mimeType: 'audio/webm' });
                const chunks = [];
                mr.ondataavailable = (e) => chunks.push(e.data);
                mr.onstop = async () => {
                    log('recording stopped');
                    stream.getTracks().forEach(t => t.stop());
                    const blob = new Blob(chunks, { type: 'audio/webm' });
                    log('blob size: ' + blob.size);
                    if (blob.size < 100) { log('blob too small'); updateButton(); return; }

                    try {
                        log('sending to API: ' + VOICE_API);
                        const fd = new FormData();
                        fd.append('audio', blob, 'recording.webm');
                        const res = await fetch(VOICE_API, { 
                            method: 'POST', 
                            body: fd,
                            mode: 'cors'
                        });
                        log('response status: ' + res.status);
                        const data = await res.json();
                        log('response data:', data);

                        if (data.text?.trim()) {
                            insertTextToInput(data.text.trim());
                        } else if (data.result?.trim()) {
                            insertTextToInput(data.result.trim());
                        } else {
                            log('No text returned:', data);
                        }
                    } catch (err) {
                        log('API error:', err);
                        alert('语音识别失败：' + err.message);
                    }
                    updateButton();
                };
                mr.start();
                recording = true;
                duration = 0;
                updateButton();
                timer = setInterval(() => { duration++; updateButton(); }, 1000);
                setTimeout(() => { if (mr?.state === 'recording') stopRecording(); }, 60000);
                log('recording started');
            })
            .catch(err => {
                log('microphone error:', err);
                alert('请允许麦克风权限');
            });
    }

    function showMicSelector(mics) {
        const selector = document.createElement('div');
        selector.style.cssText = `
            position: fixed;
            bottom: 80px;
            right: 20px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 8px;
            min-width: 200px;
            z-index: 9999;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        `;

        const title = document.createElement('div');
        title.textContent = '选择麦克风';
        title.style.cssText = 'padding: 8px 12px; font-size: 12px; color: #8b949e; border-bottom: 1px solid #30363d; margin-bottom: 4px;';
        selector.appendChild(title);

        mics.forEach(mic => {
            const item = document.createElement('button');
            item.textContent = mic.label || '未知麦克风';
            item.style.cssText = `
                display: block;
                width: 100%;
                padding: 8px 12px;
                text-align: left;
                border: none;
                background: transparent;
                color: #e6edf3;
                font-size: 13px;
                cursor: pointer;
                border-radius: 4px;
                margin: 2px 0;
            `;
            item.onmouseenter = () => item.style.background = '#30363d';
            item.onmouseleave = () => item.style.background = 'transparent';
            item.onclick = () => {
                selectedDeviceId = mic.deviceId;
                selector.remove();
                doRecording(mic.deviceId);
            };
            selector.appendChild(item);
        });

        document.body.appendChild(selector);
        document.addEventListener('click', function close(e) {
            if (!selector.contains(e.target)) {
                selector.remove();
                document.removeEventListener('click', close);
            }
        });
    }

    function startRecording() {
        log('starting recording...');
        navigator.mediaDevices.enumerateDevices()
            .then(devices => {
                const mics = devices.filter(d => d.kind === 'audioinput');
                log('available microphones:', mics.map(m => m.label || 'unknown'));
                
                if (mics.length === 0) {
                    alert('未找到麦克风设备');
                    return;
                }
                
                if (mics.length === 1 || selectedDeviceId) {
                    doRecording(selectedDeviceId);
                } else {
                    showMicSelector(mics);
                }
            })
            .catch(err => {
                log('failed to enumerate devices:', err);
                doRecording('');
            });
    }

    function createVoiceButton() {
        if (document.querySelector('.mimo-voice-btn')) return;

        const rightArea = document.querySelector('.absolute.bottom-2.right-2');
        if (!rightArea) { log('right area not found'); return; }

        rightArea.style.pointerEvents = 'auto';

        const btn = document.createElement('button');
        btn.className = 'mimo-voice-btn';
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="5.5" y="1.5" width="5" height="9" rx="2.5"/><path d="M2 7.5a5 5 0 0110 0"/><path d="M8 12.5v2"/></svg>';
        btn.title = '语音输入';

        Object.assign(btn.style, {
            width: '28px',
            height: '28px',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'transparent',
            border: 'none',
            cursor: 'pointer',
            color: '#8b949e',
            marginRight: '4px',
            transition: 'all 0.2s',
            zIndex: '1000'
        });

        btn.addEventListener('mouseenter', () => { if (!recording) btn.style.color = '#e6edf3'; });
        btn.addEventListener('mouseleave', () => { if (!recording) btn.style.color = '#8b949e'; });
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (recording) stopRecording(); else startRecording();
        });
        btn.addEventListener('mousedown', (e) => { e.preventDefault(); e.stopPropagation(); });

        rightArea.insertBefore(btn, rightArea.firstChild);

        const style = document.createElement('style');
        style.textContent = '.mimo-voice-btn.recording { animation: voice-pulse 1s infinite; } @keyframes voice-pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }';
        document.head.appendChild(style);

        log('voice button created');
    }

    createVoiceButton();

    const observer = new MutationObserver(() => {
        if (!document.querySelector('.mimo-voice-btn')) {
            createVoiceButton();
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });

    log('Voice Input loaded via Chrome Extension');
})();
