// background.js - Phishing Shield AI Chrome Extension

chrome.runtime.onInstalled.addListener(() => {
  console.log("Phishing Shield AI installed.");
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "ANALYZE_CONTENT") {
    (async () => {
      try {
        const payload = {
          raw_text: message.payload || "Empty Content",
          source_platform: "Chrome Web",
          sender_id: message.senderId || "Unknown",
          urls: sender.tab ? [sender.tab.url] : []
        };

        let data = null;

        // Try localhost first, then 127.0.0.1 fallback
        for (const host of ["localhost", "127.0.0.1"]) {
          try {
            const res = await fetch(`http://${host}:8000/api/verify-message`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload)
            });
            data = await res.json();
            break; // success, stop trying
          } catch (e) {
            console.warn(`Failed on ${host}:`, e.message);
          }
        }

        if (data) {
          sendResponse({ result: data });
        } else {
          sendResponse({ result: null, error: "Cannot reach backend. Make sure the server is running on port 8000." });
        }
      } catch (err) {
        console.error("Analysis Error:", err);
        sendResponse({ result: null, error: err.message });
      }
    })();
    return true; // keeps message channel open for async response
  }
});
