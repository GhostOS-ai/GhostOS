// GhostOS Interactive Frontend Controller

let currentMode = "pet";
let isThinking = false;

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  setupDragAndDrop();
  setupKeyboardShortcuts();
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
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.toggle_mode("hud");
    }
  } else {
    hudView.classList.add("hidden");
    petView.classList.remove("hidden");
    setGhostMood("idle");
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

// ==================== GHOST PET ANIMATION & MOODS ====================
function setGhostMood(mood) {
  const mouth = document.getElementById("mouth");
  const aura = document.getElementById("aura");
  const speech = document.getElementById("speech-text");
  const headphones = document.getElementById("headphones");

  if (mood === "idle") {
    mouth.setAttribute("d", "M 73 80 Q 80 88 87 80");
    aura.setAttribute("fill", "url(#aura-grad)");
    headphones.style.display = "none";
  } else if (mood === "eating") {
    // Open mouth wide for eating
    mouth.setAttribute("d", "M 72 78 Q 80 94 88 78 Q 80 74 72 78 Z");
    speech.innerText = "Nom nom nom! Ingesting file into memory...";
  } else if (mood === "thinking") {
    aura.setAttribute("fill", "rgba(155, 81, 224, 0.4)");
    speech.innerText = "Consulting local neural weights...";
  } else if (mood === "listening") {
    headphones.style.display = "block";
    speech.innerText = "Listening to meeting audio...";
  } else if (mood === "happy") {
    mouth.setAttribute("d", "M 70 78 Q 80 92 90 78");
  }
}

// ==================== DRAG & DROP FILE INGESTION ====================
function setupDragAndDrop() {
  const petView = document.getElementById("pet-view");

  window.addEventListener("dragover", (e) => {
    e.preventDefault();
    petView.classList.add("drag-over");
    setGhostMood("eating");
    document.getElementById("speech-text").innerText = "Ooh! Feed me that file!";
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
          document.getElementById("speech-text").innerText = `Yum! Ingested "${file.name}" (${res.chunks_count} chunks)!`;
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
      Thinking with local weights...
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
  // Simple clean markdown parser for code blocks and bold
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Code blocks
  html = html.replace(/```([a-z]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    return `<pre><code>${code.trim()}</code></pre>`;
  });

  // Inline code
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Bold
  html = html.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");

  // Newlines
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
      } else {
        box.innerHTML = `<p style="color: #ff6584;">Capture error: ${res.error}</p>`;
      }
    } catch (err) {
      box.innerHTML = `<p style="color: #ff6584;">Error: ${err}</p>`;
    }
  } else {
    box.innerHTML = "<p>👁️ Screen Peek (Simulated): Active app is VS Code. No syntax errors detected.</p>";
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
  } else {
    currentGeneratedCommand = `find . -name "*.${task}"`;
    document.getElementById("pilot-cmd").innerText = currentGeneratedCommand;
    document.getElementById("pilot-desc").innerText = "Find files matching your query.";
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
  } else {
    stdoutEl.innerText = "Executed simulated command successfully.";
  }
}

function copyCommand() {
  if (currentGeneratedCommand) {
    navigator.clipboard.writeText(currentGeneratedCommand);
    alert("Command copied to clipboard!");
  }
}

// ==================== VRAM & KNOWLEDGE REFRESH ====================
async function refreshVramStats() {
  if (window.pywebview && window.pywebview.api) {
    const stats = await window.pywebview.api.get_memory_stats();
    document.getElementById("stat-active-vram").innerText = `${stats.active_vram_mb} MB`;
    document.getElementById("stat-saved-vram").innerText = `+${stats.vram_saved_mb} MB`;
    document.getElementById("stat-swaps").innerText = stats.total_swaps;
    document.getElementById("stat-ram-percent").innerText = `${stats.system_ram_percent}%`;
  }
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
