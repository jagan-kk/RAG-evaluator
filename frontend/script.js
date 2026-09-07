const API_BASE = "http://127.0.0.1:8000";

// ──────────────────────────────────────────
// Tab Navigation
// ──────────────────────────────────────────
document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(`${btn.dataset.tab}-tab`).classList.add("active");
    });
});

// ──────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────
function $(id) { return document.getElementById(id); }

function escapeHtml(str) {
    const d = document.createElement("div");
    d.textContent = str;
    return d.innerHTML;
}

function show(el) { el.classList.remove("hidden"); }
function hide(el) { el.classList.add("hidden"); }

// ──────────────────────────────────────────
// PDF Upload
// ──────────────────────────────────────────
const uploadArea = $("upload-area");
const pdfInput = $("pdf-input");

uploadArea.addEventListener("click", () => pdfInput.click());
uploadArea.addEventListener("dragover", e => { e.preventDefault(); uploadArea.classList.add("dragover"); });
uploadArea.addEventListener("dragleave", () => uploadArea.classList.remove("dragover"));
uploadArea.addEventListener("drop", e => {
    e.preventDefault();
    uploadArea.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
        pdfInput.files = e.dataTransfer.files;
        uploadPDF(e.dataTransfer.files[0]);
    }
});
pdfInput.addEventListener("change", () => { if (pdfInput.files.length) uploadPDF(pdfInput.files[0]); });

async function uploadPDF(file) {
    hide($("upload-placeholder"));
    hide($("error-message"));
    hide($("upload-result"));
    show($("upload-progress"));
    $("progress-fill").style.width = "20%";
    $("progress-text").textContent = "Uploading document...";

    const formData = new FormData();
    formData.append("file", file);

    try {
        $("progress-fill").style.width = "50%";
        $("progress-text").textContent = "Processing & embedding...";

        const res = await fetch(`${API_BASE}/documents/uploads`, { method: "POST", body: formData });
        if (!res.ok) throw new Error(`Upload failed (${res.status})`);
        const data = await res.json();

        $("progress-fill").style.width = "100%";
        $("progress-text").textContent = "Done";

        await new Promise(r => setTimeout(r, 350));
        hide($("upload-progress"));

        $("result-filename").textContent = data.file_name;
        $("result-pages").textContent = data.pages;
        $("result-chunks").textContent = data.chunks;
        $("result-embeddings").textContent = data.embeddings;
        show($("upload-result"));

        $("chat-input").disabled = false;
        $("send-btn").disabled = false;
        $("chat-status-badge").textContent = "Online";
        $("chat-status-badge").className = "badge online";

        clearChat();
    } catch (err) {
        hide($("upload-progress"));
        show($("upload-placeholder"));
        $("error-message").textContent = err.message;
        show($("error-message"));
    }
}

$("clear-btn").addEventListener("click", () => {
    pdfInput.value = "";
    hide($("upload-result"));
    hide($("error-message"));
    show($("upload-placeholder"));
    $("chat-input").disabled = true;
    $("send-btn").disabled = true;
    $("chat-status-badge").textContent = "Offline";
    $("chat-status-badge").className = "badge";
    clearChat();
});

// ──────────────────────────────────────────
// Chat
// ──────────────────────────────────────────
const chatMessages = $("chat-messages");

$("send-btn").addEventListener("click", sendMessage);
$("chat-input").addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

function clearChat() {
    chatMessages.innerHTML = `
        <div class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="empty-icon">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <p>Ask anything about your document</p>
        </div>`;
}

function addMessage(role, text) {
    const emptyState = chatMessages.querySelector(".empty-state");
    if (emptyState) emptyState.remove();

    const div = document.createElement("div");
    div.className = `message ${role}`;
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

async function sendMessage() {
    const input = $("chat-input");
    const question = input.value.trim();
    if (!question) return;

    input.value = "";
    addMessage("user", question);
    const assistantMsg = addMessage("assistant thinking", "Thinking...");

    try {
        const res = await fetch(`${API_BASE}/chat/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question })
        });

        if (!res.ok) throw new Error(`Chat failed (${res.status})`);

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        assistantMsg.textContent = "";
        assistantMsg.classList.remove("thinking");

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            assistantMsg.textContent += decoder.decode(value, { stream: true });
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    } catch (err) {
        assistantMsg.textContent = `Error: ${err.message}`;
        assistantMsg.classList.remove("thinking");
    }
}

// ──────────────────────────────────────────
// Evaluation
// ──────────────────────────────────────────
$("run-eval-btn").addEventListener("click", runEvaluation);

async function runEvaluation() {
    const k = parseInt($("k-value").value) || 5;

    hide($("eval-error-message"));
    hide($("eval-results"));
    show($("eval-progress"));
    $("eval-progress-fill").style.width = "20%";
    $("eval-progress-text").textContent = "Running retrieval evaluation...";

    try {
        $("eval-progress-fill").style.width = "50%";
        const res = await fetch(`${API_BASE}/evaluation/retrieval?k=${k}`);

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || `Evaluation failed (${res.status})`);
        }

        $("eval-progress-fill").style.width = "80%";
        $("eval-progress-text").textContent = "Computing metrics...";

        const data = await res.json();

        $("eval-progress-fill").style.width = "100%";
        $("eval-progress-text").textContent = "Done";

        await new Promise(r => setTimeout(r, 300));
        hide($("eval-progress"));
        renderEvalResults(data.results, data.averages);
        show($("eval-results"));
    } catch (err) {
        hide($("eval-progress"));
        $("eval-error-message").textContent = err.message;
        show($("eval-error-message"));
    }
}

function renderEvalResults(results, averages) {
    const metrics = [
        { key: "hit_rate", label: "Hit Rate" },
        { key: "recall", label: "Recall" },
        { key: "precision", label: "Precision" },
        { key: "reciprocal_rank", label: "MRR" }
    ];

    $("metrics-summary").innerHTML = metrics.map(m => {
        const val = averages[m.key];
        const pct = Math.round(val * 100);
        return `
            <div class="metric-card">
                <span class="label">${m.label}</span>
                <span class="value">${val.toFixed(3)}</span>
                <div class="bar"><div class="bar-fill" style="width:${pct}%"></div></div>
            </div>`;
    }).join("");

    $("metrics-tbody").innerHTML = results.map(r => `
        <tr>
            <td>${escapeHtml(r.question)}</td>
            <td>${r.hit_rate.toFixed(3)}</td>
            <td>${r.recall.toFixed(3)}</td>
            <td>${r.precision.toFixed(3)}</td>
            <td>${r.reciprocal_rank.toFixed(3)}</td>
        </tr>`).join("");
}

// ──────────────────────────────────────────
// Manual Dataset Entry
// ──────────────────────────────────────────
$("add-entry-btn").addEventListener("click", addEntry);
document.querySelectorAll(".remove-entry").forEach(btn => btn.addEventListener("click", removeEntry));

function addEntry() {
    const row = document.createElement("div");
    row.className = "entry-row";
    row.innerHTML = `
        <div class="entry-fields">
            <input type="text" class="input-field" placeholder="Question">
            <textarea class="input-field textarea-field" placeholder="Relevant chunks (one per line)"></textarea>
        </div>
        <button class="btn btn-ghost btn-sm remove-entry">✕</button>`;
    row.querySelector(".remove-entry").addEventListener("click", removeEntry);
    $("dataset-entries").appendChild(row);
}

function removeEntry() {
    this.closest(".entry-row").remove();
}