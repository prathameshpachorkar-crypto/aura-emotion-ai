// ==========================================
// Emotion Polling & Dynamic UI Updates
// ==========================================
setInterval(async () => {
    if (typeof cameraEnabled !== 'undefined' && !cameraEnabled) return;
    try {
        let response = await fetch('/get_current_emotion');
        let data = await response.json();
        let emotionLabel = document.getElementById('emotion-label');
        let emotionBadge = document.getElementById('emotion-badge');
        let emotionIcon = document.getElementById('emotion-icon');
        let videoWrapper = document.getElementById('video-wrapper');
        
        let emotion = data.emotion;
        emotionLabel.innerText = emotion;
        
        // Tailwind/Hex Colors & Icons Mapping based on Emotion
        const theme = {
            "Happy":    { color: "#eab308", icon: "fa-face-smile", glow: "rgba(234, 179, 8, 0.4)" },
            "Sad":      { color: "#3b82f6", icon: "fa-face-sad-tear", glow: "rgba(59, 130, 246, 0.4)" },
            "Angry":    { color: "#ef4444", icon: "fa-face-angry", glow: "rgba(239, 68, 68, 0.4)" },
            "Fear":     { color: "#a855f7", icon: "fa-face-flushed", glow: "rgba(168, 85, 247, 0.4)" },
            "Surprise": { color: "#f97316", icon: "fa-face-surprise", glow: "rgba(249, 115, 22, 0.4)" },
            "Disgust":  { color: "#84cc16", icon: "fa-face-grin-tongue-squint", glow: "rgba(132, 204, 22, 0.4)" },
            "Neutral":  { color: "#10b981", icon: "fa-face-meh", glow: "rgba(16, 185, 129, 0.2)" }
        };

        let currentTheme = theme[emotion] || theme["Neutral"];

        // Update UI Colors
        emotionIcon.className = `fa-solid ${currentTheme.icon} text-xl`;
        emotionIcon.style.color = currentTheme.color;
        emotionLabel.style.color = currentTheme.color;
        
        // Update Video Glow Effect
        videoWrapper.style.borderColor = currentTheme.color;
        videoWrapper.style.boxShadow = `0 0 25px ${currentTheme.glow}`;

    } catch (err) {
        console.error("Error fetching emotion:", err);
    }
}, 1500);

// ==========================================
// Chat Logic & UI Formatting
// ==========================================
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

async function sendMessage() {
    let inputField = document.getElementById('user-input');
    let message = inputField.value.trim();
    if (!message) return;

    // 1. Show User Message
    appendMessage("user", message);
    inputField.value = '';

    // 2. Show Animated Typing Indicator
    let chatWindow = document.getElementById('chat-window');
    
    let typingWrapper = document.createElement('div');
    typingWrapper.id = "typing-indicator";
    typingWrapper.className = "flex flex-col space-y-2 max-w-[85%] self-start";
    
    typingWrapper.innerHTML = `
        <div class="bg-slate-800 border border-slate-700 p-2 rounded-2xl rounded-tl-none shadow-md typing-indicator">
            <div class="dot"></div><div class="dot"></div><div class="dot"></div>
        </div>
    `;
    
    chatWindow.appendChild(typingWrapper);
    scrollToBottom();

    try {
        let response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        let data = await response.json();
        
        // Remove typing indicator
        document.getElementById("typing-indicator").remove();
        
        // 3. Append bot reply
        appendMessage("bot", data.response);
        speakText(data.response);
        
    } catch (err) {
        document.getElementById("typing-indicator").remove();
        appendMessage("bot", "**Error:** Could not connect to the server.");
    }
}

function appendMessage(sender, text) {
    let chatWindow = document.getElementById('chat-window');
    let msgWrapper = document.createElement('div');
    
    // Applying Tailwind Classes dynamically based on sender
    if (sender === "user") {
        msgWrapper.className = "flex flex-col space-y-2 max-w-[85%] self-end";
        msgWrapper.innerHTML = `
            <div class="bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-4 rounded-2xl rounded-tr-none shadow-md shadow-indigo-500/20 text-sm md:text-base">
                ${text}
            </div>
        `;
    } else {
        msgWrapper.className = "flex flex-col space-y-2 max-w-[85%] self-start";
        let parsedHTML = marked.parse(text); // Convert Markdown to HTML
        msgWrapper.innerHTML = `
            <div class="bg-slate-800 border border-slate-700 text-slate-200 p-4 rounded-2xl rounded-tl-none shadow-md text-sm md:text-base markdown-body">
                ${parsedHTML}
            </div>
        `;
    }
    
    chatWindow.appendChild(msgWrapper);
    scrollToBottom();
}

function scrollToBottom() {
    let chatWindow = document.getElementById('chat-window');
    chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: 'smooth' });
}

// ==========================================
// Text-to-Speech (Voice) Logic
// ==========================================
let voiceEnabled = true;

function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    let icon = document.getElementById("voice-icon");
    let text = document.getElementById("voice-text");
    
    if (voiceEnabled) {
        icon.className = "fa-solid fa-volume-high text-emerald-400";
        text.innerText = "Voice On";
    } else {
        icon.className = "fa-solid fa-volume-xmark text-red-400";
        text.innerText = "Voice Off";
        window.speechSynthesis.cancel();
    }
}

function speakText(text) {
    if (!voiceEnabled) return;
    window.speechSynthesis.cancel();
    let cleanText = text.replace(/[*_#`~]/g, '');
    let speech = new SpeechSynthesisUtterance(cleanText);
    let currentEmotion = document.getElementById('emotion-label').innerText;

    speech.pitch = 1.0; 
    speech.rate = 1.0;  

    if (currentEmotion === "Sad") {
        speech.pitch = 0.8; speech.rate = 0.85;
    } else if (currentEmotion === "Happy") {
        speech.pitch = 1.2; speech.rate = 1.1;
    } else if (currentEmotion === "Angry") {
        speech.pitch = 0.9; speech.rate = 0.9;
    } else if (currentEmotion === "Fear") {
        speech.pitch = 1.0; speech.rate = 0.9;
    }

    window.speechSynthesis.speak(speech);
}

// ==========================================
// Emotion Suggestion Button Logic
// ==========================================
function requestEmotionSuggestion() {
    let currentEmotion = document.getElementById('emotion-label').innerText;
    if (currentEmotion === "Loading..." || currentEmotion === "Camera Off") {
        appendMessage("bot", "Please wait until an emotion is detected or ensure the camera is on.");
        return;
    }
    
    let suggestionMessage = `I'm currently feeling ${currentEmotion}. Can you give me some advice or a suggestion based on this?`;
    
    let inputField = document.getElementById('user-input');
    inputField.value = suggestionMessage;
    sendMessage();
}

// ==========================================
// Camera Toggle Logic
// ==========================================
let cameraEnabled = true;

async function toggleCamera() {
    cameraEnabled = !cameraEnabled;
    let icon = document.getElementById("camera-icon");
    let videoStream = document.getElementById("video-stream");
    let emotionLabel = document.getElementById('emotion-label');
    let emotionIcon = document.getElementById('emotion-icon');
    let videoWrapper = document.getElementById('video-wrapper');
    
    try {
        await fetch('/toggle_camera', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state: cameraEnabled })
        });
        
        if (cameraEnabled) {
            icon.className = "fa-solid fa-video text-emerald-400";
            videoStream.style.display = "block";
            // Force browser to reconnect to the stream
            videoStream.src = "/webcam_stream?" + new Date().getTime(); 
            emotionLabel.innerText = "Loading...";
        } else {
            icon.className = "fa-solid fa-video-slash text-red-400";
            videoStream.style.display = "none";
            
            // Set UI to offline state
            emotionLabel.innerText = "Camera Off";
            emotionIcon.className = "fa-solid fa-power-off text-xl";
            emotionIcon.style.color = "#64748b"; // slate-500
            emotionLabel.style.color = "#64748b";
            videoWrapper.style.borderColor = "#334155"; // slate-700
            videoWrapper.style.boxShadow = "none";
        }
    } catch (err) {
        console.error("Error toggling camera:", err);
        // Revert state if failed
        cameraEnabled = !cameraEnabled;
    }
}