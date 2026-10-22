// background.js - Phishing Shield AI Chrome Extension (Cloud & Local Support)

const DEFAULT_CLOUD_URL = "https://phishing-shield-ai-backend.onrender.com";

chrome.runtime.onInstalled.addListener(() => {
  console.log("Phishing Shield AI installed.");
  chrome.storage.local.get(["apiUrl"], (res) => {
    if (!res.apiUrl) {
      chrome.storage.local.set({ apiUrl: "auto" });
    }
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "ANALYZE_CONTENT") {
    (async () => {
      try {
        const payload = {
          raw_text: message.payload || "Empty Content",
          source_platform: "Chrome Extension",
          sender_id: message.senderId || "Unknown",
          urls: sender.tab ? [sender.tab.url] : []
        };

        // Determine target endpoints (User preference > Cloud Render > Local fallback)
        const storageData = await chrome.storage.local.get(["apiUrl"]);
        const configUrl = storageData.apiUrl || "auto";

        let candidateEndpoints = [];
        if (configUrl && configUrl !== "auto") {
          candidateEndpoints.push(configUrl.replace(/\/+$/, '') + "/api/verify-message");
        } else {
          // In auto mode, try local first for dev, then cloud Render
          candidateEndpoints.push("http://127.0.0.1:8000/api/verify-message");
          candidateEndpoints.push("http://localhost:8000/api/verify-message");
          candidateEndpoints.push(`${DEFAULT_CLOUD_URL}/api/verify-message`);
        }

        let data = null;
        let lastError = null;

        for (const endpoint of candidateEndpoints) {
          try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 6000);

            const res = await fetch(endpoint, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
              signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (res.ok) {
              data = await res.json();
              data._endpoint_used = endpoint;
              break;
            }
          } catch (e) {
            lastError = e.message;
            console.warn(`Connection attempt failed on ${endpoint}:`, e.message);
          }
        }

        if (data) {
          sendResponse({ result: data });
        } else {
          sendResponse({
            result: null,
            error: `Cannot reach backend services. Checked: ${candidateEndpoints.join(', ')}. Last error: ${lastError || 'Timeout'}`
          });
        }
      } catch (err) {
        console.error("Analysis Error:", err);
        sendResponse({ result: null, error: err.message });
      }
    })();
    return true; // keeps message channel open for async response
  }
});
