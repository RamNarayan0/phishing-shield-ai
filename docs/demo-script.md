# Demo Script - Phishing Shield AI

*Time: 3-5 minutes*

### STEP 1: Introduction
**Open Dashboard (http://localhost:3000)**

*Speak:* "Phishing attacks don't only arrive as suspicious websites. They arrive through messages, emails, and social links. Today I will demonstrate Phishing Shield AI, a real-time threat detection engine."

### STEP 2: The Baseline (Safe Message)
**Click the 'Safe Message' preset button on the dashboard.**

*Speak:* "First, let's analyze a normal message. As you can see, the system parses the text and identifies it as SAFE with a low risk score. No suspicious signals are detected."

### STEP 3: The Threat (Phishing Message)
**Click the 'Phishing Link' preset button.**

*Speak:* "Now, let's look at a simulated attack. 'URGENT: Your bank account has been suspended. Verify immediately at this link.'"

**Click 'Analyze Threat'**

*Speak:* "The system immediately flags this as CRITICAL."

### STEP 4: Explainability
**Point to the 'Detected Signals' section on the screen.**

*Speak:* "Notice that the system did not just rely on one simple keyword. It combined multiple independent signals: urgent language, an account suspension threat, and a suspicious URL structure. This explainability is crucial for users to understand *why* they shouldn't click."

### STEP 5: Browser Integration
**Open a new tab or use a test page. Click the Phishing Shield Chrome Extension popup.**
**Click 'Scan Current Page'.**

*Speak:* "But users don't always copy and paste messages. Our architecture allows for seamless integrations. Here is our Chrome Extension dynamically analyzing the browser content in real-time, using the exact same backend risk engine."

### STEP 6: Architecture Overview
**Show the README Architecture diagram or quickly explain it.**

*Speak:* "The system is built for scalability. Clients like the web dashboard, browser extension, or mobile apps simply send the payload to the FastAPI core. Our analysis pipeline separates Text Analysis, URL extraction, and Sender profiling before passing it to a Risk Engine that generates the final explainable verdict."
