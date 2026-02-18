"""
Demo Router - Voice Chat Demo UI for testing the voice experience.

Provides a simple SPA endpoint at /spa for testing:
- Microphone input with real-time STT streaming
- Text chat with agent
- Simultaneous text streaming and TTS audio playback
- Support for Arabic (Kuwaiti dialect) and English
"""
import logging

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/spa", tags=["Demo UI"])

# HTML template for the voice chat demo
DEMO_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PACI Agent - Voice Demo | ساهل</title>
    <style>
        :root {
            --primary: #0066cc;
            --primary-dark: #004d99;
            --secondary: #00a884;
            --bg-dark: #111b21;
            --bg-chat: #0b141a;
            --bg-input: #202c33;
            --bg-user: #005c4b;
            --bg-agent: #202c33;
            --text-primary: #e9edef;
            --text-secondary: #8696a0;
            --border: #2a3942;
            --recording: #ef4444;
            --listening: #22c55e;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Header */
        .header {
            background: var(--bg-input);
            padding: 16px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
        }

        .header-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .header-title h1 {
            font-size: 18px;
            font-weight: 600;
        }

        .header-title span {
            color: var(--text-secondary);
            font-size: 14px;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--text-secondary);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--text-secondary);
        }

        .status-dot.connected {
            background: var(--listening);
        }

        .status-dot.recording {
            background: var(--recording);
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* Language Toggle */
        .lang-toggle {
            display: flex;
            gap: 4px;
            background: var(--bg-dark);
            border-radius: 8px;
            padding: 4px;
        }

        .lang-btn {
            padding: 6px 12px;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }

        .lang-btn.active {
            background: var(--primary);
            color: white;
        }

        /* Chat Container */
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: var(--bg-chat);
        }

        .message {
            max-width: 75%;
            margin-bottom: 12px;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            margin-right: auto;
            margin-left: 0;
        }

        .message.agent {
            margin-left: auto;
            margin-right: 0;
        }

        .message-bubble {
            padding: 10px 14px;
            border-radius: 12px;
            line-height: 1.5;
            font-size: 15px;
            position: relative;
        }

        .message.user .message-bubble {
            background: var(--bg-user);
            border-bottom-left-radius: 4px;
        }

        .message.agent .message-bubble {
            background: var(--bg-agent);
            border-bottom-right-radius: 4px;
        }

        .message-meta {
            font-size: 11px;
            color: var(--text-secondary);
            margin-top: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .message.user .message-meta {
            justify-content: flex-start;
        }

        .message.agent .message-meta {
            justify-content: flex-end;
        }

        /* Typing indicator */
        .typing-indicator {
            display: inline-flex;
            gap: 4px;
            padding: 8px 12px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: var(--text-secondary);
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-8px); }
        }

        /* Thought Indicator (Chain-of-Thought Feedback) */
        .thought-message {
            max-width: 90%;
        }

        .thought-bubble {
            background: linear-gradient(135deg, var(--bg-agent) 0%, #1a2c38 100%) !important;
            border: 1px solid var(--primary);
            border-radius: 16px !important;
        }

        .thought-content {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 8px;
        }

        .thought-icon {
            font-size: 16px;
            animation: thoughtPulse 1.5s ease-in-out infinite;
        }

        .thought-text {
            color: var(--text-secondary);
            font-size: 13px;
            font-style: italic;
        }

        @keyframes thoughtPulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }

        /* Input Area */
        .input-area {
            background: var(--bg-input);
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-top: 1px solid var(--border);
        }

        .text-input {
            flex: 1;
            background: var(--bg-dark);
            border: none;
            border-radius: 24px;
            padding: 12px 20px;
            color: var(--text-primary);
            font-size: 15px;
            outline: none;
            direction: auto;
        }

        .text-input::placeholder {
            color: var(--text-secondary);
        }

        /* Buttons */
        .btn {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }

        .btn-send {
            background: var(--primary);
            color: white;
        }

        .btn-send:hover {
            background: var(--primary-dark);
        }

        .btn-send:disabled {
            background: var(--bg-dark);
            color: var(--text-secondary);
            cursor: not-allowed;
        }

        .btn-mic {
            background: var(--bg-dark);
            color: var(--text-primary);
            position: relative;
        }

        .btn-mic:hover {
            background: var(--border);
        }

        .btn-mic.recording {
            background: var(--recording);
            color: white;
            animation: pulse 1s infinite;
        }

        .btn-mic.disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* Live Transcript */
        .live-transcript {
            position: absolute;
            bottom: 100%;
            left: 20px;
            right: 20px;
            background: var(--bg-dark);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 8px;
            font-size: 14px;
            color: var(--text-secondary);
            display: none;
        }

        .live-transcript.visible {
            display: block;
            animation: fadeIn 0.2s ease;
        }

        .live-transcript .interim {
            color: var(--text-secondary);
            font-style: italic;
        }

        .live-transcript .final {
            color: var(--text-primary);
        }

        /* Audio indicator */
        .audio-indicator {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            margin-right: 8px;
        }

        .audio-bar {
            width: 3px;
            height: 12px;
            background: var(--secondary);
            border-radius: 2px;
            animation: audioWave 0.5s ease-in-out infinite;
        }

        .audio-bar:nth-child(2) { animation-delay: 0.1s; }
        .audio-bar:nth-child(3) { animation-delay: 0.2s; }
        .audio-bar:nth-child(4) { animation-delay: 0.3s; }

        @keyframes audioWave {
            0%, 100% { height: 4px; }
            50% { height: 12px; }
        }

        /* Transcript Preview (when recording) */
        .input-wrapper {
            flex: 1;
            position: relative;
        }

        /* Debug panel (hidden by default) */
        .debug-panel {
            position: fixed;
            bottom: 100px;
            right: 20px;
            background: var(--bg-dark);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            font-size: 12px;
            font-family: monospace;
            max-width: 300px;
            max-height: 200px;
            overflow-y: auto;
            display: none;
        }

        .debug-panel.visible {
            display: block;
        }

        /* SVG Icons */
        .icon {
            width: 24px;
            height: 24px;
        }

        /* Loading state for agent response */
        .agent-loading {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Voice waveform */
        .waveform {
            display: flex;
            align-items: center;
            gap: 2px;
            height: 24px;
        }

        .waveform-bar {
            width: 3px;
            background: var(--secondary);
            border-radius: 2px;
            transition: height 0.1s;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="header-title">
            <h1>ساهل</h1>
            <span>PACI Voice Demo</span>
        </div>

        <div class="status-indicator">
            <div class="status-dot" id="statusDot"></div>
            <span id="statusText">Connecting...</span>
        </div>

        <div class="lang-toggle">
            <button class="lang-btn active" data-lang="ar-KW">عربي</button>
            <button class="lang-btn" data-lang="en-US">English</button>
        </div>
    </header>

    <!-- Chat Messages -->
    <div class="chat-container" id="chatContainer">
        <div class="message agent">
            <div class="message-bubble">
                مرحباً! أنا ساهل، مساعدك الرقمي من الهيئة العامة للمعلومات المدنية. كيف أقدر أساعدك اليوم؟
                <br><br>
                <em style="color: var(--text-secondary); font-size: 13px;">
                    Hello! I'm Sahel, your digital assistant from PACI. How can I help you today?
                </em>
            </div>
            <div class="message-meta">
                <span>ساهل</span>
            </div>
        </div>
    </div>

    <!-- Live Transcript Overlay -->
    <div class="live-transcript" id="liveTranscript">
        <span class="final" id="transcriptFinal"></span>
        <span class="interim" id="transcriptInterim"></span>
    </div>

    <!-- Input Area -->
    <div class="input-area">
        <button class="btn btn-mic" id="micBtn" title="Click to start/stop | قل 'ساهل' للبدء">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
                <line x1="8" y1="23" x2="16" y2="23"/>
            </svg>
        </button>

        <div class="input-wrapper">
            <input type="text" class="text-input" id="textInput" 
                   placeholder="اكتب رسالتك هنا... / Type your message..." 
                   autocomplete="off">
        </div>

        <button class="btn btn-send" id="sendBtn" disabled title="Send message">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
        </button>
    </div>

    <!-- Debug Panel (toggle with Ctrl+D) -->
    <div class="debug-panel" id="debugPanel">
        <div id="debugLog"></div>
    </div>

    <!-- Hidden audio element for TTS playback -->
    <audio id="audioPlayer" style="display: none;" playsinline preload="auto"></audio>

    <script>
    (function() {
        'use strict';

        // =================================================================
        // Configuration
        // =================================================================
        const CONFIG = {
            wsBaseUrl: `ws://${window.location.host}`,
            apiBaseUrl: `http://${window.location.host}`,
            sampleRate: 16000,
            audioChunkSize: 4096,
            language: 'ar-KW',
            ttsVoice: 'nova',

            // Voice Activity Detection (VAD) and Wake Word
            silenceThresholdRMS: 0.02,
            silenceDurationMs: 2000,
            wakeWordEnabled: true,
            // Arabic wake word variations (with/without diacritics, alef variations, etc.)
            wakeWordPhrases: [
                'ساهل', 'سَاهِل', 'سَاهَل', 'ساهِل', 'ساهَل',  // base + diacritics
                'صاهل', 'صَاهِل',  // sad instead of seen (common confusion)
                'يا ساهل', 'ياساهل', 'يا سَاهِل',  // with "ya"
                'اساهل', 'أساهل', 'إساهل',  // with alef variations at start
                'سهل', 'سَهَل', 'سَهِل',  // without alef (shorter form)
                'يا سهل', 'ياسهل'  // ya + shorter form
            ]
        };

        // =================================================================
        // State
        // =================================================================
        const state = {
            // Connection states
            chatWsConnected: false,
            sttWsConnected: false,

            // WebSocket connections
            chatWs: null,
            sttWs: null,

            // Audio recording
            mediaRecorder: null,
            audioContext: null,
            audioStream: null,
            isRecording: false,

            // Audio playback control
            allowPlayback: true,

            // Silence detection (VAD)
            silenceIntervalId: null,
            silenceStartedAt: null,
            audioAnalyser: null,
            audioSource: null,

            // Wake word detection (cross-browser)
            wakeWordEnabled: false,
            wakeWordListening: false,
            wakeWordStream: null,
            wakeWordAudioContext: null,
            wakeWordSource: null,
            wakeWordAnalyser: null,
            wakeWordIntervalId: null,

            // Session info
            threadId: generateUUID(),
            sttSessionId: null,
            currentMessageId: null,

            // Transcription state
            transcriptFinal: '',
            transcriptInterim: '',

            // TTS audio queue
            audioQueue: [],
            isPlayingAudio: false,

            // Current agent response
            currentAgentText: '',
            agentMessageElement: null,
            currentResponse: '',

            // Pending audio for autoplay blocked scenario
            pendingAudioUrl: null
        };

        // =================================================================
        // DOM Elements
        // =================================================================
        const elements = {
            chatContainer: document.getElementById('chatContainer'),
            textInput: document.getElementById('textInput'),
            sendBtn: document.getElementById('sendBtn'),
            micBtn: document.getElementById('micBtn'),
            statusDot: document.getElementById('statusDot'),
            statusText: document.getElementById('statusText'),
            liveTranscript: document.getElementById('liveTranscript'),
            transcriptFinal: document.getElementById('transcriptFinal'),
            transcriptInterim: document.getElementById('transcriptInterim'),
            audioPlayer: document.getElementById('audioPlayer'),
            debugPanel: document.getElementById('debugPanel'),
            debugLog: document.getElementById('debugLog'),
            langBtns: document.querySelectorAll('.lang-btn')
        };

        // =================================================================
        // Utility Functions
        // =================================================================
        function generateUUID() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = Math.random() * 16 | 0;
                const v = c === 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        }

        // Normalize Arabic text by removing diacritics and normalizing characters
        function normalizeArabic(text) {
            if (!text) return '';
            return text
                // Remove Arabic diacritics (tashkeel)
                .replace(/[\u064B-\u065F\u0670]/g, '')  // fatha, damma, kasra, shadda, sukun, etc.
                // Normalize alef variations to plain alef
                .replace(/[أإآٱ]/g, 'ا')
                // Normalize teh marbuta to heh
                .replace(/ة/g, 'ه')
                // Normalize alef maksura to yeh
                .replace(/ى/g, 'ي')
                // Remove tatweel (kashida)
                .replace(/ـ/g, '')
                // Normalize spaces
                .replace(/\s+/g, ' ')
                .trim();
        }

        // Check if text contains wake word (with normalization)
        function containsWakeWord(transcript) {
            const normalizedTranscript = normalizeArabic(transcript.toLowerCase());

            // Check against all wake word phrases
            for (const phrase of CONFIG.wakeWordPhrases) {
                const normalizedPhrase = normalizeArabic(phrase.toLowerCase());
                if (normalizedTranscript.includes(normalizedPhrase)) {
                    return true;
                }
            }

            // Also check for core pattern "س*ه*ل" (seen + heh + lam) with anything in between
            // This catches variations like ساهل, سهل, سَاهِل, etc.
            const corePattern = /س[اآأإ]?ه[يى]?ل/;
            if (corePattern.test(normalizedTranscript)) {
                return true;
            }

            return false;
        }

        function log(message, type = 'info') {
            console.log(`[${type.toUpperCase()}] ${message}`);
            const debugLog = elements.debugLog;
            const entry = document.createElement('div');
            entry.style.color = type === 'error' ? '#ef4444' : type === 'warn' ? '#f59e0b' : '#8696a0';
            entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            debugLog.appendChild(entry);
            debugLog.scrollTop = debugLog.scrollHeight;
        }

        function updateStatus(connected, text) {
            elements.statusDot.className = 'status-dot' + (connected ? ' connected' : '');
            elements.statusText.textContent = text;
        }

        function scrollToBottom() {
            elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
        }

        // =================================================================
        // Message UI Functions
        // =================================================================
        function addMessage(text, isUser = false, isStreaming = false) {
            const message = document.createElement('div');
            message.className = `message ${isUser ? 'user' : 'agent'}`;
            if (!isUser && isStreaming) {
                message.id = 'streamingMessage';
            }

            const bubble = document.createElement('div');
            bubble.className = 'message-bubble';
            bubble.textContent = text;

            const meta = document.createElement('div');
            meta.className = 'message-meta';
            meta.innerHTML = `<span>${isUser ? 'أنت' : 'ساهل'}</span>`;

            message.appendChild(bubble);
            message.appendChild(meta);
            elements.chatContainer.appendChild(message);
            scrollToBottom();

            return bubble;
        }

        function updateAgentMessage(messageId, text) {
            // Find or create the streaming message element
            let streamingMsg = document.getElementById('streamingMessage');

            if (!streamingMsg) {
                // Create new message if it doesn't exist
                removeTypingIndicator();
                addMessage(text, false, true);
            } else {
                // Update existing message
                const bubble = streamingMsg.querySelector('.message-bubble');
                if (bubble) {
                    bubble.textContent = text;
                    scrollToBottom();
                }
            }
        }

        function addTypingIndicator() {
            const message = document.createElement('div');
            message.className = 'message agent';
            message.id = 'typingIndicator';
            message.innerHTML = `
                <div class="message-bubble">
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            `;
            elements.chatContainer.appendChild(message);
            scrollToBottom();
        }

        function removeTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) indicator.remove();
        }

        // =================================================================
        // Thought Indicator (Chain-of-Thought Feedback)
        // =================================================================
        function showThoughtIndicator(thought) {
            // Remove existing indicator if any
            hideThoughtIndicator();

            const indicator = document.createElement('div');
            indicator.className = 'message agent thought-message';
            indicator.id = 'thoughtIndicator';
            indicator.innerHTML = `
                <div class="message-bubble thought-bubble">
                    <div class="thought-content">
                        <span class="thought-icon">🧠</span>
                        <span class="thought-text">${thought || 'Processing...'}</span>
                    </div>
                </div>
            `;
            elements.chatContainer.appendChild(indicator);
            scrollToBottom();
        }

        function updateThoughtIndicator(thought) {
            const indicator = document.getElementById('thoughtIndicator');
            if (indicator) {
                const textEl = indicator.querySelector('.thought-text');
                if (textEl) {
                    textEl.textContent = thought;
                    scrollToBottom();
                }
            } else {
                // If no indicator exists, create one
                showThoughtIndicator(thought);
            }
        }

        function hideThoughtIndicator() {
            const indicator = document.getElementById('thoughtIndicator');
            if (indicator) {
                // Fade out animation
                indicator.style.opacity = '0';
                indicator.style.transition = 'opacity 0.3s ease';
                setTimeout(() => indicator.remove(), 300);
            }
        }

        // =================================================================
        // Chat WebSocket (for agent communication)
        // =================================================================
        function connectChatWebSocket() {
            const wsUrl = `${CONFIG.wsBaseUrl}/ws/${state.threadId}`;
            log(`Connecting to chat WebSocket: ${wsUrl}`);

            state.chatWs = new WebSocket(wsUrl);

            state.chatWs.onopen = () => {
                state.chatWsConnected = true;
                log('Chat WebSocket connected');
                updateStatus(true, 'Connected | متصل');
                elements.sendBtn.disabled = false;
            };

            state.chatWs.onclose = () => {
                state.chatWsConnected = false;
                log('Chat WebSocket disconnected', 'warn');
                updateStatus(false, 'Disconnected | غير متصل');
                elements.sendBtn.disabled = true;

                // Reconnect after delay
                setTimeout(connectChatWebSocket, 3000);
            };

            state.chatWs.onerror = (error) => {
                log(`Chat WebSocket error: ${error}`, 'error');
            };

            state.chatWs.onmessage = (event) => {
                handleChatMessage(event.data);
            };
        }

        function handleChatMessage(data) {
            try {
                const message = JSON.parse(data);
                const type = message.type;

                log(`Chat message received: ${type}`);

                switch (type) {
                    case 'thought-stream-start':
                        log(`🧠 Thought stream started: ${message.thought_id}`);
                        showThoughtIndicator(message.thought || 'Processing...');
                        break;

                    case 'thought-stream-delta':
                        log(`🧠 Thinking: ${message.thought}`);
                        updateThoughtIndicator(message.thought);
                        break;

                    case 'thought-stream-end':
                        log(`🧠 Thought stream ended`);
                        hideThoughtIndicator();
                        break;

                    case 'text-stream-start':
                        removeTypingIndicator();
                        hideThoughtIndicator();
                        state.currentAgentText = '';
                        state.agentMessageElement = addMessage('', false, true);
                        state.currentMessageId = message.message_id;
                        break;

                    case 'text-stream-chunk':
                        if (state.agentMessageElement && message.text) {
                            state.currentAgentText += message.text;
                            state.agentMessageElement.textContent = state.currentAgentText;
                            scrollToBottom();
                        }
                        break;

                    case 'text-stream-end':
                        log(`Agent response complete: ${state.currentAgentText.length} chars`);
                        state.agentMessageElement = null;

                        // Request TTS for the complete response
                        if (state.currentAgentText.trim()) {
                            generateTTS(state.currentAgentText);
                        }
                        break;

                    case 'audio-stream-start':
                        log('Audio stream started');
                        break;

                    case 'audio-stream-chunk':
                        if (message.audio_data) {
                            queueAudioChunk(message.audio_data);
                        }
                        break;

                    case 'audio-stream-end':
                        log('Audio stream ended');
                        break;

                    case 'tool-call-start':
                        log(`Tool call: ${message.tool_name}`);
                        if (message.thought) {
                            updateThoughtIndicator(message.thought);
                        }
                        break;

                    case 'tool-call-end':
                        log(`Tool complete: ${message.tool_name} (${message.status})`);
                        break;

                    default:
                        log(`Unhandled message type: ${type}`);
                }
            } catch (e) {
                log(`Failed to parse chat message: ${e}`, 'error');
            }
        }

        function sendMessage(text) {
            // Use STT WebSocket for sending messages (unified WebSocket)
            const wsConnected = state.sttWsConnected && state.sttWs && state.sttWs.readyState === WebSocket.OPEN;

            if (!wsConnected || !text.trim()) {
                log(`Cannot send message: WebSocket connected=${wsConnected}, text="${text.substring(0, 20)}..."`, 'warn');
                return;
            }

            // Add user message to UI
            addMessage(text, true);

            // Clear input
            elements.textInput.value = '';
            elements.sendBtn.disabled = true;

            // Show typing indicator
            addTypingIndicator();

            // Send to agent via STT WebSocket using new text message format
            const payload = {
                type: 'text',
                text: text,
                sender: state.threadId,
                language: CONFIG.language,
                timestamp: new Date().toISOString(),
                user_context: {
                    location: null  // Can be populated with geolocation if available
                }
            };

            log(`📤 Sending text message via STT WebSocket: ${text.substring(0, 50)}...`);
            state.sttWs.send(JSON.stringify(payload));
        }

        // =================================================================
        // Unified WebSocket (for both text chat and audio streaming)
        // =================================================================
        function connectSTTWebSocket() {
            return new Promise((resolve, reject) => {
                // Connect to unified WebSocket endpoint with thread_id
                const wsUrl = `${CONFIG.wsBaseUrl}/ws/${state.threadId}?created_by=voice_demo`;
                log(`Connecting to unified WebSocket: ${wsUrl}`);

                state.sttWs = new WebSocket(wsUrl);

                state.sttWs.onopen = () => {
                    state.sttWsConnected = true;
                    log('Unified WebSocket connected');
                    resolve();
                };

                state.sttWs.onclose = (event) => {
                    state.sttWsConnected = false;
                    log(`Unified WebSocket disconnected - code: ${event.code}, reason: ${event.reason || 'none'}, wasClean: ${event.wasClean}`);
                };

                state.sttWs.onerror = (error) => {
                    log(`Unified WebSocket error: ${error}`, 'error');
                    reject(error);
                };

                state.sttWs.onmessage = (event) => {
                    handleSTTMessage(event.data);
                };
            });
        }

        function handleSTTMessage(data) {
            try {
                const message = JSON.parse(data);
                const type = message.type;

                log(`WS message: ${type}`);

                switch (type) {
                    // Audio session events (unified WebSocket)
                    case 'audio-session-started':
                        log(`Audio session started: ${message.session_id}`);
                        break;

                    case 'transcription-result':
                        // Handle transcription result from unified WebSocket
                        log(`Transcription result: ${message.text}`);
                        state.transcriptFinal = message.text || '';
                        state.transcriptInterim = '';
                        updateTranscriptUI();

                        // Hide transcript overlay after a delay
                        setTimeout(() => {
                            elements.liveTranscript.classList.remove('visible');
                        }, 500);
                        break;

                    case 'transcription-error':
                        log(`Transcription error: ${message.error}`, 'error');
                        break;

                    case 'transcription-start':
                        state.transcriptFinal = '';
                        state.transcriptInterim = '';
                        updateTranscriptUI();
                        break;

                    case 'transcription-chunk':
                        if (message.is_final) {
                            state.transcriptFinal += message.text + ' ';
                            state.transcriptInterim = '';
                        } else {
                            state.transcriptInterim = message.text;
                        }
                        updateTranscriptUI();
                        break;

                    case 'transcription-end':
                        state.transcriptFinal = message.full_text || state.transcriptFinal;
                        state.transcriptInterim = '';
                        updateTranscriptUI();

                        // Send the transcribed text to the agent
                        if (state.transcriptFinal.trim()) {
                            sendMessage(state.transcriptFinal.trim());
                        }

                        // Hide transcript overlay
                        setTimeout(() => {
                            elements.liveTranscript.classList.remove('visible');
                        }, 500);
                        break;

                    case 'transcription-error':
                        log(`STT Error: ${message.error}`, 'error');
                        break;

                    // Text stream events (new frontend contract schema)
                    case 'text-stream-start':
                        log(`Text stream starting: ${message.message_id}`);
                        removeTypingIndicator();
                        hideThoughtIndicator();
                        state.currentAgentText = '';
                        state.agentMessageElement = addMessage('', false, true);
                        state.currentMessageId = message.message_id;
                        break;

                    case 'text-stream-delta':
                        if (state.agentMessageElement && message.text) {
                            state.currentAgentText += message.text;
                            state.agentMessageElement.textContent = state.currentAgentText;
                            scrollToBottom();
                        }
                        break;

                    case 'text-stream-end':
                        log(`Text stream complete: ${state.currentAgentText.length} chars`);
                        state.agentMessageElement = null;
                        state.currentMessageId = null;
                        break;

                    // Agent response events (deprecated - kept for backward compat)
                    case 'agent-response-start':
                        log(`Agent response starting: ${message.message_id}`);
                        state.currentResponse = '';
                        state.currentMessageId = message.message_id;
                        // Remove typing indicator when response starts
                        removeTypingIndicator();
                        break;

                    case 'audio-response':
                        // Play TTS audio for agent response
                        log(`🔊 Audio response received: ${message.audio_data ? message.audio_data.length : 0} chars (base64)`);
                        if (message.audio_data) {
                            try {
                                // Convert base64 to blob and play
                                const audioBytes = atob(message.audio_data);
                                log(`🔊 Decoded audio: ${audioBytes.length} bytes`);

                                const audioArray = new Uint8Array(audioBytes.length);
                                for (let i = 0; i < audioBytes.length; i++) {
                                    audioArray[i] = audioBytes.charCodeAt(i);
                                }
                                const audioBlob = new Blob([audioArray], { type: 'audio/mpeg' });
                                const audioUrl = URL.createObjectURL(audioBlob);

                                log(`🔊 Audio blob created: ${audioBlob.size} bytes, URL: ${audioUrl}`);

                                // Check if playback is allowed (not recording)
                                if (state.isRecording) {
                                    log('🔇 Deferring audio playback (recording in progress)');
                                    state.pendingAudioUrl = audioUrl;
                                    break;
                                }

                                // Temporarily pause wake word listener to avoid mic/audio conflicts in Safari
                                const wasListening = state.wakeWordListening;
                                if (wasListening) {
                                    log('🔇 Pausing wake word listener for audio playback');
                                    stopWakeWordListener();
                                }

                                // Play the audio with proper Promise handling
                                elements.audioPlayer.src = audioUrl;
                                elements.audioPlayer.volume = 1.0;

                                const playPromise = elements.audioPlayer.play();
                                if (playPromise !== undefined) {
                                    playPromise.then(() => {
                                        log(`🔊 TTS audio playing successfully`);
                                    }).catch(playError => {
                                        log(`⚠️ Autoplay blocked: ${playError}. Click anywhere to enable audio.`, 'warn');
                                        // Store the URL to play on next user interaction
                                        state.pendingAudioUrl = audioUrl;
                                        // Resume wake word listener if it was paused
                                        if (wasListening && CONFIG.wakeWordEnabled) {
                                            setTimeout(() => resumeWakeWordListener(), 500);
                                        }
                                    });
                                }

                                // Resume wake word listener when audio ends
                                if (wasListening && CONFIG.wakeWordEnabled) {
                                    elements.audioPlayer.onended = () => {
                                        log('🔊 Audio playback ended, resuming wake word listener');
                                        setTimeout(() => resumeWakeWordListener(), 500);
                                    };
                                }
                            } catch (audioError) {
                                log(`❌ Failed to process audio: ${audioError}`, 'error');
                                console.error('Audio error:', audioError);
                            }
                        }
                        break;

                    case 'agent-response-chunk':
                        state.currentResponse += message.text;
                        // Update the current agent message bubble with streaming text
                        updateAgentMessage(state.currentMessageId, state.currentResponse);
                        break;

                    case 'agent-response-end':
                        log(`Agent response complete: ${message.full_text.substring(0, 50)}...`);
                        // Finalize the message
                        removeTypingIndicator();
                        if (!state.currentMessageId) {
                            // If we didn't get a start event, add the message directly
                            addMessage(message.full_text, false);
                        }
                        state.currentResponse = '';
                        state.currentMessageId = null;
                        break;

                    case 'agent-response-error':
                        log(`Agent error: ${message.error}`, 'error');
                        removeTypingIndicator();
                        hideThoughtIndicator();
                        addMessage(`Error: ${message.error}`, false);
                        break;

                    // Thought stream events (chain-of-thought feedback)
                    case 'thought-stream-start':
                        log(`🧠 Thought stream started: ${message.thought_id}`);
                        showThoughtIndicator(message.thought || 'Processing...');
                        break;

                    case 'thought-stream-delta':
                        log(`🧠 Thinking: ${message.thought}`);
                        updateThoughtIndicator(message.thought);
                        break;

                    case 'thought-stream-end':
                        log(`🧠 Thought stream ended`);
                        hideThoughtIndicator();
                        break;

                    case 'tool-call-start':
                        log(`Tool call: ${message.tool_name}`);
                        if (message.thought) {
                            updateThoughtIndicator(message.thought);
                        }
                        break;

                    case 'tool-call-end':
                        log(`Tool complete: ${message.tool_name}`);
                        break;

                    default:
                        log(`Unhandled STT/Chat message type: ${type}`);
                }
            } catch (e) {
                log(`Failed to parse STT message: ${e}`, 'error');
            }
        }

        function updateTranscriptUI() {
            elements.transcriptFinal.textContent = state.transcriptFinal;
            elements.transcriptInterim.textContent = state.transcriptInterim;
            elements.liveTranscript.classList.add('visible');
        }

        // =================================================================
        // Audio Recording
        // =================================================================
        async function startRecording() {
            try {
                // Phase 2: Stop all audio playback during recording
                state.allowPlayback = false;
                state.audioQueue = [];
                state.isPlayingAudio = false;
                if (elements.audioPlayer) {
                    elements.audioPlayer.pause();
                    elements.audioPlayer.currentTime = 0;
                    log('🔇 Paused audio playback for recording');
                }

                // Phase 4: Stop wake word listener while recording
                if (state.wakeWordListening) {
                    stopWakeWordListener();
                }

                // Connect STT WebSocket if not connected
                if (!state.sttWsConnected) {
                    await connectSTTWebSocket();
                }

                // Request microphone access
                state.audioStream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        sampleRate: CONFIG.sampleRate,
                        channelCount: 1,
                        echoCancellation: true,
                        noiseSuppression: true
                    }
                });

                // Create AudioContext for processing
                state.audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: CONFIG.sampleRate
                });

                // Phase 3: Set up analyser for silence detection
                state.audioSource = state.audioContext.createMediaStreamSource(state.audioStream);
                state.audioAnalyser = state.audioContext.createAnalyser();
                state.audioAnalyser.fftSize = 2048;
                state.audioSource.connect(state.audioAnalyser);
                startSilenceMonitor();

                // Generate session ID
                state.sttSessionId = generateUUID();

                // Create MediaRecorder with appropriate format
                // Note: Most browsers support webm with opus codec
                const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
                    ? 'audio/webm;codecs=opus' 
                    : MediaRecorder.isTypeSupported('audio/webm')
                    ? 'audio/webm'
                    : 'audio/mp4';

                // Determine encoding format for backend
                const encoding = mimeType.includes('webm') ? 'webm' : 'mp4';

                log(`========== STARTING RECORDING ==========`);
                log(`Session ID: ${state.sttSessionId}`);
                log(`MediaRecorder mimeType: ${mimeType}`);
                log(`Backend encoding: ${encoding}`);
                log(`Sample rate: ${CONFIG.sampleRate}`);
                log(`Language: ${CONFIG.language}`);

                // Send audio-input-start with correct encoding
                const startMsg = {
                    type: 'audio-input-start',
                    session_id: state.sttSessionId,
                    sample_rate: CONFIG.sampleRate,
                    encoding: encoding,
                    language: CONFIG.language
                };
                log(`Sending audio-input-start: ${JSON.stringify(startMsg)}`);
                state.sttWs.send(JSON.stringify(startMsg));

                state.mediaRecorder = new MediaRecorder(state.audioStream, {
                    mimeType: mimeType
                });

                // Accumulate all audio chunks into a single blob
                // WebM chunks from MediaRecorder with timeslice are NOT independently valid!
                // We must collect all chunks and send as ONE complete file
                const audioChunks = [];

                state.mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                        log(`Accumulated chunk: ${event.data.size} bytes (total chunks: ${audioChunks.length})`);
                    }
                };

                state.mediaRecorder.onstop = async () => {
                    log(`========== MEDIARECORDER STOPPED ==========`);
                    log(`Total chunks accumulated: ${audioChunks.length}`);

                    if (audioChunks.length === 0) {
                        log('No audio chunks recorded!', 'error');
                        return;
                    }

                    // Combine all chunks into a single blob
                    const completeBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    log(`Complete audio blob: ${completeBlob.size} bytes, type: ${completeBlob.type}`);

                    // Send WebM blob directly to transcription endpoint
                    log(`📤 Sending ${completeBlob.size} bytes WebM to /speech/transcription...`);

                    try {
                        const response = await fetch(`${CONFIG.apiBaseUrl}/speech/transcription`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'audio/webm'
                            },
                            body: completeBlob
                        });

                        log(`📥 Response received: ${response.status}`);

                        if (!response.ok) {
                            const errorText = await response.text();
                            throw new Error(`HTTP ${response.status}: ${errorText}`);
                        }

                        let result;
                        try {
                            result = await response.json();
                            log(`✅ Transcription result: ${JSON.stringify(result)}`);
                        } catch (parseError) {
                            log(`❌ Failed to parse response as JSON: ${parseError}`, 'error');
                            const textResult = await response.text();
                            log(`Raw response text: ${textResult}`);
                            result = { text: textResult };
                        }

                        // Get transcript text - handle various response formats
                        const transcript = result.text || result.transcript || result.transcription || 
                                          (typeof result === 'string' ? result : '');
                        log(`📝 Extracted transcript: "${transcript}"`);

                        // Debug: Log WebSocket state
                        log(`📡 STT WebSocket state check:`);
                        log(`   - state.sttWsConnected: ${state.sttWsConnected}`);
                        log(`   - state.sttWs exists: ${!!state.sttWs}`);
                        if (state.sttWs) {
                            log(`   - state.sttWs.readyState: ${state.sttWs.readyState} (0=CONNECTING, 1=OPEN, 2=CLOSING, 3=CLOSED)`);
                        }
                        log(`   - state.sttSessionId: ${state.sttSessionId}`);

                        // Send transcription-result via WebSocket to complete the streaming UX
                        // This triggers the backend to echo back transcription-chunk and transcription-end events
                        // Use readyState check (1 = OPEN) instead of our flag which may be stale
                        const wsIsOpen = state.sttWs && state.sttWs.readyState === WebSocket.OPEN;
                        log(`📡 WebSocket is open: ${wsIsOpen}`);

                        if (wsIsOpen) {
                            const resultMsg = {
                                type: 'transcription-result',
                                session_id: state.sttSessionId,
                                text: transcript,
                                success: !!transcript.trim()
                            };
                            log(`📡 Sending transcription-result via WebSocket: ${JSON.stringify(resultMsg)}`);
                            try {
                                state.sttWs.send(JSON.stringify(resultMsg));
                                log(`📡 transcription-result SENT successfully`);
                            } catch (sendError) {
                                log(`❌ Failed to send via WebSocket: ${sendError}`, 'error');
                                // Fall through to fallback
                            }
                        }

                        // ALWAYS do fallback for now to ensure UX works regardless of WebSocket state
                        // The WebSocket handler will also send to agent, but sendMessage is idempotent for UI
                        if (transcript.trim()) {
                            log(`📝 Fallback: Updating UI and sending message directly`);
                            state.transcriptFinal = transcript;
                            state.transcriptInterim = '';
                            updateTranscriptUI();

                            // Only send message if WebSocket flow didn't work
                            if (!wsIsOpen) {
                                sendMessage(transcript.trim());
                            }

                            setTimeout(() => {
                                elements.liveTranscript.classList.remove('visible');
                            }, 500);
                        } else {
                            log('⚠️ Transcript is empty, nothing to send', 'warn');
                        }

                    } catch (error) {
                        log(`❌ Transcription error: ${error}`, 'error');
                        log(`❌ Error stack: ${error.stack || 'no stack'}`, 'error');
                    }
                };

                // Start recording WITHOUT timeslice - collect complete audio
                // Using timeslice creates fragmented chunks that aren't valid WebM files
                state.mediaRecorder.start();
                state.isRecording = true;
                log(`MediaRecorder started (no timeslice - will send complete audio on stop)`);

                // Update UI
                elements.micBtn.classList.add('recording');
                elements.statusDot.classList.add('recording');
                elements.statusText.textContent = 'Recording... | جاري التسجيل...';

                // Reset transcript
                state.transcriptFinal = '';
                state.transcriptInterim = '';
                elements.liveTranscript.classList.add('visible');

                log('Recording started');

            } catch (error) {
                log(`Failed to start recording: ${error}`, 'error');
                alert('Could not access microphone. Please check permissions.');
                // Reset playback flag on error
                state.allowPlayback = true;
            }
        }

        function stopRecording() {
            if (!state.isRecording) return;

            log(`========== STOPPING RECORDING ==========`);
            log(`Session ID: ${state.sttSessionId}`);
            log(`MediaRecorder state: ${state.mediaRecorder ? state.mediaRecorder.state : 'null'}`);
            log(`STT WebSocket connected: ${state.sttWsConnected}`);

            // Phase 3: Stop silence monitor and clean up analyser nodes
            stopSilenceMonitor();
            if (state.audioSource) {
                try { state.audioSource.disconnect(); } catch (e) {}
                state.audioSource = null;
            }
            if (state.audioAnalyser) {
                try { state.audioAnalyser.disconnect(); } catch (e) {}
                state.audioAnalyser = null;
            }

            // Stop MediaRecorder - this triggers onstop which sends the complete audio
            if (state.mediaRecorder && state.mediaRecorder.state !== 'inactive') {
                log('Stopping MediaRecorder (will send complete audio in onstop callback)...');
                state.mediaRecorder.stop();
            }

            // Stop audio stream
            if (state.audioStream) {
                log('Stopping audio stream tracks...');
                state.audioStream.getTracks().forEach(track => track.stop());
            }

            // Close AudioContext
            if (state.audioContext) {
                log('Closing AudioContext...');
                state.audioContext.close();
            }

            // NOTE: audio-input-end is now sent in MediaRecorder.onstop callback
            // after the complete audio blob is sent as a single chunk

            state.isRecording = false;
            state.mediaRecorder = null;
            state.audioStream = null;
            state.audioContext = null;

            // Phase 2: Re-enable audio playback and resume pending audio
            state.allowPlayback = true;
            if (state.pendingAudioUrl && elements.audioPlayer) {
                log('🔊 Resuming pending audio after recording');
                elements.audioPlayer.src = state.pendingAudioUrl;
                elements.audioPlayer.play().catch(e => log(`Failed to resume audio: ${e}`, 'warn'));
                state.pendingAudioUrl = null;
            }

            // Update UI
            elements.micBtn.classList.remove('recording');
            elements.statusDot.classList.remove('recording');
            const wsConnected = state.sttWs && state.sttWs.readyState === WebSocket.OPEN;
            updateStatus(wsConnected, 'Connected | متصل');

            // Phase 4: Resume wake word listener
            if (CONFIG.wakeWordEnabled && !state.wakeWordListening) {
                setTimeout(() => resumeWakeWordListener(), 500); // Small delay to avoid overlap
            }

            log('Recording stopped, waiting for transcription...');
        }

        // =================================================================
        // Wake Word Detection (Cross-Browser using Backend STT)
        // =================================================================
        async function startWakeWordListener() {
            if (!CONFIG.wakeWordEnabled) {
                log('Wake word detection disabled in config');
                return;
            }

            // Skip if already listening or recording
            if (state.wakeWordListening || state.isRecording) {
                return;
            }

            try {
                // Request microphone access for wake word detection
                state.wakeWordStream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        sampleRate: CONFIG.sampleRate,
                        channelCount: 1,
                        echoCancellation: true,
                        noiseSuppression: true
                    }
                });

                // Create AudioContext for VAD during wake word listening
                state.wakeWordAudioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: CONFIG.sampleRate
                });

                // Set up analyser for voice activity detection
                state.wakeWordSource = state.wakeWordAudioContext.createMediaStreamSource(state.wakeWordStream);
                state.wakeWordAnalyser = state.wakeWordAudioContext.createAnalyser();
                state.wakeWordAnalyser.fftSize = 2048;
                state.wakeWordSource.connect(state.wakeWordAnalyser);

                state.wakeWordListening = true;
                state.wakeWordEnabled = true;
                log('👂 Wake word listener started (cross-browser mode)');
                elements.statusText.textContent = "قل 'ساهل' للبدء | Say 'Sahel' in Arabic";

                // Start the wake word detection loop
                startWakeWordDetectionLoop();

            } catch (error) {
                log(`Failed to start wake word listener: ${error}`, 'error');
                state.wakeWordEnabled = false;
                state.wakeWordListening = false;
            }
        }

        function startWakeWordDetectionLoop() {
            if (state.wakeWordIntervalId) {
                clearInterval(state.wakeWordIntervalId);
            }

            const bufferLength = state.wakeWordAnalyser.fftSize;
            const dataArray = new Uint8Array(bufferLength);
            const voiceThreshold = 0.03; // Slightly higher threshold to detect speech
            let speechDetectedAt = null;
            let isCapturing = false;
            let captureChunks = [];
            let captureRecorder = null;

            state.wakeWordIntervalId = setInterval(async () => {
                if (!state.wakeWordListening || state.isRecording) return;

                // Get audio level
                state.wakeWordAnalyser.getByteTimeDomainData(dataArray);
                let sumSquares = 0;
                for (let i = 0; i < bufferLength; i++) {
                    const sample = (dataArray[i] - 128) / 128;
                    sumSquares += sample * sample;
                }
                const rms = Math.sqrt(sumSquares / bufferLength);

                // Detect speech start
                if (rms > voiceThreshold && !isCapturing) {
                    speechDetectedAt = performance.now();
                    isCapturing = true;
                    captureChunks = [];

                    // Start capturing audio for wake word check
                    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') 
                        ? 'audio/webm;codecs=opus' 
                        : MediaRecorder.isTypeSupported('audio/webm')
                        ? 'audio/webm'
                        : 'audio/mp4';

                    captureRecorder = new MediaRecorder(state.wakeWordStream, { mimeType });
                    captureRecorder.ondataavailable = (e) => {
                        if (e.data.size > 0) captureChunks.push(e.data);
                    };
                    captureRecorder.start();
                    log('👂 Voice detected, capturing for wake word check...');
                }

                // Check if speech ended (silence after speech)
                if (isCapturing && rms < voiceThreshold) {
                    const speechDuration = performance.now() - speechDetectedAt;

                    // Only process if speech was between 0.5s and 3s (typical wake word duration)
                    if (speechDuration > 500 && speechDuration < 3000) {
                        isCapturing = false;

                        if (captureRecorder && captureRecorder.state === 'recording') {
                            captureRecorder.stop();

                            // Wait for data to be available
                            await new Promise(resolve => {
                                captureRecorder.onstop = resolve;
                            });

                            if (captureChunks.length > 0) {
                                const audioBlob = new Blob(captureChunks, { type: 'audio/webm' });
                                log(`👂 Checking wake word in ${audioBlob.size} bytes audio...`);

                                // Send to backend STT for wake word detection
                                try {
                                    const response = await fetch(`${CONFIG.apiBaseUrl}/speech/transcription`, {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'audio/webm' },
                                        body: audioBlob
                                    });

                                    if (response.ok) {
                                        const result = await response.json();
                                        const transcript = (result.text || result.transcript || '').trim();
                                        log(`👂 Wake word check transcript: "${transcript}"`);
                                        log(`👂 Normalized: "${normalizeArabic(transcript)}"`);

                                        // Check if transcript contains wake word (with normalization)
                                        if (containsWakeWord(transcript)) {
                                            log('✅ Wake word detected! Starting recording...');
                                            stopWakeWordListener();
                                            startRecording();
                                            return;
                                        }
                                    }
                                } catch (err) {
                                    log(`Wake word STT error: ${err}`, 'warn');
                                }
                            }
                        }
                        captureRecorder = null;
                        captureChunks = [];
                    } else if (speechDuration >= 3000) {
                        // Too long, reset capture
                        isCapturing = false;
                        if (captureRecorder && captureRecorder.state === 'recording') {
                            captureRecorder.stop();
                        }
                        captureRecorder = null;
                        captureChunks = [];
                    }
                }
            }, 100); // Check every 100ms
        }

        function stopWakeWordListener() {
            // Stop the detection loop
            if (state.wakeWordIntervalId) {
                clearInterval(state.wakeWordIntervalId);
                state.wakeWordIntervalId = null;
            }

            // Disconnect audio nodes
            if (state.wakeWordSource) {
                try { state.wakeWordSource.disconnect(); } catch (e) {}
                state.wakeWordSource = null;
            }
            if (state.wakeWordAnalyser) {
                try { state.wakeWordAnalyser.disconnect(); } catch (e) {}
                state.wakeWordAnalyser = null;
            }

            // Close audio context
            if (state.wakeWordAudioContext) {
                try { state.wakeWordAudioContext.close(); } catch (e) {}
                state.wakeWordAudioContext = null;
            }

            // Stop microphone stream
            if (state.wakeWordStream) {
                state.wakeWordStream.getTracks().forEach(track => track.stop());
                state.wakeWordStream = null;
            }

            state.wakeWordListening = false;
            log('👂 Wake word listener stopped');
        }

        function resumeWakeWordListener() {
            if (CONFIG.wakeWordEnabled && !state.wakeWordListening && !state.isRecording) {
                log('👂 Resuming wake word listener...');
                startWakeWordListener();
            }
        }

        // =================================================================
        // Silence Detection (VAD)
        // =================================================================
        function startSilenceMonitor() {
            if (!state.audioAnalyser) return;

            const bufferLength = state.audioAnalyser.fftSize;
            const dataArray = new Uint8Array(bufferLength);
            const silenceThreshold = CONFIG.silenceThresholdRMS;
            const silenceDurationMs = CONFIG.silenceDurationMs;

            state.silenceStartedAt = null;
            stopSilenceMonitor(); // Clear any existing monitor

            state.silenceIntervalId = setInterval(() => {
                if (!state.isRecording) return;

                // Get time domain data for RMS calculation
                state.audioAnalyser.getByteTimeDomainData(dataArray);

                // Calculate RMS (Root Mean Square) for volume level
                let sumSquares = 0;
                for (let i = 0; i < bufferLength; i++) {
                    const sample = (dataArray[i] - 128) / 128; // Normalize to [-1, 1]
                    sumSquares += sample * sample;
                }
                const rms = Math.sqrt(sumSquares / bufferLength);

                // Check if audio level is below silence threshold
                if (rms < silenceThreshold) {
                    if (!state.silenceStartedAt) {
                        state.silenceStartedAt = performance.now();
                        log(`🔇 Silence detected (RMS: ${rms.toFixed(4)})`);
                    } else {
                        const silenceDuration = performance.now() - state.silenceStartedAt;
                        if (silenceDuration >= silenceDurationMs) {
                            log(`⏹️ Auto-stopping after ${(silenceDuration/1000).toFixed(1)}s of silence`);
                            stopRecording();
                        }
                    }
                } else {
                    // Reset silence timer when sound is detected
                    if (state.silenceStartedAt) {
                        log(`🔊 Sound detected, silence timer reset (RMS: ${rms.toFixed(4)})`);
                    }
                    state.silenceStartedAt = null;
                }
            }, 200); // Check every 200ms

            log('👂 Silence monitor started');
        }

        function stopSilenceMonitor() {
            if (state.silenceIntervalId) {
                clearInterval(state.silenceIntervalId);
                state.silenceIntervalId = null;
                log('👂 Silence monitor stopped');
            }
            state.silenceStartedAt = null;
        }

        // =================================================================
        // TTS (Text-to-Speech)
        // =================================================================
        async function generateTTS(text) {
            try {
                log(`Generating TTS for ${text.length} characters`);

                const response = await fetch(`${CONFIG.apiBaseUrl}/tts/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        text: text,
                        voice: CONFIG.ttsVoice,
                        instructions: CONFIG.language === 'ar-KW' 
                            ? 'Speak with a clear Kuwaiti (Khaliji) accent. Use the intonation of a native speaker from Kuwait.'
                            : 'Speak clearly and naturally with a friendly, professional tone.'
                    })
                });

                if (!response.ok) {
                    throw new Error(`TTS API error: ${response.status}`);
                }

                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);

                // Check if playback is allowed (not recording)
                if (state.isRecording) {
                    log('🔇 Deferring TTS playback (recording in progress)');
                    state.pendingAudioUrl = audioUrl;
                } else {
                    // Temporarily pause wake word listener to avoid mic/audio conflicts in Safari
                    const wasListening = state.wakeWordListening;
                    if (wasListening) {
                        log('🔇 Pausing wake word listener for TTS playback');
                        stopWakeWordListener();
                    }

                    // Play audio
                    elements.audioPlayer.src = audioUrl;
                    elements.audioPlayer.play();
                    log('TTS audio playing');

                    // Resume wake word listener when audio ends
                    if (wasListening && CONFIG.wakeWordEnabled) {
                        elements.audioPlayer.onended = () => {
                            log('🔊 TTS playback ended, resuming wake word listener');
                            setTimeout(() => resumeWakeWordListener(), 500);
                        };
                    }
                }

            } catch (error) {
                log(`TTS error: ${error}`, 'error');
            }
        }

        function queueAudioChunk(base64Data) {
            // Skip audio queueing if recording
            if (state.isRecording) {
                log('🔇 Dropping audio chunk (recording in progress)');
                return;
            }

            // Decode base64 to audio bytes
            const audioBytes = atob(base64Data);
            state.audioQueue.push(audioBytes);

            if (!state.isPlayingAudio) {
                playNextAudioChunk();
            }
        }

        function playNextAudioChunk() {
            // Placeholder for streaming audio playback
            // In production, would use Web Audio API for streaming
            if (state.audioQueue.length === 0) {
                state.isPlayingAudio = false;
                return;
            }

            state.isPlayingAudio = true;
            // Process queue...
        }

        // =================================================================
        // Event Handlers
        // =================================================================
        function setupEventListeners() {
            // Send button
            elements.sendBtn.addEventListener('click', () => {
                sendMessage(elements.textInput.value);
            });

            // Text input - check STT WebSocket since we use it for chat now
            elements.textInput.addEventListener('input', () => {
                const wsConnected = state.sttWs && state.sttWs.readyState === WebSocket.OPEN;
                elements.sendBtn.disabled = !elements.textInput.value.trim() || !wsConnected;
            });

            elements.textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const wsConnected = state.sttWs && state.sttWs.readyState === WebSocket.OPEN;
                    if (elements.textInput.value.trim() && wsConnected) {
                        sendMessage(elements.textInput.value);
                    }
                }
            });

            // Microphone button (click to toggle)
            elements.micBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (state.isRecording) {
                    stopRecording();
                } else {
                    startRecording();
                }
            });

            // Touch support for mobile (tap to toggle)
            elements.micBtn.addEventListener('touchend', (e) => {
                e.preventDefault();
                if (state.isRecording) {
                    stopRecording();
                } else {
                    startRecording();
                }
            });

            // Language toggle
            elements.langBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    elements.langBtns.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    CONFIG.language = btn.dataset.lang;
                    log(`Language changed to: ${CONFIG.language}`);

                    // Update placeholder
                    elements.textInput.placeholder = CONFIG.language === 'ar-KW' 
                        ? 'اكتب رسالتك هنا...'
                        : 'Type your message...';
                });
            });

            // Debug panel toggle (Ctrl+D)
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'd') {
                    e.preventDefault();
                    elements.debugPanel.classList.toggle('visible');
                }
            });

            // Handle pending audio playback on user interaction (for autoplay blocked)
            document.addEventListener('click', () => {
                if (state.pendingAudioUrl) {
                    log('🔊 Playing pending audio after user interaction...');
                    elements.audioPlayer.src = state.pendingAudioUrl;
                    elements.audioPlayer.play().then(() => {
                        log('🔊 Pending audio now playing');
                        state.pendingAudioUrl = null;
                    }).catch(e => {
                        log(`❌ Still failed to play: ${e}`, 'error');
                    });
                }
            }, { once: false });

            // Also try to unlock audio on first interaction
            const unlockAudio = () => {
                elements.audioPlayer.play().then(() => {
                    elements.audioPlayer.pause();
                    elements.audioPlayer.currentTime = 0;
                    log('🔊 Audio context unlocked');
                }).catch(() => {});
                document.removeEventListener('click', unlockAudio);
                document.removeEventListener('touchstart', unlockAudio);
            };
            document.addEventListener('click', unlockAudio);
            document.addEventListener('touchstart', unlockAudio);
        }

        // =================================================================
        // Initialization
        // =================================================================
        async function init() {
            log('Initializing PACI Voice Demo...');
            setupEventListeners();

            // Setup audio player event listeners for debugging
            elements.audioPlayer.addEventListener('play', () => log('🔊 Audio: play event'));
            elements.audioPlayer.addEventListener('playing', () => log('🔊 Audio: playing event'));
            elements.audioPlayer.addEventListener('pause', () => log('🔊 Audio: pause event'));
            elements.audioPlayer.addEventListener('ended', () => log('🔊 Audio: ended event'));
            elements.audioPlayer.addEventListener('error', (e) => {
                log(`❌ Audio error: ${elements.audioPlayer.error?.message || 'unknown'}`, 'error');
                console.error('Audio element error:', elements.audioPlayer.error);
            });
            elements.audioPlayer.addEventListener('canplay', () => log('🔊 Audio: canplay event'));
            elements.audioPlayer.addEventListener('loadeddata', () => log('🔊 Audio: loadeddata event'));

            // Connect unified WebSocket (used for both text chat and audio)
            try {
                await connectSTTWebSocket();
                log('Unified WebSocket connected');
                updateStatus(true, 'Connected | متصل');
                elements.sendBtn.disabled = false;
            } catch (e) {
                log(`Failed to connect unified WebSocket: ${e}`, 'error');
                updateStatus(false, 'Disconnected | غير متصل');
            }

            // Phase 4: Start wake word listener after connection
            if (CONFIG.wakeWordEnabled) {
                setTimeout(() => startWakeWordListener(), 500);
            }

            // Optionally still connect the original chat WebSocket (for backwards compatibility)
            // connectChatWebSocket();

            log('Initialization complete');
        }

        // Start when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }

    })();
    </script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
async def get_demo_page():
    """
    Serve the Voice Chat Demo UI.

    Access at /spa to test the voice interaction experience:
    - Click microphone button to start/stop recording (toggle behavior)
    - Say "Ya Sahel" (يا ساهل) to auto-trigger recording (wake-word)
    - Recording auto-stops after 2 seconds of silence
    - Audio playback pauses during recording
    - See real-time transcription as you speak
    - View agent responses streaming in
    - Hear TTS audio of agent responses
    - Supports Arabic (Kuwaiti dialect) and English

    Press Ctrl+D to toggle debug panel.

    Browser compatibility:
    - Wake-word detection requires Chrome/Edge (Web Speech API)
    - Manual recording works in all modern browsers
    """
    return HTMLResponse(content=DEMO_HTML)