// background.js - Phishing Shield AI Chrome Extension (Cloud & Local Support)

const FALLBACK_CLOUD_URL = "https://thank-causes-materials-seed.trycloudflare.com";

async function resolveDefaultApiUrl() {
  try {
    const res = await fetch(chrome.runtime.getURL("config.json"));
    if (res.ok) {
      const data = await res.json();
      if (data && data.apiUrl) return data.apiUrl;
    }
  } catch (e) {}
  return FALLBACK_CLOUD_URL;
}

chrome.runtime.onInstalled.addListener(async () => {
  console.log("Phishing Shield AI installed/updated.");
  const defaultUrl = await resolveDefaultApiUrl();
  chrome.storage.local.set({ apiUrl: defaultUrl });
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

        const defaultUrl = await resolveDefaultApiUrl();
        const storageData = await chrome.storage.local.get(["apiUrl"]);
        let configUrl = storageData.apiUrl;
        
        // Discard stale trycloudflare URLs that don't match the current config
        if (!configUrl || configUrl === "auto" || (configUrl.includes("trycloudflare.com") && configUrl !== defaultUrl)) {
          configUrl = defaultUrl;
          chrome.storage.local.set({ apiUrl: configUrl });
        }

        let candidateEndpoints = [];
        // 1. Primary configured Cloud / Custom endpoint
        if (configUrl && configUrl !== "auto") {
          candidateEndpoints.push(configUrl.replace(/\/+$/, '') + "/api/verify-message");
        }
        // 2. Default Cloud endpoint if different
        const defaultEndpoint = defaultUrl.replace(/\/+$/, '') + "/api/verify-message";
        if (!candidateEndpoints.includes(defaultEndpoint)) {
          candidateEndpoints.push(defaultEndpoint);
        }
        // 3. Local endpoints for offline / local dev
        const localPrimary = "http://127.0.0.1:8000/api/verify-message";
        const localSecondary = "http://localhost:8000/api/verify-message";
        if (!candidateEndpoints.includes(localPrimary)) {
          candidateEndpoints.push(localPrimary);
        }
        if (!candidateEndpoints.includes(localSecondary)) {
          candidateEndpoints.push(localSecondary);
        }

        let data = null;
        let lastError = null;

        for (const endpoint of candidateEndpoints) {
          try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 8000);

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
