# FAQ For Faculty Guide

### 1. Why FastAPI?
FastAPI is a modern, high-performance web framework for Python. It provides automatic interactive API documentation (Swagger UI), validation via Pydantic, and handles asynchronous requests efficiently, which is ideal for real-time threat detection.

### 2. Why React?
React allows for component-driven UI development, making it easy to create an interactive, stateful dashboard for threat analysis.

### 3. Why TF-IDF?
Term Frequency-Inverse Document Frequency (TF-IDF) is a statistical measure that evaluates how relevant a word is to a document in a collection. It is computationally lightweight, requiring no GPU, making it perfect for our prototype baseline.

### 4. Why Logistic Regression?
Logistic Regression is an excellent binary classification algorithm. It outputs probabilities, which maps perfectly to our 0-100 risk scoring system.

### 5. Why not BERT?
BERT and other large language models are highly accurate but computationally expensive and slow. For this prototype, we prioritized a lightweight, real-time CPU-based architecture. BERT is documented as a future enhancement.

### 6. How is URL analysis performed?
We use deterministic security heuristics to analyze the URL domain, path, scheme (HTTPS), presence of IP addresses, and typosquatting patterns.

### 7. How do you calculate risk score?
We use a hybrid weighting model. The system calculates the ML probability score and the text heuristic score, takes the maximum of the two as the core text risk, and adds weighted penalties for suspicious URLs and senders.

### 8. What happens when the ML model is uncertain?
The system falls back on deterministic heuristics. If the ML probability is below 60%, it outputs a 0 score, allowing the rule-based Text and URL engines to dictate the risk level.

### 9. How does Android receive messages?
Via the `NotificationListenerService`, an Android OS feature that can intercept incoming notifications from apps like WhatsApp or SMS, extracting the text for API analysis.

### 10. How does the Chrome extension work?
It uses Manifest V3 Content Scripts to read the visible DOM text (`document.body.innerText`) and extracts URLs, passing them to the FastAPI backend via a Background Service Worker to bypass CORS restrictions.

### 11. How does Gmail authentication work?
For production, it uses OAuth 2.0. The user grants access via a consent screen, and the application receives an access token to read emails via the Gmail REST API. No passwords are ever stored.

### 12. What protocols are used?
HTTP/HTTPS for transport, REST for API architecture, JSON for data interchange, and TLS for encryption.

### 13. What is REST API?
Representational State Transfer. It is a software architectural style that uses standard HTTP methods (GET, POST) to interact with stateless resources.

### 14. What is OAuth 2.0?
An industry-standard protocol for authorization. It grants a third-party application limited access to an HTTP service without sharing user credentials.

### 15. What is HTTPS?
Hypertext Transfer Protocol Secure. It uses TLS to encrypt HTTP requests and responses.

### 16. Why is localhost not accessible externally?
`localhost` (127.0.0.1) is a loopback interface meaning the network traffic never leaves the local machine's network card.

### 17. How can another person access the demo?
By connecting to the same LAN (Wi-Fi) and using the host machine's IPv4 address (e.g., `192.168.1.5:5173`), or by using a tunneling service like Cloudflare Tunnel.

### 18. What are the privacy concerns?
Analyzing messages requires accessing private text. We address this by ensuring zero persistence (messages are dropped immediately after analysis) and avoiding storage of sensitive data.

### 19. What are the limitations?
The ML dataset is currently a synthetic prototype baseline. Real-world implementation requires a massive labeled dataset. Web DOM scraping is also inherently brittle to UI changes.

### 20. How can this become production software?
By transitioning to a larger ML model (BERT/Transformers), integrating real-time threat intelligence feeds (e.g., VirusTotal), and deploying to a secure, auto-scaling cloud environment using Docker and Kubernetes.
