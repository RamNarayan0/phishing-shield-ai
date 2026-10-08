// Service Worker
console.log("Phishing Shield AI Background Service Worker Loaded.");

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "VERIFY_MESSAGE") {
        fetch("http://localhost:8000/api/verify-message", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(request.payload)
        })
        .then(response => response.json())
        .then(data => sendResponse({ success: true, data }))
        .catch(error => sendResponse({ success: false, error: error.message }));
        
        return true; // Keep the messaging channel open for sendResponse
    }
});
