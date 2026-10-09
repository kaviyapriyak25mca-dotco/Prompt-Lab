/**
 * Academic Document Retrieval Agent - Client Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const uploadProgress = document.getElementById("uploadProgress");
  const docList = document.getElementById("docList");
  const statDocsCount = document.getElementById("statDocsCount");
  const statChunksCount = document.getElementById("statChunksCount");
  const docCountBadge = document.getElementById("docCountBadge");

  const queryInput = document.getElementById("queryInput");
  const btnSubmitQuery = document.getElementById("btnSubmitQuery");
  const placeholderState = document.getElementById("placeholderState");
  const loadingState = document.getElementById("loadingState");
  const answerCard = document.getElementById("answerCard");

  const primaryDocTitle = document.getElementById("primaryDocTitle");
  const primaryDocYear = document.getElementById("primaryDocYear");
  const engineModeBadge = document.getElementById("engineModeBadge");
  const conflictBanner = document.getElementById("conflictBanner");
  const conflictTopic = document.getElementById("conflictTopic");
  const conflictActiveText = document.getElementById("conflictActiveText");
  const conflictOlderText = document.getElementById("conflictOlderText");
  const conflictResolutionText = document.getElementById("conflictResolutionText");

  const answerText = document.getElementById("answerText");
  const validationStatusText = document.getElementById("validationStatusText");
  const validationScoreVal = document.getElementById("validationScoreVal");
  const meterFill = document.getElementById("meterFill");
  const totalClaimsCount = document.getElementById("totalClaimsCount");
  const claimsList = document.getElementById("claimsList");
  const citationsGrid = document.getElementById("citationsGrid");

  const btnToggleRawContext = document.getElementById("btnToggleRawContext");
  const rawChunksContainer = document.getElementById("rawChunksContainer");
  const rawChunksList = document.getElementById("rawChunksList");

  const btnSettingsToggle = document.getElementById("btnSettingsToggle");
  const settingsPanel = document.getElementById("settingsPanel");
  const geminiKeyInput = document.getElementById("geminiKeyInput");
  const topKSlider = document.getElementById("topKSlider");
  const topKVal = document.getElementById("topKVal");
  const btnSaveSettings = document.getElementById("btnSaveSettings");
  const btnResetCorpus = document.getElementById("btnResetCorpus");

  const chunkModal = document.getElementById("chunkModal");
  const modalDocTitle = document.getElementById("modalDocTitle");
  const modalChunksBody = document.getElementById("modalChunksBody");
  const btnCloseModal = document.getElementById("btnCloseModal");

  // State
  let geminiApiKey = localStorage.getItem("geminiApiKey") || "";
  let topK = parseInt(localStorage.getItem("topK") || "5", 10);
  if (geminiKeyInput) geminiKeyInput.value = geminiApiKey;
  if (topKSlider) topKSlider.value = topK;
  if (topKVal) topKVal.textContent = topK;

  // Initialize
  fetchDocuments();

  // Settings Handlers
  btnSettingsToggle.addEventListener("click", () => {
    settingsPanel.classList.toggle("hidden");
  });

  topKSlider.addEventListener("input", (e) => {
    topKVal.textContent = e.target.value;
  });

  btnSaveSettings.addEventListener("click", () => {
    geminiApiKey = geminiKeyInput.value.trim();
    topK = parseInt(topKSlider.value, 10);
    localStorage.setItem("geminiApiKey", geminiApiKey);
    localStorage.setItem("topK", topK);
    settingsPanel.classList.add("hidden");
    showNotification("Settings updated successfully!");
  });

  btnResetCorpus.addEventListener("click", async () => {
    if (!confirm("Reset document repository to default sample academic files?")) return;
    try {
      const res = await fetch("/api/reset", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        showNotification("Repository reset to default academic documents!");
        fetchDocuments();
      }
    } catch (err) {
      alert("Error resetting repository: " + err.message);
    }
  });

  // Upload Handlers
  dropzone.addEventListener("click", () => fileInput.click());
  
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
      uploadFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      uploadFile(e.target.files[0]);
    }
  });

  async function uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    uploadProgress.classList.remove("hidden");

    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        showNotification(`Indexed ${file.name} (${data.chunks_count} chunks)`);
        fetchDocuments();
      } else {
        alert("Upload error: " + (data.error || "Failed to parse document"));
      }
    } catch (err) {
      alert("Network error while uploading: " + err.message);
    } finally {
      uploadProgress.classList.add("hidden");
      fileInput.value = "";
    }
  }

  // Fetch Documents
  async function fetchDocuments() {
    try {
      const res = await fetch("/api/documents");
      const data = await res.json();
      if (data.success) {
        renderDocumentList(data.documents);
        statDocsCount.textContent = `${data.documents.length} Documents`;
        docCountBadge.textContent = `${data.documents.length} Files`;
        
        const totalChunks = data.documents.reduce((acc, d) => acc + d.total_chunks, 0);
        statChunksCount.textContent = totalChunks;
      }
    } catch (err) {
      console.error("Failed to fetch documents", err);
    }
  }

  function renderDocumentList(documents) {
    docList.innerHTML = "";
    documents.forEach((doc) => {
      const card = document.createElement("div");
      card.className = "doc-card";

      const ext = doc.file_type.toLowerCase();
      let typeClass = "doc-type-pdf";
      if (ext === "docx") typeClass = "doc-type-docx";
      if (ext === "txt") typeClass = "doc-type-txt";

      card.innerHTML = `
        <div class="doc-card-header">
          <span class="doc-type-pill ${typeClass}">${doc.file_type}</span>
          <span class="doc-year-pill">AY ${doc.academic_year}</span>
        </div>
        <div class="doc-card-name" title="${doc.filename}">${doc.filename}</div>
        <div class="doc-card-meta">
          <span>${doc.total_chunks} chunks • ${doc.total_pages} pg</span>
          <span style="color: ${doc.is_revision ? '#38bdf8' : '#94a3b8'}">${doc.is_revision ? 'Revised' : 'Standard'}</span>
        </div>
      `;

      card.addEventListener("click", () => openDocChunksModal(doc.filename));
      docList.appendChild(card);
    });
  }

  // Modal Handlers
  async function openDocChunksModal(docName) {
    modalDocTitle.textContent = `Extracted Text Chunks: ${docName}`;
    modalChunksBody.innerHTML = `<div class="spinner-sm"></div> Loading chunks...`;
    chunkModal.classList.remove("hidden");

    try {
      const res = await fetch(`/api/chunks?doc_name=${encodeURIComponent(docName)}`);
      const data = await res.json();
      if (data.success) {
        modalChunksBody.innerHTML = "";
        data.chunks.forEach((c) => {
          const div = document.createElement("div");
          div.className = "raw-chunk-item";
          div.innerHTML = `
            <div class="raw-chunk-header">
              <span>Page ${c.page_number} (${c.section_title})</span>
              <span>ID: ${c.chunk_id}</span>
            </div>
            <div class="raw-chunk-text">${escapeHtml(c.text)}</div>
          `;
          modalChunksBody.appendChild(div);
        });
      }
    } catch (err) {
      modalChunksBody.textContent = "Failed to load chunks: " + err.message;
    }
  }

  btnCloseModal.addEventListener("click", () => {
    chunkModal.classList.add("hidden");
  });

  chunkModal.addEventListener("click", (e) => {
    if (e.target === chunkModal) chunkModal.classList.add("hidden");
  });

  // Preset Chips Handlers
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      queryInput.value = q;
      handleQuerySubmit();
    });
  });

  // Query Submit Handler
  btnSubmitQuery.addEventListener("click", handleQuerySubmit);
  queryInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleQuerySubmit();
    }
  });

  btnToggleRawContext.addEventListener("click", () => {
    rawChunksContainer.classList.toggle("hidden");
  });

  async function handleQuerySubmit() {
    const query = queryInput.value.trim();
    if (!query) return;

    placeholderState.classList.add("hidden");
    answerCard.classList.add("hidden");
    loadingState.classList.remove("hidden");

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          top_k: topK,
          gemini_api_key: geminiApiKey || undefined
        })
      });

      const json = await res.json();
      if (!json.success) {
        throw new Error(json.error || "Failed to retrieve answer");
      }

      renderAnswer(json.data);
    } catch (err) {
      alert("Error querying agent: " + err.message);
    } finally {
      loadingState.classList.add("hidden");
    }
  }

  function renderAnswer(data) {
    answerCard.classList.remove("hidden");

    // Authoritative Source Header
    const decision = data.source_decision || {};
    primaryDocTitle.textContent = decision.primary_document || "Corpus Query";
    primaryDocYear.textContent = decision.primary_academic_year ? `AY ${decision.primary_academic_year}` : "";
    engineModeBadge.textContent = data.engine_mode || "Grounded Fact Engine";

    // Conflict Resolution Banner
    if (decision.conflict_detected && decision.conflict_details) {
      const cd = decision.conflict_details;
      conflictBanner.classList.remove("hidden");
      conflictTopic.textContent = `⚠️ Active Policy Conflict Resolved: ${cd.topic}`;
      conflictActiveText.textContent = cd.latest_policy;
      conflictOlderText.textContent = cd.older_policy;
      conflictResolutionText.innerHTML = `<strong>Legal Precedence:</strong> ${escapeHtml(cd.resolution)}`;
    } else {
      conflictBanner.classList.add("hidden");
    }

    // Answer Body
    answerText.innerHTML = formatMarkdown(data.answer);

    // Validation Meter & Claims
    const val = data.validation || {};
    const score = val.grounding_score || 0;
    validationScoreVal.textContent = `${score}%`;
    meterFill.style.width = `${score}%`;
    validationStatusText.textContent = val.status || "Grounding Evaluated";

    if (score >= 80) {
      meterFill.style.background = "linear-gradient(90deg, #10b981, #34d399)";
      validationStatusText.style.color = "#10b981";
    } else if (score >= 60) {
      meterFill.style.background = "linear-gradient(90deg, #f59e0b, #fbbf24)";
      validationStatusText.style.color = "#f59e0b";
    } else {
      meterFill.style.background = "linear-gradient(90deg, #ef4444, #f87171)";
      validationStatusText.style.color = "#ef4444";
    }

    // Claims Breakdown
    const claims = val.claims_breakdown || [];
    totalClaimsCount.textContent = claims.length;
    claimsList.innerHTML = "";

    claims.forEach((c) => {
      const claimDiv = document.createElement("div");
      let borderClass = "claim-verified";
      let statusPill = `<span class="claim-status-pill status-verified">VERIFIED</span>`;

      if (c.status === "PARTIALLY_SUPPORTED") {
        borderClass = "claim-partial";
        statusPill = `<span class="claim-status-pill status-partial">PARTIAL</span>`;
      } else if (c.status === "UNSUPPORTED_OR_MISSING") {
        borderClass = "claim-unsupported";
        statusPill = `<span class="claim-status-pill status-unsupported">MISSING/UNVERIFIED</span>`;
      }

      claimDiv.className = `claim-item ${borderClass}`;
      claimDiv.innerHTML = `
        <div class="claim-text">${escapeHtml(c.claim_text)}</div>
        <div class="claim-meta">
          <span>${c.supporting_doc} (p. ${c.page_number})</span>
          ${statusPill}
        </div>
      `;
      claimsList.appendChild(claimDiv);
    });

    // Citations Cards
    citationsGrid.innerHTML = "";
    (data.citations || []).forEach((cite) => {
      const card = document.createElement("div");
      card.className = "citation-card";
      card.innerHTML = `
        <div class="citation-header">
          <span class="citation-doc-name" title="${cite.document}">${cite.document}</span>
          <span class="citation-page-badge">Page ${cite.page}</span>
        </div>
        <div class="citation-excerpt">"${escapeHtml(cite.excerpt)}"</div>
        <div class="citation-score-bar">
          <span>${cite.section || 'General'}</span>
          <span>Score: ${(cite.relevance_score || 0).toFixed(2)}</span>
        </div>
      `;
      citationsGrid.appendChild(card);
    });

    // Raw Chunks Inspector
    rawChunksList.innerHTML = "";
    (data.retrieved_chunks || []).forEach((c) => {
      const item = document.createElement("div");
      item.className = "raw-chunk-item";
      item.innerHTML = `
        <div class="raw-chunk-header">
          <span>${c.doc_name} (Page ${c.page_number})</span>
          <span>Hybrid: ${c.score.toFixed(3)} | Sem: ${c.semantic_score.toFixed(3)} | Lex: ${c.keyword_score.toFixed(3)}</span>
        </div>
        <div class="raw-chunk-text">${escapeHtml(c.text)}</div>
      `;
      rawChunksList.appendChild(item);
    });

    // Scroll into view
    answerCard.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function formatMarkdown(text) {
    if (!text) return "";
    let html = escapeHtml(text);

    // Blockquote
    html = html.replace(/^\&gt;\s+(.*$)/gim, '<blockquote>$1</blockquote>');
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h4 style="margin: 12px 0 6px;">$1</h4>');
    html = html.replace(/^## (.*$)/gim, '<h3 style="margin: 14px 0 8px;">$1</h3>');
    // Bullet points
    html = html.replace(/^\-\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gms, '<ul>$1</ul>');
    // Double newlines to paragraphs
    html = html.replace(/\n\n/g, '<p></p>');
    return html;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function showNotification(msg) {
    const toast = document.createElement("div");
    toast.style.position = "fixed";
    toast.style.bottom = "24px";
    toast.style.right = "24px";
    toast.style.background = "linear-gradient(135deg, #4f46e5, #0ea5e9)";
    toast.style.color = "white";
    toast.style.padding = "10px 18px";
    toast.style.borderRadius = "8px";
    toast.style.boxShadow = "0 10px 25px rgba(0,0,0,0.5)";
    toast.style.fontSize = "0.85rem";
    toast.style.fontWeight = "600";
    toast.style.zIndex = "999";
    toast.style.transition = "all 0.3s ease";
    toast.textContent = msg;

    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(10px)";
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
});
