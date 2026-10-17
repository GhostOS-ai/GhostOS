// GhostOS Interactive Frontend Controller

let currentMode = "pet";
let isThinking = false;
let currentClipboardText = "";

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  setupDragAndDrop();
  setupKeyboardShortcuts();
  refreshRpg();
  refreshChameleon();
});

// Toggle between Floating Casper and Spotlight HUD
function toggleHudMode(mode) {
  currentMode = mode;
  const petView = document.getElementById("pet-view");
  const hudView = document.getElementById("hud-view");

  if (mode === "hud") {
    petView.classList.add("hidden");
    hudView.classList.remove("hidden");
    setTimeout(() => {
      document.getElementById("hud-input").focus();
    }, 100);
    refreshVramStats();
    refreshKnowledgeDocs();
    refreshRpg();
    refreshChameleon();
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.toggle_mode("hud");
    }
  } else {
    hudView.classList.add("hidden");
    petView.classList.remove("hidden");
    setGhostMood("idle");
    refreshRpg();
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.toggle_mode("pet");
    }
  }
}

function minimizeWindow() {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.minimize_pet();
  }
}

// ==================== GHOST PET ANIMATION, MOODS & ACCESSORIES ====================
function setGhostMood(mood) {
  const mouth = document.getElementById("mouth");
  const aura = document.getElementById("aura");
  const speech = document.getElementById("speech-text");
  const headphones = document.getElementById("accessory-headphones");

  if (mood === "idle") {
    mouth.setAttribute("d", "M 73 80 Q 80 88 87 80");
    aura.setAttribute("fill", "url(#aura-grad)");
    if (headphones) headphones.style.display = "none";
  } else if (mood === "eating") {
    mouth.setAttribute("d", "M 72 78 Q 80 94 88 78 Q 80 74 72 78 Z");
    speech.innerText = "Nom nom nom! Ingesting file into memory (+15 XP)...";
  } else if (mood === "thinking") {
    aura.setAttribute("fill", "rgba(155, 81, 224, 0.4)");
    speech.innerText = "Consulting local neural weights...";
  } else if (mood === "listening") {
    if (headphones) headphones.style.display = "block";
    speech.innerText = "Listening to meeting audio...";
  } else if (mood === "happy") {
    mouth.setAttribute("d", "M 70 78 Q 80 92 90 78");
  }
}

// ==================== RPG EVOLUTION ====================
async function refreshRpg() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const stats = await window.pywebview.api.get_rpg_status();
      updateRpgUI(stats);
    } catch (e) {
      console.log("RPG init error:", e);
    }
  }
}

function updateRpgUI(stats) {
  if (!stats) return;

  const petBadge = document.getElementById("pet-rpg-badge");
  const hudTag = document.getElementById("hud-rpg-tag");
  if (petBadge) petBadge.innerText = `${stats.badge} (Lv.${stats.level})`;
  if (hudTag) hudTag.innerText = `Lv.${stats.level} ${stats.title} (${stats.xp} XP)`;

  // Toggle accessories based on evolution level
  const visor = document.getElementById("accessory-visor");
  const book = document.getElementById("accessory-book");
  const crown = document.getElementById("accessory-crown");

  if (visor) visor.style.display = (stats.level >= 3) ? "block" : "none";
  if (book) book.style.display = (stats.level >= 5) ? "block" : "none";
  if (crown) crown.style.display = (stats.level >= 6) ? "block" : "none";
}

// ==================== DRAG & DROP FILE INGESTION ====================
function setupDragAndDrop() {
  const petView = document.getElementById("pet-view");

  window.addEventListener("dragover", (e) => {
    e.preventDefault();
    petView.classList.add("drag-over");
    setGhostMood("eating");
    document.getElementById("speech-text").innerText = "Ooh! Feed me that file (+15 XP)!";
  });

  window.addEventListener("dragleave", (e) => {
    e.preventDefault();
    petView.classList.remove("drag-over");
    setGhostMood("idle");
    document.getElementById("speech-text").innerText = "Boo! Drag files here to feed me, or click to open HUD!";
  });

  window.addEventListener("drop", (e) => {
    e.preventDefault();
    petView.classList.remove("drag-over");
    
    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      handleFileIngestion(file);
    } else {
      setGhostMood("idle");
    }
  });
}

function handleFileIngestion(file) {
  setGhostMood("eating");
  const reader = new FileReader();

  reader.onload = async (event) => {
    const content = event.target.result;
    if (window.pywebview && window.pywebview.api) {
      try {
        const res = await window.pywebview.api.ingest_dropped_content(file.name, content);
        if (res.success) {
          document.getElementById("speech-text").innerText = `Yum! Ingested "${file.name}"! +15 XP`;
          refreshRpg();
        } else {
          document.getElementById("speech-text").innerText = `Couldn't eat that: ${res.error}`;
        }
      } catch (err) {
        document.getElementById("speech-text").innerText = `Ingestion error: ${err}`;
      }
    } else {
      document.getElementById("speech-text").innerText = `Chomp! Ingested "${file.name}"!`;
    }

    setTimeout(() => {
      setGhostMood("idle");
      document.getElementById("speech-text").innerText = "Boo! Ask me anything about your files!";
    }, 3500);
  };

  reader.readAsText(file);
}

// ==================== HUD INTERACTION & CHAT ====================
function setupKeyboardShortcuts() {
  const input = document.getElementById("hud-input");
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
    if (e.key === "Escape") {
      toggleHudMode("pet");
    }
  });

  const pilotInput = document.getElementById("pilot-input");
  if (pilotInput) {
    pilotInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        generateCommand();
      }
    });
  }
}

async function handleSend() {
  const input = document.getElementById("hud-input");
  const query = input.value.trim();
  if (!query || isThinking) return;

  // Slash commands routing
  if (query.startsWith("/clip")) {
    input.value = "";
    switchTab("clipboard");
    refreshClipboard();
    return;
  }
  if (query.startsWith("/time")) {
    input.value = "";
    switchTab("timemachine");
    refreshTimeMachine();
    return;
  }
  if (query.startsWith("/screen")) {
    input.value = "";
    switchTab("screen");
    runScreenPeek();
    return;
  }
  if (query.startsWith("/rag")) {
    input.value = "";
    switchTab("rag");
    refreshKnowledgeDocs();
    return;
  }
  if (query.startsWith("/status") || query.startsWith("/vram")) {
    input.value = "";
    switchTab("vram");
    refreshVramStats();
    return;
  }
  if (query.startsWith("/exec")) {
    const task = query.replace(/^\/exec\s*/, "");
    input.value = "";
    switchTab("autopilot");
    if (task) {
      document.getElementById("pilot-input").value = task;
      generateCommand();
    }
    return;
  }

  // Regular Chat message
  appendMessage("user", query);
  input.value = "";
  isThinking = true;
  setGhostMood("thinking");

  const typingId = appendTypingIndicator();

  try {
    let reply = "I am ready!";
    let citations = [];

    if (window.pywebview && window.pywebview.api) {
      const res = await window.pywebview.api.ask(query);
      reply = res.response;
      citations = res.citations || [];
      refreshRpg();
    } else {
      reply = `👻 (Simulated): Analyzed "${query}". 100% offline local inference ready.`;
    }

    removeTypingIndicator(typingId);
    appendMessage("ghost", reply, citations);
  } catch (err) {
    removeTypingIndicator(typingId);
    appendMessage("ghost", `⚠️ Error: ${err}`);
  } finally {
    isThinking = false;
    setGhostMood("idle");
  }
}

function appendMessage(sender, text, citations = []) {
  const container = document.getElementById("chat-messages");
  const msgDiv = document.createElement("div");
  msgDiv.className = `msg ${sender}`;

  const avatar = sender === "user" ? "👤" : "👻";
  let formattedText = formatMarkdown(text);

  if (citations.length > 0) {
    formattedText += `<div style="margin-top: 6px; font-size: 11px; color: var(--accent-cyan);">📚 Cited from: ${citations.join(", ")}</div>`;
  }

  msgDiv.innerHTML = `
    <div class="msg-avatar">${avatar}</div>
    <div class="msg-bubble">${formattedText}</div>
  `;

  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;
}

function appendTypingIndicator() {
  const container = document.getElementById("chat-messages");
  const id = "typing-" + Date.now();
  const div = document.createElement("div");
  div.id = id;
  div.className = "msg ghost";
  div.innerHTML = `
    <div class="msg-avatar">👻</div>
    <div class="msg-bubble" style="font-style: italic; color: var(--accent-cyan);">
      Thinking with local weights (Context Vacuum active)...
    </div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function formatMarkdown(text) {
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  html = html.replace(/```([a-z]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    return `<pre><code>${code.trim()}</code></pre>`;
  });

  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
  html = html.replace(/\n/g, "<br>");
  return html;
}

// ==================== TABS NAVIGATION ====================
function switchTab(tabName) {
  document.querySelectorAll(".nav-pill").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

  const targetPane = document.getElementById(`tab-${tabName}`);
  if (targetPane) targetPane.classList.add("active");

  const pills = Array.from(document.querySelectorAll(".nav-pill"));
  const match = pills.find(p => p.getAttribute("onclick").includes(tabName));
  if (match) match.classList.add("active");

  if (tabName === "vram") refreshVramStats();
  if (tabName === "rag") refreshKnowledgeDocs();
  if (tabName === "clipboard") refreshClipboard();
  if (tabName === "timemachine") refreshTimeMachine();
}

// ==================== PHANTOM CLIPBOARD ====================
async function refreshClipboard() {
  const badge = document.getElementById("clip-badge");
  const title = document.getElementById("clip-title");
  const preview = document.getElementById("clip-preview-text");
  const actionsBox = document.getElementById("clip-actions-container");

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.inspect_clipboard();
    currentClipboardText = res.raw_text || "";
    badge.innerText = res.badge;
    title.innerText = res.action_title || "Action Available";
    preview.innerText = res.raw_text || "(Clipboard empty)";

    actionsBox.innerHTML = "";
    (res.actions || []).forEach(act => {
      const btn = document.createElement("button");
      btn.className = "clip-action-btn";
      btn.innerText = act;
      btn.onclick = () => runClipboardAction(act, currentClipboardText);
      actionsBox.appendChild(btn);
    });
  }
}

async function runClipboardAction(action, text) {
  const outBox = document.getElementById("clip-output-box");
  const resultText = document.getElementById("clip-result-text");
  outBox.classList.remove("hidden");
  resultText.innerText = "Processing with zero-latency heuristics...";

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.apply_clipboard_action(action, text);
    if (res.success) {
      resultText.innerText = res.result;
      if (res.copied) alert("Result copied to clipboard!");
      refreshRpg();
    } else {
      resultText.innerText = `Error: ${res.error}`;
    }
  }
}

// ==================== TIME MACHINE ====================
async function refreshTimeMachine() {
  const summaryBox = document.getElementById("tm-summary");
  const commitMsg = document.getElementById("tm-commit-msg");

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.get_time_machine_summary();
    summaryBox.innerHTML = formatMarkdown(res.summary);
    if (res.commit_suggestion) {
      commitMsg.innerText = res.commit_suggestion;
    }
  }
}

function copyCommitMsg() {
  const msg = document.getElementById("tm-commit-msg").innerText;
  navigator.clipboard.writeText(msg);
  alert("Git commit message copied to clipboard!");
}

// ==================== SCREEN PEEK ====================
async function runScreenPeek() {
  const box = document.getElementById("screen-result");
  box.innerHTML = "<p>Capturing active window silently...</p>";

  if (window.pywebview && window.pywebview.api) {
    try {
      const res = await window.pywebview.api.peek_screen();
      if (res.success) {
        box.innerHTML = formatMarkdown(res.analysis);
        refreshRpg();
      } else {
        box.innerHTML = `<p style="color: #ff6584;">Capture error: ${res.error}</p>`;
      }
    } catch (err) {
      box.innerHTML = `<p style="color: #ff6584;">Error: ${err}</p>`;
    }
  }
}

// ==================== TERMINAL AUTOPILOT ====================
let currentGeneratedCommand = "";

async function generateCommand() {
  const input = document.getElementById("pilot-input");
  const task = input.value.trim();
  if (!task) return;

  const resultCard = document.getElementById("pilot-result");
  resultCard.classList.remove("hidden");
  document.getElementById("pilot-output-box").classList.add("hidden");

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.generate_autopilot_command(task);
    currentGeneratedCommand = res.command;
    document.getElementById("pilot-cmd").innerText = res.command;
    document.getElementById("pilot-desc").innerText = res.explanation;
    
    const badge = document.getElementById("pilot-badge");
    badge.innerText = res.risk.badge;

    // Show Anti-Hallucination Lens patch info
    const lensInfo = document.getElementById("pilot-lens-info");
    if (res.lens_modifications && res.lens_modifications.length > 0) {
      lensInfo.classList.remove("hidden");
      lensInfo.innerHTML = `🛡️ <b>Anti-Hallucination Lens:</b> ${res.lens_modifications.join("; ")}`;
    } else {
      lensInfo.classList.add("hidden");
    }
  }
}

async function runGeneratedCommand() {
  if (!currentGeneratedCommand) return;
  const outBox = document.getElementById("pilot-output-box");
  const stdoutEl = document.getElementById("pilot-stdout");
  outBox.classList.remove("hidden");
  stdoutEl.innerText = "Executing in zsh...";

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.execute_terminal(currentGeneratedCommand);
    stdoutEl.innerText = res.stdout || res.stderr || `(Completed with exit code ${res.exit_code})`;
    refreshRpg();
  }
}

function copyCommand() {
  if (currentGeneratedCommand) {
    navigator.clipboard.writeText(currentGeneratedCommand);
    alert("Command copied to clipboard!");
  }
}

// ==================== VRAM & CHAMELEON ====================
async function refreshVramStats() {
  if (window.pywebview && window.pywebview.api) {
    const stats = await window.pywebview.api.get_memory_stats();
    document.getElementById("stat-active-vram").innerText = `${stats.active_vram_mb} MB`;
    document.getElementById("stat-saved-vram").innerText = `+${stats.vram_saved_mb} MB`;
    document.getElementById("stat-swaps").innerText = stats.total_swaps;
    document.getElementById("stat-ram-percent").innerText = `${stats.system_ram_percent}%`;
  }
}

async function refreshChameleon() {
  if (window.pywebview && window.pywebview.api) {
    const profile = await window.pywebview.api.get_chameleon_profile();
    const pill = document.getElementById("chameleon-pill");
    const details = document.getElementById("chameleon-details");

    const modeLabels = {
      eco: "🍃 ECO (Battery)",
      balanced: "⚖️ BALANCED",
      performance: "⚡ BEAST MODE"
    };

    if (pill) pill.innerText = modeLabels[profile.active_mode] || "🍃 ECO";
    if (details) {
      details.innerHTML = `
        Mode: <b>${profile.name}</b> | Context Window: <b>${profile.context_window} tok</b> | 
        Auto-sleep: <b>${profile.auto_sleep_seconds}s</b> | Battery: <b>${profile.is_battery ? 'Yes (Power-save)' : 'Plugged-in'}</b>
      `;
    }

    // Update active button
    document.querySelectorAll(".mode-btn").forEach(btn => btn.classList.remove("active"));
    const activeBtn = document.getElementById(`btn-mode-${profile.active_mode}`);
    if (activeBtn) activeBtn.classList.add("active");
  }
}

async function setChameleonMode(mode) {
  if (window.pywebview && window.pywebview.api) {
    await window.pywebview.api.set_chameleon_mode(mode);
    refreshChameleon();
    refreshVramStats();
  }
}

function cycleChameleonMode() {
  const pill = document.getElementById("chameleon-pill");
  const current = pill.innerText;
  if (current.includes("ECO")) setChameleonMode("balanced");
  else if (current.includes("BALANCED")) setChameleonMode("performance");
  else setChameleonMode("eco");
}

async function refreshKnowledgeDocs() {
  const listEl = document.getElementById("rag-doc-list");
  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.get_indexed_documents();
    const docs = res.documents || [];
    if (docs.length === 0) {
      listEl.innerHTML = '<div class="doc-item empty">No files indexed yet. Feed some files to Casper!</div>';
      return;
    }
    listEl.innerHTML = docs.map(d => `
      <div class="doc-item">
        <span>📄 <b>${d.filename}</b> (${d.chunk_count} chunks)</span>
        <span style="color: var(--text-muted); font-size: 11px;">${Math.round(d.size_bytes / 1024)} KB</span>
      </div>
    `).join("");
  }
}

// ==================== VOICE & DICTATION ====================
let isVoiceEnabled = false;
let recognition = null;
let isDictating = false;

async function toggleVoice() {
  const btn = document.getElementById("voice-toggle-btn");
  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.toggle_voice();
    isVoiceEnabled = res.voice_enabled;
    btn.innerText = isVoiceEnabled ? "🔊 Voice ON" : "🔇 Voice OFF";
    btn.style.color = isVoiceEnabled ? "var(--accent-cyan)" : "inherit";
  }
}

function toggleDictation() {
  const micBtn = document.getElementById("mic-btn");
  const input = document.getElementById("hud-input");

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this WebKit window. Type your message below.");
    return;
  }

  if (isDictating) {
    if (recognition) recognition.stop();
    isDictating = false;
    micBtn.innerText = "🎙️";
    setGhostMood("idle");
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "ru-RU"; // or auto
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isDictating = true;
    micBtn.innerText = "🔴 Listening...";
    setGhostMood("listening");
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    input.value = transcript;
    micBtn.innerText = "🎙️";
    isDictating = false;
    setGhostMood("idle");
    handleSend();
  };

  recognition.onerror = (event) => {
    console.log("Speech recognition error:", event.error);
    micBtn.innerText = "🎙️";
    isDictating = false;
    setGhostMood("idle");
  };

  recognition.onend = () => {
    micBtn.innerText = "🎙️";
    isDictating = false;
    setGhostMood("idle");
  };

  recognition.start();
}

// ==================== OS AGENT ====================
async function runAgentTask() {
  const input = document.getElementById("agent-input");
  const task = input.value.trim();
  if (!task) return;

  const resultCard = document.getElementById("agent-result");
  const outputEl = document.getElementById("agent-output");
  resultCard.classList.remove("hidden");
  outputEl.innerHTML = "Executing OS Agent task via Apple Spotlight / System Calls...";

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.execute_agent_task(task);
    outputEl.innerHTML = formatMarkdown(res.output || "Done.");
    refreshRpg();
  }
}

// ==================== WEB SEARCH ====================
async function runWebSearch() {
  const input = document.getElementById("web-input");
  const query = input.value.trim();
  if (!query) return;

  const resultCard = document.getElementById("web-result");
  const outputEl = document.getElementById("web-output");
  resultCard.classList.remove("hidden");
  outputEl.innerHTML = "Fetching live web information with zero memory bloat...";

  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.search_web(query);
    outputEl.innerHTML = formatMarkdown(res.content || "No results found.");
  }
}
