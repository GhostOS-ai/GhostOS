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
  setupHudDragAndDrop();
  setupKeyboardShortcuts();
  setupEyeTracking();
  setupInactivitySleep();
  refreshRpg();
  refreshChameleon();

  // Apply Skin from localStorage or URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const skin = localStorage.getItem("ghostos_skin") || urlParams.get("skin") || "glass";
  switchSkin(skin, false);

  // Direct Spotlight / HUD / Studio Mode launcher
  const mode = urlParams.get("mode");
  if (mode === "hud" || mode === "spotlight" || mode === "studio") {
    setTimeout(() => {
      toggleHudMode(mode === "studio" ? "studio" : "hud");
      if (mode === "studio") {
        switchStudioMode("chat");
      }
    }, 50);
  }
  setupStudioListeners();
});

function applySkin(skinName) {
  document.body.classList.remove("skin-glass", "skin-cyberpunk", "skin-gold", "skin-matrix");
  document.body.classList.add(`skin-${skinName}`);
}

function switchSkin(skinName, notifyBackend = true) {
  applySkin(skinName);
  try {
    localStorage.setItem("ghostos_skin", skinName);
  } catch (e) {}
  const select = document.getElementById("skin-select");
  if (select && select.value !== skinName) {
    select.value = skinName;
  }
  if (notifyBackend && window.pywebview && window.pywebview.api && window.pywebview.api.set_skin) {
    window.pywebview.api.set_skin(skinName).catch(() => {});
  }
}

function clearChatHistory() {
  const container = document.getElementById("chat-messages");
  if (!container) return;
  container.innerHTML = `
    <div class="chat-welcome-container">
      <div class="welcome-avatar">👻</div>
      <h1 class="welcome-title">Чем я могу помочь сегодня?</h1>
      <p class="welcome-subtitle">
        Ваш персональный локальный ИИ. Пишите код, анализируйте файлы и управляйте macOS в полной приватности.
      </p>

      <div class="welcome-prompt-grid">
        <div class="prompt-card" onclick="triggerQuickAction('Напиши скрипт на Python для автоматизации поиска дубликатов файлов')">
          <span class="prompt-icon">💡</span>
          <div class="prompt-content">
            <span class="prompt-title">Написать скрипт на Python</span>
            <span class="prompt-desc">Автоматизация задач и утилиты</span>
          </div>
        </div>
        <div class="prompt-card highlight" onclick="switchStudioMode('code')">
          <span class="prompt-icon">⚡</span>
          <div class="prompt-content">
            <span class="prompt-title">Открыть GhostCode IDE</span>
            <span class="prompt-desc">Автономная разработка проектов</span>
          </div>
        </div>
        <div class="prompt-card" onclick="triggerQuickAction('Объясни, как работает Zero-DB RAG и локальная векторная память')">
          <span class="prompt-icon">📚</span>
          <div class="prompt-content">
            <span class="prompt-title">Изучить и объяснить тему</span>
            <span class="prompt-desc">Архитектура, алгоритмы и документация</span>
          </div>
        </div>
        <div class="prompt-card" onclick="triggerQuickAction('Погода в Алматы и курс доллара')">
          <span class="prompt-icon">🌤️</span>
          <div class="prompt-content">
            <span class="prompt-title">Погода и курсы валют</span>
            <span class="prompt-desc">Быстрый поиск информации</span>
          </div>
        </div>
      </div>
    </div>
  `;
  if (window.i18n) {
    i18n.applyTranslations();
  }
  if (window.pywebview && window.pywebview.api && window.pywebview.api.clear_chat) {
    window.pywebview.api.clear_chat().catch(() => {});
  }
  showSpeechBubble("🧹 " + (window.i18n ? i18n.t("clear_chat", "История очищена") : "История очищена"), 2500);
}

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
    toggleHudMode("studio");
    return;
  }

  // First click -> wait 220ms before triggering single-click reaction
  petClickDebounceTimer = setTimeout(() => {
    petClickDebounceTimer = null;
    handlePetClick(event);
  }, 220);
}

// Toggle between Floating Casper and Spotlight HUD / Studio
function toggleHudMode(mode) {
  currentMode = mode;
  const petView = document.getElementById("pet-view");
  const hudView = document.getElementById("hud-view");

  if (mode === "hud" || mode === "studio") {
    petView.classList.add("hidden");
    hudView.classList.remove("hidden");
    hideSpeechBubble();

    // Smooth resize via WebKit Cocoa Bridge
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.toggle_mode(mode);
    }

    setTimeout(() => {
      const input = document.getElementById("hud-input");
      if (input) input.focus();
    }, 80);

    // Light asynchronous header refreshes without blocking
    refreshRpg();
    refreshChameleon();
    refreshWorkspaceExplorer();
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
  const wrapper = document.getElementById("ghost-wrapper");
  if (wrapper) wrapper.classList.add("eating-chew");

  showSpeechBubble(window.i18n ? i18n.t("eating") : "✨ Nom nom nom...", 4000);
  const reader = new FileReader();

  const isPdfOrBinary = file.name.toLowerCase().endsWith(".pdf") || 
                        file.name.toLowerCase().endsWith(".png") || 
                        file.name.toLowerCase().endsWith(".jpg");

  reader.onload = async (event) => {
    const content = event.target.result;
    if (window.pywebview && window.pywebview.api) {
      try {
        let res;
        if (isPdfOrBinary && window.pywebview.api.ingest_dropped_file_base64) {
          res = await window.pywebview.api.ingest_dropped_file_base64(file.name, content);
        } else {
          res = await window.pywebview.api.ingest_dropped_content(file.name, content);
        }

        if (res && res.success) {
          showSpeechBubble(`✨ Yum! "${file.name}" learned! +25 XP`, 3800);
          refreshRpg();
        } else {
          showSpeechBubble(`Error: ${res ? res.error : "Failed to parse"}`, 3500);
        }
      } catch (err) {
        showSpeechBubble(`Error: ${err}`, 3500);
      }
    }

    setTimeout(() => {
      setGhostMood("idle");
      if (wrapper) wrapper.classList.remove("eating-chew");
    }, 3200);
  };

  if (isPdfOrBinary) {
    reader.readAsDataURL(file);
  } else {
    reader.readAsText(file);
  }
}

function setupHudDragAndDrop() {
  const hudView = document.getElementById("hud-view");
  const overlay = document.getElementById("hud-drop-overlay");
  if (!hudView || !overlay) return;

  let dragCounter = 0;

  hudView.addEventListener("dragenter", (e) => {
    e.preventDefault();
    dragCounter++;
    overlay.classList.remove("hidden");
  });

  hudView.addEventListener("dragleave", (e) => {
    e.preventDefault();
    dragCounter--;
    if (dragCounter <= 0) {
      dragCounter = 0;
      overlay.classList.add("hidden");
    }
  });

  hudView.addEventListener("dragover", (e) => {
    e.preventDefault();
  });

  hudView.addEventListener("drop", (e) => {
    e.preventDefault();
    dragCounter = 0;
    overlay.classList.add("hidden");

    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      handleFileIngestion(file);
      switchTab("rag");
      setTimeout(() => refreshKnowledgeDocs(), 1200);
    }
  });
}

function handleManualFileInput(event) {
  if (event && event.target && event.target.files.length > 0) {
    const file = event.target.files[0];
    handleFileIngestion(file);
    switchTab("rag");
    setTimeout(() => refreshKnowledgeDocs(), 1200);
  }
}

// ==================== HUD INTERACTION & CHAT ====================
function setupKeyboardShortcuts() {
  const input = document.getElementById("hud-input");
  if (input) {
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
      if (e.key === "Escape") {
        toggleHudMode("pet");
      }
    });
    input.addEventListener("input", () => {
      input.style.height = "auto";
      input.style.height = Math.min(input.scrollHeight, 160) + "px";
    });
  }

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
    input.style.height = "auto";
    switchStudioMode("os-tools");
    switchSubTool("clipboard");
    refreshClipboard();
    return;
  }
  if (query.startsWith("/time")) {
    input.value = "";
    input.style.height = "auto";
    switchStudioMode("os-tools");
    switchSubTool("timemachine");
    refreshTimeMachine();
    return;
  }
  if (query.startsWith("/screen")) {
    input.value = "";
    input.style.height = "auto";
    switchStudioMode("os-tools");
    switchSubTool("screen");
    runScreenPeek();
    return;
  }
  if (query.startsWith("/rag")) {
    input.value = "";
    input.style.height = "auto";
    switchStudioMode("rag");
    refreshKnowledgeDocs();
    return;
  }
  if (query.startsWith("/status") || query.startsWith("/vram")) {
    input.value = "";
    input.style.height = "auto";
    switchStudioMode("vram");
    refreshVramStats();
    return;
  }
  if (query.startsWith("/exec")) {
    const task = query.replace(/^\/exec\s*/, "");
    input.value = "";
    input.style.height = "auto";
    switchStudioMode("os-tools");
    switchSubTool("autopilot");
    if (task) {
      document.getElementById("pilot-input").value = task;
      generateCommand();
    }
    return;
  }

  // Regular Chat message
  appendMessage("user", query);
  input.value = "";
  input.style.height = "auto";
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
  if (!container) return;

  // Remove welcome hero if this is the first message
  const welcome = container.querySelector(".chat-welcome-container, .welcome-hero-box, .welcome-card");
  if (welcome) welcome.remove();

  const msgDiv = document.createElement("div");
  msgDiv.className = `msg ${sender}`;

  const avatar = sender === "user" ? "👤" : "👻";
  let formattedText = formatMarkdown(text);

  if (citations && citations.length > 0) {
    formattedText += `<div style="margin-top: 6px; font-size: 11px; color: var(--mac-accent);">📚 Источники: ${citations.join(", ")}</div>`;
  }

  msgDiv.innerHTML = `
    <div class="msg-avatar">${avatar}</div>
    <div class="msg-bubble">${formattedText}</div>
  `;

  container.appendChild(msgDiv);
  const viewport = container.closest(".chat-viewport") || container;
  viewport.scrollTop = viewport.scrollHeight;
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
      ${window.i18n ? i18n.t("thinking") : "Думаю над ответом..."}
    </div>
  `;
  container.appendChild(div);
  const viewport = container.closest(".chat-viewport") || container;
  viewport.scrollTop = viewport.scrollHeight;
  return id;
}
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
  if (!text) return "";

  // 1. Extract triple-backtick code blocks first to protect code indentation and syntax
  const codeBlocks = [];
  let processed = text.replace(/```([a-zA-Z0-9_-]*)\n?([\s\S]*?)```/g, (match, lang, code) => {
    const placeholder = `___GHOST_CODEBLOCK_${codeBlocks.length}___`;
    codeBlocks.push({ lang: lang || "code", code: code.trim() });
    return placeholder;
  });

  // 2. Escape HTML
  let html = processed
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // 3. Inline code
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // 4. Bold and italics
  html = html.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
  html = html.replace(/\*([^*]+)\*/g, "<i>$1</i>");

  // 5. Line breaks for prose
  html = html.replace(/\n/g, "<br>");

  // 6. Restore code blocks with syntax header and copy button
  codeBlocks.forEach((item, index) => {
    const placeholder = `___GHOST_CODEBLOCK_${index}___`;
    const escapedCode = item.code
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    const copyLabel = window.i18n ? i18n.t("copy_code", "📋 Копировать") : "📋 Копировать";
    const blockHtml = `
      <div class="code-block-wrapper">
        <div class="code-block-header">
          <span class="code-lang">${item.lang}</span>
          <button class="code-copy-btn" onclick="copyCodeBlock(this)">${copyLabel}</button>
        </div>
        <pre><code>${escapedCode}</code></pre>
      </div>
    `;
    html = html.replace(placeholder, blockHtml);
  });

  return html;
}

function copyCodeBlock(btn) {
  const wrapper = btn.closest(".code-block-wrapper");
  if (!wrapper) return;
  const codeEl = wrapper.querySelector("pre code");
  if (!codeEl) return;

  const codeText = codeEl.innerText;
  navigator.clipboard.writeText(codeText).then(() => {
    const originalText = btn.innerHTML;
    const copiedLabel = window.i18n ? i18n.t("copied", "✔ Скопировано!") : "✔ Скопировано!";
    btn.innerHTML = copiedLabel;
    btn.style.borderColor = "var(--mac-green)";
    btn.style.color = "var(--mac-green)";
    setTimeout(() => {
      btn.innerHTML = originalText;
      btn.style.borderColor = "";
      btn.style.color = "";
    }, 2000);
  }).catch((err) => {
    console.error("Clipboard error:", err);
  });
}

// ==================== TABS & SUB-TOOLS NAVIGATION ====================
function switchTab(tabName) {
  const subTools = ["agent", "screen", "clipboard", "autopilot", "timemachine"];
  if (subTools.includes(tabName)) {
    switchTab("os-tools");
    switchSubTool(tabName);
    return;
  }

  document.querySelectorAll(".nav-pill").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

  const targetPane = document.getElementById(`tab-${tabName}`);
  if (targetPane) targetPane.classList.add("active");

  const pills = Array.from(document.querySelectorAll(".nav-pill"));
  const match = pills.find(p => {
    const oc = p.getAttribute("onclick") || "";
    return oc.includes(`'${tabName}'`);
  });
  if (match) match.classList.add("active");

  // Load heavy stats lazily only when tab is activated
  if (tabName === "vram") refreshVramStats();
  if (tabName === "rag") refreshKnowledgeDocs();
}

function switchSubTool(toolName) {
  document.querySelectorAll(".sub-nav-pill").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".subtool-pane").forEach(p => p.classList.remove("active"));

  const targetPane = document.getElementById(`subtool-${toolName}`);
  if (targetPane) targetPane.classList.add("active");

  const pills = Array.from(document.querySelectorAll(".sub-nav-pill"));
  const match = pills.find(p => {
    const oc = p.getAttribute("onclick") || "";
    return oc.includes(`'${toolName}'`);
  });
  if (match) match.classList.add("active");

  if (toolName === "screen") runScreenPeek();
  if (toolName === "clipboard") refreshClipboard();
  if (toolName === "timemachine") refreshTimeMachine();
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

// ==================== ONBOARDING QUICK ACTIONS ====================
function triggerQuickAction(query) {
  const input = document.getElementById("hud-input");
  if (!input) return;
  input.value = query;
  handleSend();
}

// ==================== GHOSTOS v2.0 STUDIO & GHOSTCODE CONTROLLER ====================
let activeStudioMode = "chat";
let activeOpenedFile = "";

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function switchStudioMode(mode) {
  activeStudioMode = mode;
  // Update sidebar active item
  document.querySelectorAll(".sidebar-mode-item").forEach((el) => {
    el.classList.remove("active");
  });
  const navBtn = document.getElementById(`nav-mode-${mode}`);
  if (navBtn) navBtn.classList.add("active");

  // Update studio panes
  document.querySelectorAll(".studio-pane").forEach((pane) => {
    pane.classList.remove("active");
  });
  const targetPane = document.getElementById(`tab-${mode}`);
  if (targetPane) targetPane.classList.add("active");

  // Update topbar breadcrumb
  const badgeTitle = document.getElementById("topbar-mode-title");
  if (badgeTitle) {
    const titles = {
      chat: "💬 Ghost Chat",
      code: "⚡ GhostCode Studio",
      rag: "📚 Zero-DB RAG",
      "os-tools": "🛠️ OS Tools",
      vram: "🧠 Memory Juggler"
    };
    badgeTitle.innerText = titles[mode] || "GhostOS Studio";
  }

  if (mode === "code") {
    refreshWorkspaceExplorer();
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById("studio-sidebar");
  if (!sidebar) return;
  sidebar.classList.toggle("collapsed");
}

function startNewChat() {
  clearChatHistory();
  switchStudioMode("chat");
  const input = document.getElementById("hud-input");
  if (input) {
    input.value = "";
    input.focus();
  }
}

function startNewProject() {
  switchStudioMode("code");
  const input = document.getElementById("coder-task-input");
  if (input) {
    input.placeholder = "Например: Создай FastAPI проект с тестами...";
    input.focus();
  }
}

async function changeWorkspaceDir() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.choose_workspace_folder) {
    try {
      const res = await window.pywebview.api.choose_workspace_folder();
      if (res && res.status === "ok" && res.workspace) {
        refreshWorkspaceExplorer();
        showSpeechBubble(`📂 Папка: ${res.workspace.split("/").pop()}`, 2500);
      }
    } catch (err) {
      console.error("changeWorkspaceDir error:", err);
    }
  }
}

function switchCanvasTab(tabName) {
  document.querySelectorAll(".canvas-tab-btn").forEach((btn) => btn.classList.remove("active"));
  document.querySelectorAll(".canvas-tab-content").forEach((tab) => tab.classList.remove("active"));

  const btn = document.getElementById(`tab-btn-canvas-${tabName}`);
  const content = document.getElementById(`canvas-tab-${tabName}`);
  if (btn) btn.classList.add("active");
  if (content) content.classList.add("active");
}

async function refreshWorkspaceExplorer() {
  if (!window.pywebview || !window.pywebview.api || !window.pywebview.api.get_workspace_info) {
    return;
  }
  try {
    const info = await window.pywebview.api.get_workspace_info();
    const wsDisplay = document.getElementById("coder-ws-path-display");
    const sidebarWs = document.getElementById("sidebar-ws-name");
    const gitBadge = document.getElementById("coder-git-branch-badge");
    const filesContainer = document.getElementById("project-files-list");

    if (wsDisplay) wsDisplay.innerText = info.workspace || "...";
    if (sidebarWs) sidebarWs.innerText = (info.workspace ? info.workspace.split("/").pop() : "Проект");
    if (gitBadge && info.git) {
      gitBadge.innerText = `🌿 ${info.git.branch || "main"}${info.git.is_clean ? "" : " *"}`;
    }

    if (filesContainer && info.files) {
      if (info.files.length === 0) {
        filesContainer.innerHTML = `<span style="color: rgba(255,255,255,0.4); font-size: 11px;">Нет файлов в рабочей папке</span>`;
      } else {
        filesContainer.innerHTML = info.files.map((f) => {
          const isAct = f === activeOpenedFile ? "active" : "";
          const fname = f.split("/").pop();
          return `<div class="file-chip ${isAct}" onclick="openProjectFile('${f}')" title="${f}">📄 ${fname}</div>`;
        }).join("");
      }
    }

    // If active file is empty and files exist, open the first file
    if (!activeOpenedFile && info.files && info.files.length > 0) {
      const preferred = info.files.find(f => f.endsWith(".py") || f.endsWith(".js") || f.endsWith(".html") || f.endsWith(".md")) || info.files[0];
      openProjectFile(preferred);
    }
  } catch (err) {
    console.error("refreshWorkspaceExplorer error:", err);
  }
}

async function openProjectFile(filePath) {
  activeOpenedFile = filePath;
  const titleEl = document.getElementById("active-file-title");
  const editorEl = document.getElementById("active-file-editor");
  if (titleEl) titleEl.innerText = filePath.split("/").pop();

  // Highlight active chip
  document.querySelectorAll(".file-chip").forEach((chip) => {
    chip.classList.toggle("active", chip.getAttribute("title") === filePath);
  });

  if (window.pywebview && window.pywebview.api && window.pywebview.api.read_code_file) {
    try {
      const res = await window.pywebview.api.read_code_file(filePath);
      if (res && res.status === "ok") {
        if (editorEl) editorEl.value = res.content;
      } else if (res && res.error) {
        if (editorEl) editorEl.value = `// Ошибка чтения файла: ${res.error}`;
      }
    } catch (err) {
      if (editorEl) editorEl.value = `// Ошибка: ${err}`;
    }
  }
  switchCanvasTab("files");
}

async function saveActiveFileEdits() {
  if (!activeOpenedFile) {
    alert("Выберите файл для сохранения");
    return;
  }
  const editorEl = document.getElementById("active-file-editor");
  if (!editorEl) return;
  const content = editorEl.value;

  if (window.pywebview && window.pywebview.api && window.pywebview.api.save_code_file) {
    try {
      const res = await window.pywebview.api.save_code_file(activeOpenedFile, content);
      if (res && res.status === "ok") {
        showSpeechBubble(`💾 Файл сохранён (${res.bytes} байт)`, 2000);
      } else {
        alert("Ошибка при сохранении: " + (res.error || "Неизвестная ошибка"));
      }
    } catch (err) {
      alert("Ошибка при сохранении: " + err);
    }
  }
}

function triggerCoderAction(task) {
  const input = document.getElementById("coder-task-input");
  if (input) {
    input.value = task;
    handleCoderTaskSend();
  }
}

async function handleCoderTaskSend() {
  const input = document.getElementById("coder-task-input");
  if (!input) return;
  const task = input.value.trim();
  if (!task) return;

  const streamLog = document.getElementById("coder-steps-log");
  if (!streamLog) return;

  // Append user task step
  const userCard = document.createElement("div");
  userCard.className = "coder-step-card thought";
  userCard.innerHTML = `🎯 <b>Задача:</b> ${escapeHtml(task)}`;
  streamLog.appendChild(userCard);

  // Append in-progress indicator
  const progressCard = document.createElement("div");
  progressCard.className = "coder-step-card action";
  progressCard.id = "coder-running-card";
  progressCard.innerHTML = `⚙️ <i>GhostCode выполняет автономное исследование и генерацию...</i>`;
  streamLog.appendChild(progressCard);
  streamLog.scrollTop = streamLog.scrollHeight;

  input.value = "";
  setGhostMood("coding");

  if (window.pywebview && window.pywebview.api && window.pywebview.api.run_code_task) {
    try {
      const res = await window.pywebview.api.run_code_task(task);
      const runningEl = document.getElementById("coder-running-card");
      if (runningEl) runningEl.remove();

      const resultCard = document.createElement("div");
      if (res.status === "ok") {
        resultCard.className = "coder-step-card success";
        let detailHtml = `✔ <b>Выполнено:</b> ${escapeHtml(res.summary || "Задача завершена.")}`;
        if (res.files_touched && res.files_touched.length > 0) {
          detailHtml += `<br><small style="color: #6ee7b7;">Файлы: ${res.files_touched.map(f => `<code>${f}</code>`).join(", ")}</small>`;
        }
        if (res.command_output) {
          detailHtml += `<pre style="margin-top:6px;font-size:11px;background:rgba(0,0,0,0.4);padding:6px;border-radius:4px;overflow-x:auto;"><code>${escapeHtml(res.command_output.slice(0, 300))}</code></pre>`;
        }
        resultCard.innerHTML = detailHtml;

        // If diff exists, update diff viewer
        if (res.diff) {
          const diffViewer = document.getElementById("active-diff-viewer");
          if (diffViewer) diffViewer.innerText = res.diff;
          switchCanvasTab("diff");
        }
      } else {
        resultCard.className = "coder-step-card error";
        resultCard.innerHTML = `❌ <b>Ошибка:</b> ${escapeHtml(res.error || "Не удалось выполнить задачу")}`;
      }
      streamLog.appendChild(resultCard);
      streamLog.scrollTop = streamLog.scrollHeight;

      // Refresh workspace explorer
      refreshWorkspaceExplorer();
      refreshRpg();
    } catch (err) {
      const runningEl = document.getElementById("coder-running-card");
      if (runningEl) runningEl.remove();

      const errCard = document.createElement("div");
      errCard.className = "coder-step-card error";
      errCard.innerHTML = `❌ <b>Исключение:</b> ${escapeHtml(String(err))}`;
      streamLog.appendChild(errCard);
    }
  }
  setGhostMood("idle");
}

async function executeTerminalCommand(cmd) {
  const stdoutEl = document.getElementById("terminal-stdout");
  if (!stdoutEl) return;
  stdoutEl.innerHTML += `\n<span style="color:#60a5fa;">zsh $ ${escapeHtml(cmd)}</span>\n`;
  stdoutEl.scrollTop = stdoutEl.scrollHeight;

  if (window.pywebview && window.pywebview.api && window.pywebview.api.run_studio_terminal) {
    try {
      const res = await window.pywebview.api.run_studio_terminal(cmd);
      if (res && res.output) {
        stdoutEl.innerHTML += `${escapeHtml(res.output)}\n`;
      } else if (res && res.error) {
        stdoutEl.innerHTML += `<span style="color:#ef4444;">${escapeHtml(res.error)}</span>\n`;
      }
    } catch (err) {
      stdoutEl.innerHTML += `<span style="color:#ef4444;">${escapeHtml(String(err))}</span>\n`;
    }
    stdoutEl.scrollTop = stdoutEl.scrollHeight;
  }
}

function setupStudioListeners() {
  const terminalInput = document.getElementById("terminal-cmd-input");
  if (terminalInput) {
    terminalInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const cmd = terminalInput.value.trim();
        if (cmd) {
          terminalInput.value = "";
          executeTerminalCommand(cmd);
        }
      }
    });
  }

  const coderInput = document.getElementById("coder-task-input");
  if (coderInput) {
    coderInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleCoderTaskSend();
      }
    });
  }
}

