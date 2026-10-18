// GhostOS — Interactive Frontend Controller (Desktop Copilot)

let currentMode = "pet";
let isThinking = false;
let currentClipboardText = "";
let sleepTimer = null;
let isSleeping = false;
let clickIndex = 0;
let petClickDebounceTimer = null;
let bubbleHideTimer = null;

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  if (window.i18n) {
    i18n.applyTranslations();
  }
  setupDragAndDrop();
  setupKeyboardShortcuts();
  setupEyeTracking();
  setupInactivitySleep();
  refreshRpg();
  refreshChameleon();
});

// ==================== SPEECH BUBBLE AUTO-HIDE ====================
// Shows speech bubble for `durationMs` then smoothly fades out and disappears
function showSpeechBubble(text, durationMs = 3500) {
  const bubble = document.getElementById("speech-bubble");
  const speechText = document.getElementById("speech-text");
  if (!bubble || !speechText) return;

  speechText.innerText = text;
  bubble.classList.add("visible");

  clearTimeout(bubbleHideTimer);
  if (durationMs > 0) {
    bubbleHideTimer = setTimeout(() => {
      bubble.classList.remove("visible");
    }, durationMs);
  }
}

function hideSpeechBubble() {
  const bubble = document.getElementById("speech-bubble");
  if (bubble) bubble.classList.remove("visible");
  clearTimeout(bubbleHideTimer);
}

// ==================== DEBOUNCED CLICK VS DOUBLE CLICK ====================
// Solves sluggish window movement by eliminating double click event collisions
function onPetClick(event) {
  if (petClickDebounceTimer !== null) {
    // Second click detected -> DOUBLE CLICK!
    clearTimeout(petClickDebounceTimer);
    petClickDebounceTimer = null;
    hideSpeechBubble();
    toggleHudMode("hud");
    return;
  }

  // First click -> wait 220ms before triggering single-click reaction
  petClickDebounceTimer = setTimeout(() => {
    petClickDebounceTimer = null;
    handlePetClick(event);
  }, 220);
}

// Toggle between Floating Casper and Spotlight HUD
function toggleHudMode(mode) {
  currentMode = mode;
  const petView = document.getElementById("pet-view");
  const hudView = document.getElementById("hud-view");

  if (mode === "hud") {
    petView.classList.add("hidden");
    hudView.classList.remove("hidden");
    hideSpeechBubble();

    // Smooth resize via WebKit Cocoa Bridge
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.toggle_mode("hud");
    }

    setTimeout(() => {
      const input = document.getElementById("hud-input");
      if (input) input.focus();
    }, 80);

    // Light asynchronous header refreshes without blocking
    refreshRpg();
    refreshChameleon();
  } else {
    hudView.classList.add("hidden");
    petView.classList.remove("hidden");
    setGhostMood("idle");
    hideSpeechBubble();

    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.toggle_mode("pet");
    }
    refreshRpg();
  }
}

function minimizeWindow() {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.minimize_pet();
  }
}

// ==================== CASPER EYE TRACKING ====================
function setupEyeTracking() {
  const pupilLeft = document.getElementById("eye-pupil-left");
  const pupilRight = document.getElementById("eye-pupil-right");
  const svg = document.getElementById("ghost-svg");

  window.addEventListener("mousemove", (e) => {
    resetInactivityTimer();
    if (!pupilLeft || !pupilRight || isSleeping || currentMode !== "pet") return;

    const rect = svg.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const dx = (e.clientX - centerX) / (rect.width / 2);
    const dy = (e.clientY - centerY) / (rect.height / 2);

    const maxOffset = 2.6;
    const offsetX = Math.max(-maxOffset, Math.min(maxOffset, dx * maxOffset));
    const offsetY = Math.max(-maxOffset, Math.min(maxOffset, dy * maxOffset));

    pupilLeft.setAttribute("cx", 67 + offsetX);
    pupilLeft.setAttribute("cy", 63 + offsetY);
    pupilRight.setAttribute("cx", 97 + offsetX);
    pupilRight.setAttribute("cy", 63 + offsetY);
  });
}

// ==================== INACTIVITY SLEEP / WAKEUP ====================
function setupInactivitySleep() {
  resetInactivityTimer();
}

function resetInactivityTimer() {
  if (isSleeping) {
    wakeUpCasper();
  }
  clearTimeout(sleepTimer);
  sleepTimer = setTimeout(() => {
    if (currentMode === "pet" && !isThinking) {
      putCasperToSleep();
    }
  }, 25000);
}

function putCasperToSleep() {
  isSleeping = true;
  setGhostMood("sleepy");
  // Speech bubble stays hidden or shows gentle sleep note briefly
  showSpeechBubble(window.i18n ? i18n.t("sleeping") : "💤 zZz...", 2500);
}

function wakeUpCasper() {
  isSleeping = false;
  setGhostMood("happy");
  showSpeechBubble(window.i18n ? i18n.t("waking") : "Boo! 👻", 2500);
  setTimeout(() => {
    if (!isSleeping && currentMode === "pet") {
      setGhostMood("idle");
    }
  }, 2600);
}

// ==================== CASPER SINGLE CLICK INTERACTION ====================
function handlePetClick(event) {
  resetInactivityTimer();
  const wrapper = document.getElementById("ghost-wrapper");
  if (wrapper) {
    wrapper.classList.remove("wobble", "giggle");
    void wrapper.offsetWidth; // trigger reflow
    wrapper.classList.add(clickIndex % 2 === 0 ? "wobble" : "giggle");
    setTimeout(() => wrapper.classList.remove("wobble", "giggle"), 550);
  }

  setGhostMood("happy");

  const quotes = window.i18n ? i18n.getQuotes() : ["Boo! 👻"];
  const phrase = quotes[clickIndex % quotes.length];
  clickIndex++;

  // Show bubble for 3.5 seconds, then auto-hide cleanly
  showSpeechBubble(phrase, 3500);

  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.speak_text(phrase);
  }

  setTimeout(() => {
    if (currentMode === "pet" && !isSleeping) {
      setGhostMood("idle");
    }
  }, 3600);
}

// Quick action buttons in pet bar
function quickOpenFolder(e) {
  if (e) e.stopPropagation();
  resetInactivityTimer();
  showSpeechBubble("📂 " + (window.i18n ? i18n.t("folder_opened") : "Opening Finder..."), 3000);
  setGhostMood("happy");

  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.quick_open_folder().then((res) => {
      if (res.output) showSpeechBubble(res.output, 3500);
    });
  }
}

function quickToggleFly(e) {
  if (e) e.stopPropagation();
  resetInactivityTimer();
  const btn = document.getElementById("pet-fly-btn");

  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.toggle_wandering().then((res) => {
      if (res.wandering) {
        if (btn) btn.classList.add("active");
        showSpeechBubble(window.i18n ? i18n.t("flight_on") : "✈️ Flying!", 3000);
        setGhostMood("happy");
      } else {
        if (btn) btn.classList.remove("active");
        showSpeechBubble(window.i18n ? i18n.t("flight_off") : "🛬 Landed!", 2500);
        setGhostMood("idle");
      }
    });
  }
}

function quickToggleVoice(e) {
  if (e) e.stopPropagation();
  resetInactivityTimer();
  const btn = document.getElementById("pet-voice-btn");
  const hudBtn = document.getElementById("voice-toggle-btn");

  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.toggle_voice().then((res) => {
      if (res.voice_enabled) {
        if (btn) btn.classList.add("active");
        if (hudBtn) hudBtn.innerText = window.i18n ? i18n.t("voice_toggle_on") : "🔊 Voice ON";
        showSpeechBubble(window.i18n ? i18n.t("voice_on") : "🗣️ Voice ON", 3000);
      } else {
        if (btn) btn.classList.remove("active");
        if (hudBtn) hudBtn.innerText = window.i18n ? i18n.t("voice_toggle_off") : "🔇 Voice";
        showSpeechBubble(window.i18n ? i18n.t("voice_off") : "🔇 Voice OFF", 2500);
      }
    });
  }
}

// ==================== GHOST PET ANIMATION & MOODS ====================
function setGhostMood(mood) {
  const mouth = document.getElementById("mouth");
  const aura = document.getElementById("aura");
  const headphones = document.getElementById("accessory-headphones");
  const blushLeft = document.getElementById("blush-left");
  const blushRight = document.getElementById("blush-right");
  const eyeLeft = document.getElementById("eye-left");
  const eyeRight = document.getElementById("eye-right");

  // Reset eyes
  if (eyeLeft) eyeLeft.setAttribute("transform", "scale(1, 1)");
  if (eyeRight) eyeRight.setAttribute("transform", "scale(1, 1)");

  if (mood === "idle") {
    if (mouth) mouth.setAttribute("d", "M 73 80 Q 80 88 87 80");
    if (aura) aura.setAttribute("fill", "url(#aura-grad)");
    if (headphones) headphones.style.display = "none";
    if (blushLeft) blushLeft.style.opacity = "0.55";
    if (blushRight) blushRight.style.opacity = "0.55";
  } else if (mood === "eating") {
    if (mouth) mouth.setAttribute("d", "M 72 75 Q 80 96 88 75 Q 80 72 72 75 Z");
    if (aura) aura.setAttribute("fill", "rgba(66, 133, 244, 0.6)");
  } else if (mood === "thinking") {
    if (aura) aura.setAttribute("fill", "rgba(161, 66, 244, 0.45)");
    if (mouth) mouth.setAttribute("d", "M 75 80 Q 80 82 85 80");
  } else if (mood === "listening") {
    if (headphones) headphones.style.display = "block";
  } else if (mood === "happy") {
    if (mouth) mouth.setAttribute("d", "M 68 76 Q 80 94 92 76");
    if (aura) aura.setAttribute("fill", "rgba(27, 160, 252, 0.5)");
    if (blushLeft) blushLeft.style.opacity = "0.9";
    if (blushRight) blushRight.style.opacity = "0.9";
  } else if (mood === "sleepy") {
    if (mouth) mouth.setAttribute("d", "M 76 82 Q 80 85 84 82");
    if (aura) aura.setAttribute("fill", "rgba(100, 150, 255, 0.15)");
    if (eyeLeft) eyeLeft.setAttribute("transform", "scale(1, 0.15)");
    if (eyeRight) eyeRight.setAttribute("transform", "scale(1, 0.15)");
    if (blushLeft) blushLeft.style.opacity = "0.2";
    if (blushRight) blushRight.style.opacity = "0.2";
  }
}

// ==================== RPG EVOLUTION ====================
async function refreshRpg() {
  if (window.pywebview && window.pywebview.api) {
    try {
      const stats = await window.pywebview.api.get_rpg_status();
      updateRpgUI(stats);
    } catch (e) {
      console.log("RPG status error:", e);
    }
  }
}

function updateRpgUI(stats) {
  if (!stats) return;

  const petBadge = document.getElementById("pet-rpg-badge");
  const hudTag = document.getElementById("hud-rpg-tag");
  if (petBadge) petBadge.innerText = `${stats.badge} (Lv.${stats.level})`;
  if (hudTag) hudTag.innerText = `Lv.${stats.level} ${stats.title} (${stats.xp} XP)`;

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
    showSpeechBubble(window.i18n ? i18n.t("feed_prompt") : "🍕 Feed Me Files!", 3000);
  });

  window.addEventListener("dragleave", (e) => {
    e.preventDefault();
    petView.classList.remove("drag-over");
    setGhostMood("idle");
    hideSpeechBubble();
  });

  window.addEventListener("drop", (e) => {
    e.preventDefault();
    petView.classList.remove("drag-over");
    
    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      handleFileIngestion(file);
    } else {
      setGhostMood("idle");
      hideSpeechBubble();
    }
  });
}

function handleFileIngestion(file) {
  setGhostMood("eating");
  showSpeechBubble(window.i18n ? i18n.t("eating") : "Nom nom nom...", 4000);
  const reader = new FileReader();

  reader.onload = async (event) => {
    const content = event.target.result;
    if (window.pywebview && window.pywebview.api) {
      try {
        const res = await window.pywebview.api.ingest_dropped_content(file.name, content);
        if (res.success) {
          showSpeechBubble(`✔ "${file.name}" learned! +15 XP`, 3500);
          refreshRpg();
        } else {
          showSpeechBubble(`Error: ${res.error}`, 3500);
        }
      } catch (err) {
        showSpeechBubble(`Error: ${err}`, 3500);
      }
    }

    setTimeout(() => {
      setGhostMood("idle");
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
    let reply = "Ready!";
    let citations = [];

    if (window.pywebview && window.pywebview.api) {
      const res = await window.pywebview.api.ask(query);
      reply = res.response;
      citations = res.citations || [];
      refreshRpg();
    } else {
      reply = `👻 Analyzed "${query}". 100% offline inference active.`;
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

  if (citations && citations.length > 0) {
    formattedText += `<div style="margin-top: 6px; font-size: 11px; color: var(--mac-accent);">📚 Cited: ${citations.join(", ")}</div>`;
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
    <div class="msg-bubble" style="font-style: italic; color: var(--mac-accent);">
      ${window.i18n ? i18n.t("thinking") : "Thinking with local neural weights..."}
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
  const match = pills.find(p => {
    const oc = p.getAttribute("onclick") || "";
    return oc.includes(tabName);
  });
  if (match) match.classList.add("active");

  // Load heavy stats lazily only when tab is activated
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
      btn.className = "action-btn";
      btn.style.marginRight = "6px";
      btn.style.marginTop = "6px";
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
      if (res.copied) showSpeechBubble("✔ Copied to clipboard!", 2500);
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
  showSpeechBubble("✔ Commit message copied!", 2500);
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
        box.innerHTML = `<p style="color: var(--mac-coral);">Capture error: ${res.error}</p>`;
      }
    } catch (err) {
      box.innerHTML = `<p style="color: var(--mac-coral);">Error: ${err}</p>`;
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
    showSpeechBubble("✔ Command copied!", 2500);
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
      eco: window.i18n ? i18n.t("eco") : "🍃 ECO",
      balanced: window.i18n ? i18n.t("balanced") : "⚖️ Balanced",
      performance: window.i18n ? i18n.t("beast") : "⚡ Beast"
    };

    if (pill) pill.innerText = modeLabels[profile.active_mode] || "🍃 ECO";
    if (details) {
      details.innerHTML = `
        Mode: <b>${profile.name}</b> | Context: <b>${profile.context_window} tok</b> | 
        Auto-sleep: <b>${profile.auto_sleep_seconds}s</b> | Power: <b>${profile.is_battery ? 'Battery' : 'AC Adapter'}</b>
      `;
    }

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
  if (current.includes("ECO") || current.includes("ЭКО")) setChameleonMode("balanced");
  else if (current.includes("Balanced") || current.includes("Баланс")) setChameleonMode("performance");
  else setChameleonMode("eco");
}

async function refreshKnowledgeDocs() {
  const listEl = document.getElementById("rag-doc-list");
  if (window.pywebview && window.pywebview.api) {
    const res = await window.pywebview.api.get_indexed_documents();
    const docs = res.documents || [];
    if (docs.length === 0) {
      listEl.innerHTML = `<div class="doc-item empty">${window.i18n ? i18n.t("rag_empty") : "No files indexed yet."}</div>`;
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
    btn.innerText = isVoiceEnabled 
      ? (window.i18n ? i18n.t("voice_toggle_on") : "🔊 Voice ON")
      : (window.i18n ? i18n.t("voice_toggle_off") : "🔇 Voice");
    btn.style.color = isVoiceEnabled ? "var(--mac-accent)" : "inherit";
  }
}

function toggleDictation() {
  const micBtn = document.getElementById("mic-btn");
  const input = document.getElementById("hud-input");

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this WebKit window.");
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
  const langMap = { ru: "ru-RU", kk: "kk-KZ", zh: "zh-CN", es: "es-ES", de: "de-DE", fr: "fr-FR", ja: "ja-JP", pt: "pt-BR", ar: "ar-SA", hi: "hi-IN", en: "en-US" };
  const currentLang = window.i18n ? i18n.currentLang : "en";
  recognition.lang = langMap[currentLang] || "en-US";
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

  recognition.onerror = () => {
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
  outputEl.innerHTML = "Executing OS Agent task via Apple Spotlight / Native OS Calls...";

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
