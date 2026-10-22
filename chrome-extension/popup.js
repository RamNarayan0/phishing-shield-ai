// popup.js - Phishing Shield AI Chrome Extension

// Load settings on startup
chrome.storage.local.get(["apiUrl"], (res) => {
  const modeSelect = document.getElementById("apiMode");
  const badge = document.getElementById("envBadge");
  if (res.apiUrl) {
    modeSelect.value = res.apiUrl;
  }
  updateBadge(modeSelect.value);
});

document.getElementById("apiMode").addEventListener("change", (e) => {
  const val = e.target.value;
  chrome.storage.local.set({ apiUrl: val });
  updateBadge(val);
});

document.getElementById("toggleSettings").addEventListener("click", () => {
  const panel = document.getElementById("settingsPanel");
  panel.style.display = panel.style.display === "block" ? "none" : "block";
});

function updateBadge(val) {
  const badge = document.getElementById("envBadge");
  if (val === "http://127.0.0.1:8000") {
    badge.textContent = "Local Dev";
    badge.style.borderColor = "#64748b";
    badge.style.color = "#94a3b8";
  } else {
    badge.textContent = "Cloud AI";
    badge.style.borderColor = "#0284c7";
    badge.style.color = "#38bdf8";
  }
}

document.getElementById('scanBtn').addEventListener('click', async () => {
  const statusEl = document.getElementById('status');
  statusEl.textContent = "Scanning message text...";
  
  try {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab || !tab.id) {
      statusEl.textContent = "Error: Cannot detect active browser tab.";
      return;
    }

    if (tab.url.startsWith("chrome://") || tab.url.startsWith("edge://")) {
      statusEl.textContent = "Error: Cannot scan browser settings pages. Open WhatsApp Web or an email tab.";
      return;
    }
    
    // Inject script to extract text
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: extractPageText,
    }, (results) => {
      if (chrome.runtime.lastError) {
        statusEl.textContent = "Page Error: " + chrome.runtime.lastError.message;
        return;
      }
      
      if (!results || !results[0] || !results[0].result) {
        statusEl.textContent = "Could not read page selection.";
        return;
      }

      const text = results[0].result;
      const senderVal = document.getElementById('senderId').value.trim();
      
      if (text === "ERROR_NO_SELECTION") {
        statusEl.innerHTML = "<span style='color:#f59e0b;'>⚠️ Highlight a message or email with your mouse first, then click scan.</span>";
        return;
      }

      // Send to background service worker for analysis
      chrome.runtime.sendMessage({ 
        type: "ANALYZE_CONTENT", 
        payload: text,
        senderId: senderVal
      }, (response) => {
        if (chrome.runtime.lastError) {
          statusEl.textContent = "Extension Error: " + chrome.runtime.lastError.message;
          return;
        }
        if (response && response.result) {
          const r = response.result;
          const score = r.risk_score;
          const verdict = r.verdict || "UNKNOWN";
          const reasons = r.reasons || [];
          const phones = r.extracted_phones || [];
          const emails = r.extracted_emails || [];
          
          let color = "#22c55e"; // green
          if (score >= 80) color = "#ef4444"; // red
          else if (score >= 60) color = "#f97316"; // orange
          else if (score >= 30) color = "#eab308"; // yellow

          let html = `<div style="text-align:center; margin-bottom:8px; padding:6px; background:#1e293b; border-radius:6px; border:1px solid ${color}40;">
            <div style="font-size:16px; font-weight:800; color:${color}; letter-spacing:1px;">${verdict}</div>
            <div style="font-size:24px; font-weight:900; color:${color}; font-family:monospace;">${score} <span style="font-size:12px; color:#64748b;">/ 100</span></div>
          </div>`;

          if (senderVal) {
            html += `<div style="font-size:11px; color:#94a3b8; margin-bottom:4px;">Sender: <b style="color:#f1f5f9;">${senderVal}</b></div>`;
          }

          if (phones.length > 0) {
            html += `<div style="font-size:10px; color:#f59e0b; margin-bottom:4px;">📱 Phones: <b>${phones.join(', ')}</b></div>`;
          }

          if (emails.length > 0) {
            html += `<div style="font-size:10px; color:#a855f7; margin-bottom:4px;">📧 Emails: <b>${emails.join(', ')}</b></div>`;
          }

          if (reasons.length > 0) {
            html += `<div style="font-size:11px; color:#cbd5e1; border-top:1px solid #1e293b; padding-top:6px; margin-top:4px;">`;
            html += `<b>Detected Signals:</b><ul style="margin:4px 0; padding-left:14px;">`;
            reasons.forEach(reason => {
              html += `<li style="margin-bottom:2px; font-size:10.5px; color:#cbd5e1;">${reason}</li>`;
            });
            html += `</ul></div>`;
          }

          if (r.recommended_action) {
            let actionText = r.recommended_action.replace(/_/g, ' ');
            html += `<div style="font-size:11px; color:${color}; font-weight:bold; margin-top:6px; text-transform:uppercase; letter-spacing:0.5px;">Recommendation: ${actionText}</div>`;
          }

          statusEl.innerHTML = html;
        } else {
          statusEl.innerHTML = `<span style="color:#ef4444;">Error: ${response?.error || "Cannot reach backend server"}</span>`;
        }
      });
    });
  } catch (err) {
    statusEl.textContent = "System Error: " + err.message;
  }
});

// Runs in web page DOM
function extractPageText() {
  const selection = window.getSelection().toString();
  if (selection.trim().length > 0) {
      return selection; 
  }
  return "ERROR_NO_SELECTION"; 
}
