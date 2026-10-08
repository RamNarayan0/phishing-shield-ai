document.getElementById('scanBtn').addEventListener('click', async () => {
  const statusEl = document.getElementById('status');
  statusEl.textContent = "Scanning...";
  
  try {
    // Get active tab
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab || !tab.id) {
      statusEl.textContent = "Error: Cannot detect active tab.";
      return;
    }

    if (tab.url.startsWith("chrome://") || tab.url.startsWith("edge://")) {
      statusEl.textContent = "Error: Cannot scan browser settings pages. Go to a real website (like WhatsApp Web).";
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
        statusEl.textContent = "Could not read page text.";
        return;
      }

      const text = results[0].result;
      const senderVal = document.getElementById('senderId').value.trim();
      
      if (text === "ERROR_NO_SELECTION") {
        statusEl.textContent = "⚠️ Highlight a message with your mouse first, then scan.";
        return;
      }

      // Send to background for analysis
      chrome.runtime.sendMessage({ 
        type: "ANALYZE_CONTENT", 
        payload: text,
        senderId: senderVal
      }, (response) => {
        if (chrome.runtime.lastError) {
          statusEl.textContent = "Ext Error: " + chrome.runtime.lastError.message;
          return;
        }
        if (response && response.result) {
          const r = response.result;
          const score = r.risk_score;
          const verdict = r.verdict || "UNKNOWN";
          const reasons = r.reasons || [];
          
          let color = "#22c55e"; // green
          if (score >= 80) color = "#ef4444"; // red
          else if (score >= 60) color = "#f97316"; // orange
          else if (score >= 30) color = "#eab308"; // yellow

          let html = `<div style="text-align:center; margin-bottom:8px;">
            <div style="font-size:20px; font-weight:bold; color:${color};">${verdict}</div>
            <div style="font-size:28px; font-weight:bold; color:${color};">${score} / 100</div>
          </div>`;

          if (senderVal) {
            html += `<div style="font-size:11px; color:#94a3b8; margin-bottom:6px;">Sender: <b>${senderVal}</b></div>`;
          }

          if (reasons.length > 0) {
            html += `<div style="font-size:11px; color:#cbd5e1; border-top:1px solid #334155; padding-top:6px; margin-top:4px;">`;
            html += `<b>Signals Detected:</b><ul style="margin:4px 0; padding-left:16px;">`;
            reasons.forEach(reason => {
              html += `<li style="margin-bottom:2px;">${reason}</li>`;
            });
            html += `</ul></div>`;
          }

          if (r.recommended_action) {
            let actionText = r.recommended_action.replace(/_/g, ' ');
            html += `<div style="font-size:11px; color:${color}; font-weight:bold; margin-top:6px;">Action: ${actionText}</div>`;
          }

          statusEl.innerHTML = html;
        } else {
          statusEl.textContent = "Error: " + (response?.error || "Unknown Network Error");
        }
      });
    });
  } catch (err) {
    statusEl.textContent = "System Error: " + err.message;
  }
});

// This function runs in the context of the web page
function extractPageText() {
  const selection = window.getSelection().toString();
  if (selection.trim().length > 0) {
      return selection; 
  }
  return "ERROR_NO_SELECTION"; 
}
