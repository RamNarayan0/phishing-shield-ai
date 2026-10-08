class Injector {
    static showWarning(verdict) {
        // Prevent duplicate warnings
        if (document.getElementById('phishing-shield-warning')) return;

        const warningDiv = document.createElement('div');
        warningDiv.id = 'phishing-shield-warning';
        warningDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 350px;
            background-color: #1a1a1a;
            border: 2px solid #ef4444;
            color: #ffffff;
            z-index: 999999;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            font-family: system-ui, -apple-system, sans-serif;
        `;

        const reasonsHtml = verdict.reasons.map(r => `<li>${r}</li>`).join('');

        warningDiv.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px;">
                <h3 style="margin: 0; color: #ef4444; display: flex; align-items: center; gap: 8px;">
                    🚨 PHISHING SHIELD
                </h3>
                <button id="ps-close-btn" style="background: none; border: none; color: #888; cursor: pointer; font-size: 16px;">✕</button>
            </div>
            <div style="font-weight: bold; margin-bottom: 10px; color: #f87171;">
                HIGH-RISK CONTENT DETECTED
            </div>
            <div style="margin-bottom: 15px;">
                <strong>Risk Score:</strong> ${verdict.risk_score}/100
            </div>
            <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #d1d5db; margin-bottom: 15px;">
                ${reasonsHtml}
            </ul>
            <div style="background-color: #ef4444; color: white; text-align: center; padding: 10px; border-radius: 4px; font-weight: bold;">
                ${verdict.recommended_action.replace(/_/g, ' ')}
            </div>
        `;

        document.body.appendChild(warningDiv);

        document.getElementById('ps-close-btn').addEventListener('click', () => {
            warningDiv.remove();
        });
    }
}
window.Injector = Injector;
