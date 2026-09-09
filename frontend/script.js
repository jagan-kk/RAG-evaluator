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
        $("result-chunks").textContent = data.new_chunks;
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

    const provider = $("chat-provider").value;

    input.value = "";
    addMessage("user", question);
    const assistantMsg = addMessage("assistant thinking", "Thinking...");

    try {
        const res = await fetch(`${API_BASE}/chat/?provider=${provider}`, {
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
// Faithfulness Evaluation
// ──────────────────────────────────────────
$("run-faith-btn").addEventListener("click", runFaithfulness);

async function runFaithfulness() {
    const k = parseInt($("k-value").value) || 5;
    const provider = $("faith-provider").value;
    const start = parseInt($("faith-start").value) || 0;
    const end = parseInt($("faith-end").value) || 10;

    hide($("faith-error-message"));
    hide($("faith-results"));
    show($("faith-progress"));
    $("faith-progress-fill").style.width = "10%";
    $("faith-progress-text").textContent = `Starting faithfulness evaluation (questions ${start}-${end - 1}) with ${provider === "ollama" ? "Ollama (local)" : "OpenRouter (cloud)"}...`;

    try {
        $("faith-progress-fill").style.width = "30%";
        $("faith-progress-text").textContent = "Generating answers and evaluating faithfulness...";

        const res = await fetch(`${API_BASE}/evaluation/faithfulness?k=${k}&provider=${provider}&start=${start}&end=${end}`);

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || `Evaluation failed (${res.status})`);
        }

        $("faith-progress-fill").style.width = "80%";
        $("faith-progress-text").textContent = "Computing results...";

        const data = await res.json();

        $("faith-progress-fill").style.width = "100%";
        $("faith-progress-text").textContent = "Done";

        await new Promise(r => setTimeout(r, 300));
        hide($("faith-progress"));
        renderFaithResults(data.results);
        show($("faith-results"));
    } catch (err) {
        hide($("faith-progress"));
        $("faith-error-message").textContent = err.message;
        show($("faith-error-message"));
    }
}

function renderFaithResults(results) {
    $("faith-tbody").innerHTML = results.map(r => `
        <tr>
            <td>${escapeHtml(r.question)}</td>
            <td>${escapeHtml(r.answer.substring(0, 100))}${r.answer.length > 100 ? '...' : ''}</td>
            <td>${r.faithfulness !== null ? r.faithfulness.toFixed(3) : 'Error'}</td>
        </tr>`).join("");
}

// ──────────────────────────────────────────
// Relevance Evaluation
// ──────────────────────────────────────────
$("run-rel-btn").addEventListener("click", runRelevance);

async function runRelevance() {
    const k = parseInt($("k-value").value) || 5;
    const provider = $("rel-provider").value;
    const start = parseInt($("rel-start").value) || 0;
    const end = parseInt($("rel-end").value) || 10;

    hide($("rel-error-message"));
    hide($("rel-results"));
    show($("rel-progress"));
    $("rel-progress-fill").style.width = "10%";
    $("rel-progress-text").textContent = `Starting relevance evaluation (questions ${start}-${end - 1}) with ${provider === "ollama" ? "Ollama (local)" : "OpenRouter (cloud)"}...`;

    try {
        $("rel-progress-fill").style.width = "30%";
        $("rel-progress-text").textContent = "Generating answers and evaluating relevance...";

        const res = await fetch(`${API_BASE}/evaluation/relevance?k=${k}&provider=${provider}&start=${start}&end=${end}`);

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || `Evaluation failed (${res.status})`);
        }

        $("rel-progress-fill").style.width = "80%";
        $("rel-progress-text").textContent = "Computing results...";

        const data = await res.json();

        $("rel-progress-fill").style.width = "100%";
        $("rel-progress-text").textContent = "Done";

        await new Promise(r => setTimeout(r, 300));
        hide($("rel-progress"));
        renderRelResults(data.results);
        show($("rel-results"));
    } catch (err) {
        hide($("rel-progress"));
        $("rel-error-message").textContent = err.message;
        show($("rel-error-message"));
    }
}

function renderRelResults(results) {
    $("rel-tbody").innerHTML = results.map(r => {
        if (r.relevance) {
            return `
        <tr>
            <td>${escapeHtml(r.question)}</td>
            <td>${escapeHtml(r.answer.substring(0, 80))}${r.answer.length > 80 ? '...' : ''}</td>
            <td>${r.relevance.score.toFixed(2)}</td>
            <td>${escapeHtml(r.relevance.reason)}</td>
        </tr>`;
        } else {
            return `
        <tr>
            <td>${escapeHtml(r.question)}</td>
            <td>${escapeHtml(r.answer.substring(0, 80))}${r.answer.length > 80 ? '...' : ''}</td>
            <td>Error</td>
            <td>${escapeHtml(r.answer)}</td>
        </tr>`;
        }
    }).join("");
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