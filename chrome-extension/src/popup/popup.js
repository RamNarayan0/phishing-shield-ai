document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('scan-btn').addEventListener('click', async () => {
        const resultDiv = document.getElementById('result');
        resultDiv.innerHTML = "Scanning...";
        
        try {
            // Get current tab
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // Just pass the URL for popup scan
            const payload = {
                source_platform: "chrome_popup",
                raw_text: "Checking page: " + tab.url,
                urls: [tab.url]
            };
            
            const verdict = await window.BackendClient.verifyMessage(payload);
            
            let color = "#10b981"; // safe
            if (verdict.risk_score >= 60) color = "#ef4444"; // critical/high
            else if (verdict.risk_score >= 30) color = "#f59e0b"; // suspicious
            
            resultDiv.innerHTML = `
                <div style="margin-top: 10px; padding: 10px; border: 1px solid #333; border-radius: 4px;">
                    <strong style="color: ${color}">${verdict.verdict}</strong>
                    <div>Score: ${verdict.risk_score}/100</div>
                </div>
            `;
        } catch (e) {
            resultDiv.innerHTML = `Error: ${e.message}`;
        }
    });
});
