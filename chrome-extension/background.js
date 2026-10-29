// background.js - Phishing Shield AI Chrome Extension (Cloud, Tailscale & Local Support)

const DEFAULT_CLOUD_URL = "https://supplemental-work-qty-yeast.trycloudflare.com";

async function resolveDefaultApiUrl() {
  try {
    const res = await fetch(chrome.runtime.getURL("config.json"));
    if (res.ok) {
      const data = await res.json();
      if (data && data.apiUrl) return data.apiUrl;
    }
  } catch (e) {}
  return "auto";
}

chrome.runtime.onInstalled.addListener(async () => {
  console.log("Phishing Shield AI installed.");
  const res = await chrome.storage.local.get(["apiUrl"]);
  if (!res.apiUrl) {
    const defaultUrl = await resolveDefaultApiUrl();
    chrome.storage.local.set({ apiUrl: defaultUrl });
  }
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

        // Determine target endpoints (User preference > config.json > Cloud > Local fallback)
        const storageData = await chrome.storage.local.get(["apiUrl"]);
        let configUrl = storageData.apiUrl;
        if (!configUrl || configUrl === "auto") {
          const fileUrl = await resolveDefaultApiUrl();
          if (fileUrl && fileUrl !== "auto") {
            configUrl = fileUrl;
          }
        }
        configUrl = configUrl || "auto";

        let candidateEndpoints = [];
        if (configUrl && configUrl !== "auto") {
          candidateEndpoints.push(configUrl.replace(/\/+$/, '') + "/api/verify-message");
        } else {
          // In auto mode, try configured default cloud, then local fallbacks
          candidateEndpoints.push(`${DEFAULT_CLOUD_URL}/api/verify-message`);
          candidateEndpoints.push("http://127.0.0.1:8000/api/verify-message");
          candidateEndpoints.push("http://localhost:8000/api/verify-message");
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
