/**
 * =============================================================================
 * AI-Powered Blog Platform - Client-Side JavaScript
 * Author: Codec Technologies Industrial Training Project
 * Features: Live Markdown Preview, AI Generator, SEO Assistant, CRUD operations.
 * =============================================================================
 */

document.addEventListener("DOMContentLoaded", function () {
  initDashboard();
  initEditor();
});

/* =============================================================================
   1. Toast Notification Utility
   ============================================================================= */

function showToast(message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  const icons = {
    success: "✅",
    error: "❌",
    info: "ℹ️"
  };

  toast.innerHTML = `
    <span>${icons[type] || "ℹ️"}</span>
    <div style="flex: 1;">${escapeHtml(message)}</div>
    <button style="background:none; border:none; cursor:pointer; color:#94a3b8; font-size:1.1rem;" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.transition = "opacity 0.3s ease, transform 0.3s ease";
      toast.style.opacity = "0";
      toast.style.transform = "translateX(50px)";
      setTimeout(() => toast.remove(), 300);
    }
  }, 4500);
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}


/* =============================================================================
   2. Client-Side Markdown Parser (Zero-Dependency)
   ============================================================================= */

function parseMarkdown(md) {
  if (!md) return "";

  // Step 1: Escape HTML to prevent script injection
  let safe = escapeHtml(md);

  // Step 2: Code blocks ```lang ... ```
  safe = safe.replace(/```([a-zA-Z0-9_-]*)\r?\n([\s\S]*?)```/g, function (match, lang, code) {
    return `<pre class="code-box"><code>${code.trim()}</code></pre>`;
  });

  // Step 3: Parse line by line
  const lines = safe.split(/\r?\n/);
  const output = [];
  let inUl = false;
  let inOl = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (trimmed.startsWith("#### ")) {
      if (inUl) { output.push("</ul>"); inUl = false; }
      if (inOl) { output.push("</ol>"); inOl = false; }
      output.push(`<h4>${trimmed.substring(5)}</h4>`);
    } else if (trimmed.startsWith("### ")) {
      if (inUl) { output.push("</ul>"); inUl = false; }
      if (inOl) { output.push("</ol>"); inOl = false; }
      output.push(`<h3>${trimmed.substring(4)}</h3>`);
    } else if (trimmed.startsWith("## ")) {
      if (inUl) { output.push("</ul>"); inUl = false; }
      if (inOl) { output.push("</ol>"); inOl = false; }
      output.push(`<h2>${trimmed.substring(3)}</h2>`);
    } else if (trimmed.startsWith("# ")) {
      if (inUl) { output.push("</ul>"); inUl = false; }
      if (inOl) { output.push("</ol>"); inOl = false; }
      output.push(`<h1>${trimmed.substring(2)}</h1>`);
    } else if (trimmed.startsWith("&gt; ") || trimmed.startsWith("> ")) {
      if (inUl) { output.push("</ul>"); inUl = false; }
      if (inOl) { output.push("</ol>"); inOl = false; }
      const quoteContent = trimmed.startsWith("&gt; ") ? trimmed.substring(5) : trimmed.substring(2);
      output.push(`<blockquote class="blog-quote">${quoteContent}</blockquote>`);
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      if (inOl) { output.push("</ol>"); inOl = false; }
      if (!inUl) { output.push('<ul class="blog-list">'); inUl = true; }
      output.push(`<li>${trimmed.substring(2)}</li>`);
    } else if (/^\d+\.\s/.test(trimmed)) {
      if (inUl) { output.push("</ul>"); inUl = false; }
      if (!inOl) { output.push('<ol class="blog-ordered-list">'); inOl = true; }
      output.push(`<li>${trimmed.replace(/^\d+\.\s/, '')}</li>`);
    } else if (trimmed === "---" || trimmed === "***" || trimmed === "___") {
      if (inUl) { output.push("</ul>"); inUl = false; }
      if (inOl) { output.push("</ol>"); inOl = false; }
      output.push('<hr class="divider">');
    } else if (trimmed === "") {
      if (inUl) { output.push("</ul>"); inUl = false; }
      if (inOl) { output.push("</ol>"); inOl = false; }
      output.push("");
    } else if (trimmed.startsWith('<pre class="code-box">')) {
      if (inUl) { output.push("</ul>"); inUl = false; }
      if (inOl) { output.push("</ol>"); inOl = false; }
      output.push(trimmed);
    } else {
      if (inUl) { output.push("</ul>"); inUl = false; }
      if (inOl) { output.push("</ol>"); inOl = false; }
      output.push(`<p>${trimmed}</p>`);
    }
  }

  if (inUl) output.push("</ul>");
  if (inOl) output.push("</ol>");

  let htmlStr = output.join("\n");

  // Inline formatting
  htmlStr = htmlStr.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  htmlStr = htmlStr.replace(/\*(.+?)\*/g, "<em>$1</em>");
  htmlStr = htmlStr.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
  htmlStr = htmlStr.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="blog-link">$1</a>');

  return htmlStr;
}


/* =============================================================================
   3. Dashboard Logic (Filtering, Search, Deletion)
   ============================================================================= */

function initDashboard() {
  const cardsContainer = document.getElementById("blog-cards-container");
  if (!cardsContainer) return; // Not on dashboard page

  const filterButtons = document.querySelectorAll(".tab-btn");
  const searchInput = document.getElementById("search-input");
  let currentFilter = "all";

  // Filter tabs click
  filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      filterButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentFilter = btn.dataset.filter || "all";
      filterCards();
    });
  });

  // Search input typing
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      filterCards();
    });
  }

  function filterCards() {
    const query = (searchInput ? searchInput.value : "").toLowerCase().trim();
    const cards = document.querySelectorAll(".blog-card");
    let visibleCount = 0;

    cards.forEach(card => {
      const status = card.dataset.status || "";
      const title = (card.dataset.title || "").toLowerCase();
      const topic = (card.dataset.topic || "").toLowerCase();

      const matchesStatus = (currentFilter === "all") || (status === currentFilter);
      const matchesSearch = !query || title.includes(query) || topic.includes(query);

      if (matchesStatus && matchesSearch) {
        card.style.display = "flex";
        visibleCount++;
      } else {
        card.style.display = "none";
      }
    });

    const noResultsMsg = document.getElementById("no-results-message");
    if (noResultsMsg) {
      noResultsMsg.style.display = (visibleCount === 0 && cards.length > 0) ? "block" : "none";
    }
  }

  // Blog Deletion with Confirmation Modal
  document.addEventListener("click", function (e) {
    if (e.target && e.target.classList.contains("btn-delete-blog")) {
      const blogId = e.target.dataset.id;
      const blogTitle = e.target.dataset.title || "this blog post";

      openDeleteModal(blogId, blogTitle);
    }
  });
}

function openDeleteModal(blogId, title) {
  // Remove existing modal if any
  const existing = document.getElementById("delete-modal");
  if (existing) existing.remove();

  const modal = document.createElement("div");
  modal.id = "delete-modal";
  modal.className = "modal-overlay";
  modal.innerHTML = `
    <div class="modal-card">
      <h3>Delete Blog Post</h3>
      <p>Are you sure you want to delete <strong>"${escapeHtml(title)}"</strong>? This action cannot be undone.</p>
      <div class="modal-actions">
        <button class="btn btn-outline" id="cancel-delete-btn">Cancel</button>
        <button class="btn btn-danger" id="confirm-delete-btn">Yes, Delete</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  document.getElementById("cancel-delete-btn").addEventListener("click", () => modal.remove());

  document.getElementById("confirm-delete-btn").addEventListener("click", async () => {
    const btn = document.getElementById("confirm-delete-btn");
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner"></span> Deleting...`;

    try {
      const res = await fetch(`/api/blogs/${blogId}`, { method: "DELETE" });
      const data = await res.json();
      if (res.ok && data.status === "success") {
        showToast("Blog deleted successfully", "success");
        modal.remove();
        // Remove card from UI or reload
        const card = document.querySelector(`.blog-card[data-id="${blogId}"]`);
        if (card) {
          card.style.transition = "all 0.3s ease";
          card.style.transform = "scale(0.9)";
          card.style.opacity = "0";
          setTimeout(() => {
            card.remove();
            window.location.reload();
          }, 300);
        } else {
          window.location.reload();
        }
      } else {
        showToast(data.message || "Failed to delete post", "error");
        modal.remove();
      }
    } catch (err) {
      showToast("Server error while deleting blog.", "error");
      modal.remove();
    }
  });
}


/* =============================================================================
   4. Blog Editor Logic
   ============================================================================= */

function initEditor() {
  const contentInput = document.getElementById("editor-content");
  if (!contentInput) return; // Not on editor page

  const titleInput = document.getElementById("editor-title");
  const topicInput = document.getElementById("blog-topic");
  const toneSelect = document.getElementById("blog-tone");
  const lengthSelect = document.getElementById("blog-length");
  const previewPane = document.getElementById("editor-preview");
  const wordCountSpan = document.getElementById("word-count");
  const readTimeSpan = document.getElementById("read-time");

  // SEO Elements
  const seoTitleInput = document.getElementById("seo-title");
  const seoDescInput = document.getElementById("seo-description");
  const seoKeywordsInput = document.getElementById("seo-keywords");
  const seoTitleCount = document.getElementById("seo-title-count");
  const seoDescCount = document.getElementById("seo-desc-count");
  const googlePreviewTitle = document.getElementById("google-preview-title");
  const googlePreviewDesc = document.getElementById("google-preview-desc");

  // Live Preview & Word Counter update function
  function updatePreviewAndCounters() {
    const text = contentInput.value;
    previewPane.innerHTML = parseMarkdown(text);

    // Count words
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    if (wordCountSpan) wordCountSpan.textContent = `${words} words`;

    // Estimate reading time (~200 wpm)
    const minutes = Math.max(1, Math.round(words / 200));
    if (readTimeSpan) readTimeSpan.textContent = `~${minutes} min read`;
  }

  // Update SEO snippet
  function updateSeoSnippet() {
    const titleVal = (seoTitleInput && seoTitleInput.value.trim()) || (titleInput.value.trim()) || "Your Blog Title";
    const descVal = (seoDescInput && seoDescInput.value.trim()) || "Your blog post meta description will appear here as a Google search snippet preview.";

    if (googlePreviewTitle) googlePreviewTitle.textContent = titleVal;
    if (googlePreviewDesc) googlePreviewDesc.textContent = descVal;

    if (seoTitleCount && seoTitleInput) {
      seoTitleCount.textContent = `${seoTitleInput.value.length}/60`;
      seoTitleCount.style.color = seoTitleInput.value.length > 60 ? "#ef4444" : "#94a3b8";
    }
    if (seoDescCount && seoDescInput) {
      seoDescCount.textContent = `${seoDescInput.value.length}/160`;
      seoDescCount.style.color = seoDescInput.value.length > 160 ? "#ef4444" : "#94a3b8";
    }
  }

  // Listeners for live typing
  contentInput.addEventListener("input", updatePreviewAndCounters);
  titleInput.addEventListener("input", updateSeoSnippet);
  if (seoTitleInput) seoTitleInput.addEventListener("input", updateSeoSnippet);
  if (seoDescInput) seoDescInput.addEventListener("input", updateSeoSnippet);

  // Initialize on page load
  updatePreviewAndCounters();
  updateSeoSnippet();

  // View Mode Buttons (Write / Preview / Split)
  const panes = document.getElementById("editor-panes");
  const viewBtns = document.querySelectorAll(".view-btn");

  viewBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      viewBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const mode = btn.dataset.mode;

      if (mode === "split") {
        panes.className = "editor-panes split-mode";
        contentInput.style.display = "block";
        previewPane.style.display = "block";
      } else if (mode === "write") {
        panes.className = "editor-panes";
        contentInput.style.display = "block";
        previewPane.style.display = "none";
      } else if (mode === "preview") {
        panes.className = "editor-panes";
        contentInput.style.display = "none";
        previewPane.style.display = "block";
      }
    });
  });

  // Markdown Toolbar buttons
  const toolbarButtons = document.querySelectorAll(".tool-btn");
  toolbarButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const action = btn.dataset.action;
      insertMarkdownSyntax(contentInput, action);
      updatePreviewAndCounters();
    });
  });

  // AI Generator Button
  const generateBtn = document.getElementById("btn-generate-ai");
  if (generateBtn) {
    generateBtn.addEventListener("click", async () => {
      const topic = topicInput.value.trim();
      if (!topic) {
        showToast("Please enter a blog topic before generating.", "error");
        topicInput.focus();
        return;
      }

      const tone = toneSelect ? toneSelect.value : "Professional";
      const length = lengthSelect ? lengthSelect.value : "Medium";
      const modeSelect = document.getElementById("generator-mode");
      const mode = modeSelect ? modeSelect.value : "demo";

      // Set loading state
      const originalText = generateBtn.innerHTML;
      generateBtn.disabled = true;
      generateBtn.innerHTML = `<span class="spinner"></span> Generating...`;

      try {
        const response = await fetch("/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic, tone, length, mode })
        });

        let data;
        try {
          data = await response.json();
        } catch (parseErr) {
          throw new Error(`Server returned unexpected response (Status ${response.status}).`);
        }

        if (response.ok && data.status === "success") {
          titleInput.value = data.title;
          contentInput.value = data.content;
          updatePreviewAndCounters();
          updateSeoSnippet();

          if (data.is_demo) {
            showToast("Demo Mode: Sample blog generated locally! (No API key required)", "info");
          } else {
            showToast("Blog content generated via OpenAI successfully!", "success");
          }

          // Auto-trigger SEO generation in matching mode
          autoGenerateSeo(topic, data.content, mode);
        } else {
          showToast(data.message || "Failed to generate blog content.", "error");
        }
      } catch (err) {
        showToast(err.message || "Network error during generation.", "error");
      } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = originalText;
      }
    });
  }

  // SEO Generator Button
  const generateSeoBtn = document.getElementById("btn-generate-seo");
  if (generateSeoBtn) {
    generateSeoBtn.addEventListener("click", () => {
      const topic = topicInput.value.trim() || titleInput.value.trim();
      const content = contentInput.value.trim();
      if (!topic && !content) {
        showToast("Please enter a topic or write some content to generate SEO.", "error");
        return;
      }
      const modeSelect = document.getElementById("generator-mode");
      const mode = modeSelect ? modeSelect.value : "demo";
      autoGenerateSeo(topic, content, mode);
    });
  }

  async function autoGenerateSeo(topic, content, mode = "demo") {
    if (!generateSeoBtn) return;
    const originalText = generateSeoBtn.innerHTML;
    generateSeoBtn.disabled = true;
    generateSeoBtn.innerHTML = `<span class="spinner"></span> Generating SEO...`;

    try {
      const res = await fetch("/api/generate-seo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, content, mode })
      });

      let data;
      try {
        data = await res.json();
      } catch (parseErr) {
        throw new Error(`Server returned unexpected response (Status ${res.status}).`);
      }

      if (res.ok && data.status === "success") {
        if (seoTitleInput) seoTitleInput.value = data.seo.meta_title || "";
        if (seoDescInput) seoDescInput.value = data.seo.meta_description || "";
        if (seoKeywordsInput) seoKeywordsInput.value = data.seo.keywords || "";
        updateSeoSnippet();
        showToast(data.is_demo ? "Demo Mode: SEO metadata generated locally!" : "SEO suggestions generated via OpenAI!", "success");
      } else {
        showToast(data.message || "Could not generate SEO.", "error");
      }
    } catch (e) {
      showToast(e.message || "Error generating SEO suggestions.", "error");
    } finally {
      generateSeoBtn.disabled = false;
      generateSeoBtn.innerHTML = originalText;
    }
  }

  // Save Draft & Publish Buttons
  const btnSaveDraft = document.getElementById("btn-save-draft");
  const btnPublish = document.getElementById("btn-publish");

  if (btnSaveDraft) {
    btnSaveDraft.addEventListener("click", () => saveBlogPost("draft"));
  }
  if (btnPublish) {
    btnPublish.addEventListener("click", () => saveBlogPost("published"));
  }

  async function saveBlogPost(targetStatus) {
    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    const topic = topicInput.value.trim();
    const tone = toneSelect ? toneSelect.value : "Professional";
    const length = lengthSelect ? lengthSelect.value : "Medium";

    if (!title) {
      showToast("Please provide a blog title.", "error");
      titleInput.focus();
      return;
    }
    if (!content) {
      showToast("Blog content cannot be empty.", "error");
      contentInput.focus();
      return;
    }

    const blogId = document.getElementById("blog-id") ? document.getElementById("blog-id").value : null;

    const payload = {
      title,
      content,
      topic,
      tone,
      length,
      status: targetStatus,
      seo: {
        meta_title: seoTitleInput ? seoTitleInput.value.trim() : title,
        meta_description: seoDescInput ? seoDescInput.value.trim() : "",
        keywords: seoKeywordsInput ? seoKeywordsInput.value.trim() : ""
      }
    };

    const targetBtn = targetStatus === "published" ? btnPublish : btnSaveDraft;
    const originalText = targetBtn.innerHTML;
    targetBtn.disabled = true;
    targetBtn.innerHTML = `<span class="spinner"></span> Saving...`;

    try {
      const url = blogId ? `/api/blogs/${blogId}` : "/api/blogs";
      const method = blogId ? "PUT" : "POST";

      const res = await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (res.ok && data.status === "success") {
        showToast(`Blog successfully saved as ${targetStatus}!`, "success");
        setTimeout(() => {
          window.location.href = "/";
        }, 800);
      } else {
        showToast(data.message || "Failed to save blog.", "error");
        targetBtn.disabled = false;
        targetBtn.innerHTML = originalText;
      }
    } catch (err) {
      showToast("Network error while saving blog post.", "error");
      targetBtn.disabled = false;
      targetBtn.innerHTML = originalText;
    }
  }
}

/* =============================================================================
   5. Markdown Toolbar Insertion Helper
   ============================================================================= */

function insertMarkdownSyntax(textarea, action) {
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const text = textarea.value;
  const selectedText = text.substring(start, end) || "text";

  let replacement = "";
  let cursorOffset = 0;

  switch (action) {
    case "bold":
      replacement = `**${selectedText}**`;
      cursorOffset = 2;
      break;
    case "italic":
      replacement = `*${selectedText}*`;
      cursorOffset = 1;
      break;
    case "h1":
      replacement = `\n# ${selectedText}\n`;
      break;
    case "h2":
      replacement = `\n## ${selectedText}\n`;
      break;
    case "h3":
      replacement = `\n### ${selectedText}\n`;
      break;
    case "quote":
      replacement = `\n> ${selectedText}\n`;
      break;
    case "bullet":
      replacement = `\n- ${selectedText}\n`;
      break;
    case "number":
      replacement = `\n1. ${selectedText}\n`;
      break;
    case "code":
      replacement = `\n\`\`\`python\n${selectedText}\n\`\`\`\n`;
      break;
    case "link":
      replacement = `[${selectedText}](https://example.com)`;
      break;
    default:
      return;
  }

  textarea.value = text.substring(0, start) + replacement + text.substring(end);
  textarea.focus();
  textarea.setSelectionRange(start + replacement.length, start + replacement.length);
}
