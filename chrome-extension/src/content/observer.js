class PageObserver {
    constructor() {
        this.analyzed = false;
    }

    async analyzePage() {
        if (this.analyzed) return;
        this.analyzed = true;

        const text = window.Extractor.extractVisibleText();
        const urls = window.Extractor.extractUrls();
        
        // Take a small sample of text to avoid huge payloads
        const textSample = text.substring(0, 1000);

        try {
            const verdict = await window.BackendClient.verifyMessage({
                source_platform: "chrome",
                raw_text: textSample,
                urls: urls
            });

            if (verdict.risk_score >= 60) {
                window.Injector.showWarning(verdict);
            }
        } catch (e) {
            console.error("Phishing Shield analysis failed:", e);
        }
    }

    start() {
        // Run initial analysis after a short delay
        setTimeout(() => this.analyzePage(), 1500);
    }
}

// Ensure dependencies are loaded
if (window.Extractor && window.BackendClient && window.Injector) {
    const observer = new PageObserver();
    observer.start();
}
