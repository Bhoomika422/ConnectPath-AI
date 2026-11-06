const modal = document.getElementById("modal");
const modalContent = document.getElementById("modal-content");
const closeModal = () => { modal.hidden = true; };
document.getElementById("close-modal").addEventListener("click", closeModal);
modal.addEventListener("click", e => { if (e.target === modal) closeModal(); });

document.getElementById("filter").addEventListener("input", e => {
  const q = e.target.value.toLowerCase();
  document.querySelectorAll(".app-card").forEach(card => {
    card.style.display = card.dataset.name.includes(q) ? "" : "none";
  });
});

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function guideHtml(g, shareUrl) {
  const list = (items) => `<ul>${(items || []).map(x => `<li>${escapeHtml(x)}</li>`).join("")}</ul>`;
  const steps = (g.steps || []).map((s,i) => `<div class="step"><span class="step-num">${i+1}</span><div><b>${escapeHtml(s.title)}</b><p>${escapeHtml(s.detail)}</p><span class="owner">${escapeHtml(s.owner || "Check")}</span></div></div>`).join("");
  const sources = (g.sources || []).map(s => `<li><a href="${escapeHtml(s.url)}" target="_blank" rel="noopener">${escapeHtml(s.label)}</a></li>`).join("");
  return `<div class="eyebrow">OAUTH SETUP GUIDE</div><div class="guide-title">${escapeHtml(g.app_name)} setup</div><p class="guide-summary">${escapeHtml(g.summary)}</p>
  <div class="guide-stats"><div><small>DIFFICULTY</small><b>${escapeHtml(g.difficulty)}</b></div><div><small>ESTIMATED SETUP</small><b>${escapeHtml(g.estimated_time)}</b></div><div><small>APPROVAL WAIT</small><b>${escapeHtml(g.approval_wait)}</b></div></div>
  <div class="guide-section"><h3>Setup steps</h3>${steps}<h3>Requirements</h3>${list(g.requirements)}<h3>Potential blockers</h3>${list(g.blockers)}<h3>Agent can help with</h3>${list(g.agent_can_do)}<h3>Human must handle</h3>${list(g.human_must_do)}<h3>Sources & verification</h3><ul>${sources}</ul><p class="verification">${escapeHtml(g.verification_notes || g.verification || "")}<br>Research mode: ${escapeHtml(g.research_mode || "Curated guide")}</p></div>
  <div class="share-row"><a href="${escapeHtml(shareUrl)}" target="_blank">Open shareable guide ↗</a><button class="secondary" id="copy-share">Copy guide link</button></div>`;
}
async function showCurated(slug) {
  try {
    const res = await fetch(`/api/apps/${slug}`);

    if (!res.ok) {
      throw new Error("Could not load this guide.");
    }

    const g = await res.json();

    // Normalize library data for the guide renderer
    g.app_name = g.app_name || g.name;
    g.summary = g.summary || g.description;
    g.estimated_time = g.estimated_time || g.time;
    g.approval_wait = g.approval_wait || g.approval;
    g.verification_notes =
      g.verification_notes || g.verification;

    const share = `${location.origin}/#directory`;

    modalContent.innerHTML = guideHtml(g, share);
    modal.hidden = false;

    document.getElementById("copy-share")
      .addEventListener("click", async () => {
        await navigator.clipboard.writeText(share);
        document.getElementById("copy-share").textContent = "Copied";
      });

  } catch (error) {
    console.error("Guide loading error:", error);
    alert(error.message);
  }
}
document.querySelectorAll(".text-button").forEach(btn => btn.addEventListener("click", () => showCurated(btn.dataset.slug)));

document.getElementById("generate-form").addEventListener("submit", async e => {
  e.preventDefault();
  const name = document.getElementById("app-name").value.trim();
  const url = document.getElementById("docs-url").value.trim();
  const status = document.getElementById("status");
  const button = document.getElementById("generate-btn");
  status.hidden = false; status.className = "status"; status.textContent = "Researching the documentation and drafting your guide…";
  button.disabled = true; button.textContent = "Researching…";
  try {
    const res = await fetch("/api/generate", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({app_name:name,url})});
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not generate guide.");
    status.textContent = "Guide generated. Review the evidence and unverified items below.";
    modalContent.innerHTML = guideHtml(data.guide, data.share_url);
    modal.hidden = false;
    document.getElementById("copy-share").addEventListener("click", async () => {
      await navigator.clipboard.writeText(data.share_url);
      document.getElementById("copy-share").textContent = "Copied";
    });
  } catch (err) {
    status.className = "status error"; status.textContent = err.message;
  } finally {
    button.disabled = false; button.innerHTML = 'Generate guide <span>↗</span>';
  }
});
