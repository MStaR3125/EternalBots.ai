/* ═══════════════════════════════════════════════════════════
   EternalBots.ai — Main Application Logic
   ═══════════════════════════════════════════════════════════ */

const API = "http://localhost:8000";
let currentPersonaId = null;
let currentPersona = null;
let isRecording = false;
let recognition = null;
let audioPlayer = null;
let waveformCtx = null;
let waveformAnimId = null;

// ─── Initialization ───────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    audioPlayer = document.getElementById("audio-player");
    initWaveform();
    loadPersonas();
});

// ─── View Navigation ─────────────────────────────────────
window.showView = function (viewId) {
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    const view = document.getElementById(viewId);
    if (view) view.classList.add("active");

    if (viewId === "landing-view") loadPersonas();
};

// ─── Personas ─────────────────────────────────────────────
async function loadPersonas() {
    try {
        const res = await fetch(`${API}/api/personas`);
        const personas = await res.json();
        renderPersonaGrid(personas);
    } catch (e) {
        console.error("Failed to load personas:", e);
    }
}

function renderPersonaGrid(personas) {
    const grid = document.getElementById("personas-grid");
    if (!personas.length) {
        grid.innerHTML = `<p style="color: var(--text-muted); text-align: center; grid-column: 1/-1;">
            No memories yet. Create your first one below.</p>`;
        return;
    }

    grid.innerHTML = personas
        .map((p) => {
            const photoHtml = p.photo_path
                ? `<img class="persona-card-photo" src="${API}/uploads/${p.id}/${p.photo_path.split(/[\\/]/).pop()}" alt="${p.name}">`
                : `<div class="persona-card-placeholder">${p.name[0]}</div>`;

            return `
            <div class="persona-card" onclick="openPersona(${p.id})">
                ${photoHtml}
                <div class="persona-card-name">${p.name}</div>
                <div class="persona-card-desc">${p.relationship || p.description || "Click to chat"}</div>
            </div>`;
        })
        .join("");
}

window.openPersona = async function (id) {
    currentPersonaId = id;

    try {
        const res = await fetch(`${API}/api/persona/${id}`);
        currentPersona = await res.json();

        // Check if persona has any uploaded data
        if (!currentPersona.facts?.length && !currentPersona.files?.length) {
            // Go to upload view first
            document.getElementById("upload-persona-name").textContent =
                `Upload data about ${currentPersona.name}`;
            showView("upload-view");
        } else {
            enterChat();
        }
    } catch (e) {
        console.error("Failed to load persona:", e);
    }
};

// ─── Create Persona ──────────────────────────────────────
window.handleCreatePersona = async function (e) {
    e.preventDefault();

    const name = document.getElementById("persona-name").value.trim();
    const relationship = document.getElementById("persona-relationship").value.trim();
    const description = document.getElementById("persona-description").value.trim();
    const voice = document.getElementById("persona-voice").value;

    if (!name) return;

    const btn = document.getElementById("btn-create-submit");
    btn.innerHTML = '<span class="spinner"></span> Creating...';
    btn.disabled = true;

    try {
        const res = await fetch(`${API}/api/persona`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, relationship, description, voice_id: voice }),
        });
        const data = await res.json();
        currentPersonaId = data.id;

        // Fetch the full persona
        const pRes = await fetch(`${API}/api/persona/${data.id}`);
        currentPersona = await pRes.json();

        // Go to upload view
        document.getElementById("upload-persona-name").textContent =
            `Upload data about ${name}`;
        showView("upload-view");

        // Reset form
        document.getElementById("create-form").reset();
    } catch (e) {
        console.error("Failed to create persona:", e);
        alert("Failed to create persona. Is the backend running?");
    } finally {
        btn.innerHTML = "Create Memory ✦";
        btn.disabled = false;
    }
};

// ─── File Upload ─────────────────────────────────────────
window.handleDrop = async function (e) {
    e.preventDefault();
    e.currentTarget.classList.remove("drag-over");
    const files = Array.from(e.dataTransfer.files);
    await uploadFiles(files);
};

window.handleFileSelect = async function (e) {
    const files = Array.from(e.target.files);
    await uploadFiles(files);
    e.target.value = "";
};

async function uploadFiles(files) {
    const progress = document.getElementById("upload-progress");
    progress.style.display = "flex";

    for (const file of files) {
        const typeIcon = getFileIcon(file.type);
        const itemHtml = `<div class="upload-item" id="upload-${file.name.replace(/\W/g, '_')}">
            <span class="upload-item-icon">${typeIcon}</span>
            <span class="upload-item-name">${file.name}</span>
            <span class="upload-item-status"><span class="spinner"></span></span>
        </div>`;
        progress.innerHTML += itemHtml;

        try {
            const formData = new FormData();
            formData.append("file", file);

            await fetch(`${API}/api/persona/${currentPersonaId}/upload`, {
                method: "POST",
                body: formData,
            });

            const item = document.getElementById(`upload-${file.name.replace(/\W/g, '_')}`);
            if (item) {
                item.querySelector(".upload-item-status").textContent = "✅ Done";
            }
        } catch (e) {
            console.error(`Failed to upload ${file.name}:`, e);
            const item = document.getElementById(`upload-${file.name.replace(/\W/g, '_')}`);
            if (item) {
                item.querySelector(".upload-item-status").textContent = "❌ Failed";
            }
        }
    }

    // Refresh persona data
    const pRes = await fetch(`${API}/api/persona/${currentPersonaId}`);
    currentPersona = await pRes.json();
}

function getFileIcon(mimeType) {
    if (mimeType.startsWith("image/")) return "📸";
    if (mimeType.startsWith("audio/")) return "🎵";
    if (mimeType.startsWith("text/") || mimeType.includes("document")) return "📝";
    return "📎";
}

window.addManualFact = async function () {
    const input = document.getElementById("manual-fact");
    const fact = input.value.trim();
    if (!fact) return;

    try {
        const formData = new FormData();
        formData.append("fact_text", fact);

        await fetch(`${API}/api/persona/${currentPersonaId}/facts`, {
            method: "POST",
            body: formData,
        });

        input.value = "";

        // Show confirmation
        const progress = document.getElementById("upload-progress");
        progress.style.display = "flex";
        progress.innerHTML += `<div class="upload-item">
            <span class="upload-item-icon">💡</span>
            <span class="upload-item-name">${fact}</span>
            <span class="upload-item-status">✅ Added</span>
        </div>`;

        // Refresh persona
        const pRes = await fetch(`${API}/api/persona/${currentPersonaId}`);
        currentPersona = await pRes.json();
    } catch (e) {
        console.error("Failed to add fact:", e);
    }
};

window.startChatting = function () {
    enterChat();
};

// ─── Chat ─────────────────────────────────────────────────
function enterChat() {
    showView("chat-view");

    // Set avatar
    const avatarImg = document.getElementById("avatar-img");
    if (currentPersona.photo_url) {
        avatarImg.src = `${API}${currentPersona.photo_url}`;
        avatarImg.classList.add("loaded");
    } else {
        avatarImg.classList.remove("loaded");
    }

    document.getElementById("avatar-name").textContent = currentPersona.name;
    document.getElementById("facts-count").textContent = currentPersona.facts?.length || 0;
    document.getElementById("traits-count").textContent = currentPersona.traits?.length || 0;

    // Update welcome text
    const welcome = document.getElementById("chat-welcome");
    if (welcome) {
        welcome.querySelector(".welcome-text").textContent =
            `Start talking with ${currentPersona.name}`;
        welcome.querySelector(".welcome-hint").textContent =
            "They're trying to remember... help them piece together who they are.";
    }

    // Focus chat input
    document.getElementById("chat-input").focus();
}

window.sendMessage = async function () {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message || !currentPersonaId) return;

    input.value = "";

    // Remove welcome message
    const welcome = document.getElementById("chat-welcome");
    if (welcome) welcome.remove();

    // Add user bubble
    addChatBubble(message, "user");

    // Show typing indicator
    const typingEl = addTypingIndicator();

    // Set avatar to "thinking"
    document.getElementById("status-text").textContent = "Thinking...";

    try {
        // Send to backend
        const res = await fetch(`${API}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ persona_id: currentPersonaId, message }),
        });
        const data = await res.json();

        // Remove typing indicator
        typingEl.remove();

        // Add assistant bubble
        addChatBubble(data.reply, "assistant");

        // Show learned traits
        if (data.new_traits_learned?.length) {
            data.new_traits_learned.forEach((trait) => {
                addTraitNotification(trait);
            });
            // Update trait count
            const traitsEl = document.getElementById("traits-count");
            traitsEl.textContent = parseInt(traitsEl.textContent) + data.new_traits_learned.length;
        }

        // Generate and play TTS
        await playTTS(data.reply);
    } catch (e) {
        console.error("Chat error:", e);
        typingEl.remove();
        addChatBubble("Sorry, I couldn't respond. Please check if the backend is running.", "assistant");
    }

    document.getElementById("status-text").textContent = "Online";
};

function addChatBubble(text, role) {
    const messages = document.getElementById("chat-messages");
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${role}`;
    bubble.textContent = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
}

function addTypingIndicator() {
    const messages = document.getElementById("chat-messages");
    const typing = document.createElement("div");
    typing.className = "chat-bubble typing";
    typing.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;
    messages.appendChild(typing);
    messages.scrollTop = messages.scrollHeight;
    return typing;
}

function addTraitNotification(trait) {
    const messages = document.getElementById("chat-messages");
    const notif = document.createElement("div");
    notif.className = "trait-learned";
    notif.textContent = `🧠 Learned: ${trait}`;
    messages.appendChild(notif);
    messages.scrollTop = messages.scrollHeight;
}

// ─── TTS & Lipsync ─────────────────────────────────────────
async function playTTS(text) {
    try {
        const voiceId = currentPersona?.voice_id || "en-US-GuyNeural";

        document.getElementById("status-text").textContent = "Generating Voice / Video...";

        const res = await fetch(`${API}/api/tts`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text,
                voice_id: voiceId,
                persona_id: currentPersonaId
            }),
        });
        const data = await res.json();

        if (data.video_url) {
            // We have a D-ID lip-sync video!
            let videoEl = document.getElementById("avatar-video");
            if (!videoEl) {
                const frame = document.getElementById("avatar-frame");
                videoEl = document.createElement("video");
                videoEl.id = "avatar-video";
                videoEl.style.width = "100%";
                videoEl.style.height = "100%";
                videoEl.style.objectFit = "cover";
                videoEl.playsInline = true;
                const overlay = document.getElementById("avatar-overlay");
                frame.insertBefore(videoEl, overlay);
            }

            const imgEl = document.getElementById("avatar-img");
            imgEl.style.display = "none";
            videoEl.style.display = "block";

            document.getElementById("status-text").textContent = "Speaking...";
            setAvatarSpeaking(true);

            videoEl.src = data.video_url;
            videoEl.onended = () => {
                setAvatarSpeaking(false);
                document.getElementById("status-text").textContent = "Online";
                videoEl.style.display = "none";
                if (currentPersona.photo_url) {
                    imgEl.style.display = "block";
                }
            };
            await videoEl.play();

        } else if (data.audio_url) {
            // Just audio
            document.getElementById("status-text").textContent = "Speaking...";
            setAvatarSpeaking(true);

            audioPlayer.src = `${API}${data.audio_url}`;
            audioPlayer.onended = () => {
                setAvatarSpeaking(false);
                document.getElementById("status-text").textContent = "Online";
            };
            await audioPlayer.play();
        } else {
            document.getElementById("status-text").textContent = "Online";
        }
    } catch (e) {
        console.error("TTS error:", e);
        setAvatarSpeaking(false);
        document.getElementById("status-text").textContent = "Online";
    }
}

function setAvatarSpeaking(speaking) {
    const glow = document.getElementById("avatar-glow");
    const frame = document.getElementById("avatar-frame");

    if (speaking) {
        glow.classList.add("speaking");
        frame.classList.add("speaking");
        startWaveformAnimation();
    } else {
        glow.classList.remove("speaking");
        frame.classList.remove("speaking");
        stopWaveformAnimation();
    }
}

// ─── Voice Input (Web Speech API) ─────────────────────────
window.toggleVoiceInput = function () {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
};

function startRecording() {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
        alert("Voice input is not supported in this browser. Please use Chrome.");
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
        isRecording = true;
        document.getElementById("btn-mic").classList.add("recording");
        document.getElementById("chat-input").placeholder = "Listening...";
    };

    recognition.onresult = (event) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        document.getElementById("chat-input").value = transcript;

        if (event.results[event.results.length - 1].isFinal) {
            stopRecording();
            sendMessage();
        }
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        stopRecording();
    };

    recognition.onend = () => {
        stopRecording();
    };

    recognition.start();
}

function stopRecording() {
    isRecording = false;
    document.getElementById("btn-mic").classList.remove("recording");
    document.getElementById("chat-input").placeholder = "Type a message...";
    if (recognition) recognition.stop();
}

// ─── Waveform Visualization ───────────────────────────────
function initWaveform() {
    const canvas = document.getElementById("waveform-canvas");
    if (!canvas) return;
    waveformCtx = canvas.getContext("2d");
    drawIdleWaveform();
}

function drawIdleWaveform() {
    if (!waveformCtx) return;
    const canvas = waveformCtx.canvas;
    waveformCtx.clearRect(0, 0, canvas.width, canvas.height);

    const bars = 40;
    const barWidth = canvas.width / bars;
    waveformCtx.fillStyle = "rgba(124, 92, 252, 0.2)";

    for (let i = 0; i < bars; i++) {
        const h = 4 + Math.random() * 4;
        const x = i * barWidth;
        const y = (canvas.height - h) / 2;
        waveformCtx.fillRect(x + 2, y, barWidth - 4, h);
    }
}

function startWaveformAnimation() {
    let frame = 0;
    function animate() {
        if (!waveformCtx) return;
        const canvas = waveformCtx.canvas;
        waveformCtx.clearRect(0, 0, canvas.width, canvas.height);

        const bars = 40;
        const barWidth = canvas.width / bars;

        for (let i = 0; i < bars; i++) {
            const h = 4 + Math.sin(frame * 0.1 + i * 0.3) * 15 + Math.random() * 8;
            const x = i * barWidth;
            const y = (canvas.height - h) / 2;

            const gradient = waveformCtx.createLinearGradient(0, y, 0, y + h);
            gradient.addColorStop(0, "rgba(124, 92, 252, 0.8)");
            gradient.addColorStop(1, "rgba(99, 68, 224, 0.3)");
            waveformCtx.fillStyle = gradient;
            waveformCtx.fillRect(x + 2, y, barWidth - 4, h);
        }

        frame++;
        waveformAnimId = requestAnimationFrame(animate);
    }
    animate();
}

function stopWaveformAnimation() {
    if (waveformAnimId) {
        cancelAnimationFrame(waveformAnimId);
        waveformAnimId = null;
    }
    drawIdleWaveform();
}
