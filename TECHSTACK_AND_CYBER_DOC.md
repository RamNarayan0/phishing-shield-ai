# Phishing Shield AI — Technical Stack, Machine Learning & Cybersecurity Architecture Document

---

## 1. Executive System Mission & Architecture Overview

**Phishing Shield AI** is an enterprise-grade, defense-in-depth threat detection and explainable risk analysis ecosystem. It actively intercepts, decomposes, inspects, and neutralizes multi-channel social engineering threats across modern communication channels (Webmail, WhatsApp Web, SMS/Smishing, and Browser Navigation).

Rather than relying solely on static blacklists (which fail against zero-day URLs) or isolated black-box deep learning models (which suffer from hallucinations and zero explainability), Phishing Shield AI implements a **Hybrid Neuro-Symbolic Security Architecture**:
1. **Empirical Natural Language Processing (NLP)**: Statistical text classification over a verified 29,113-sample dataset.
2. **Deterministic Contextual Detectors**: Specialized rule engines examining RFC compliance, international telecommunication routing codes (ITU-T E.164), domain registrar heuristics, and homoglyph typosquatting.
3. **Explainable AI (XAI) Risk Engine**: A transparent arbitration layer that aggregates probabilistic signals into a calibrated 0–100 threat score accompanied by verifiable forensic evidence for Security Operations Center (SOC) analysts and end users.

```
+-------------------------------------------------------------------------------------------------------+
|                                    CLIENT THREAT RECEPTORS                                            |
|                                                                                                       |
|  +--------------------------------+   +-------------------------------+   +------------------------+  |
|  | Google Chrome Extension (MV3)  |   | React SOC Security Dashboard  |   | Webmail / SMS Payloads |  |
|  | Background Worker & Content DOM|   | Real-Time Analysis & Telemetry|   | Zero-Day Raw Messages  |  |
|  +----------------+---------------+   +---------------+---------------+   +------------+-----------+  |
+-------------------|-----------------------------------|--------------------------------|--------------+
                    |                                   |                                |
                    +-----------------------------------+--------------------------------+
                                                        |
                                                        v
+-------------------------------------------------------------------------------------------------------+
|                                  API GATEWAY & DEFENSIVE PERIMETER                                     |
|                                                                                                       |
|  - FastHTTP / ASGI Engine (FastAPI & Uvicorn 3.11.9)                                                  |
|  - Content-Length Protection (256 KB Buffer Limit against Resource Exhaustion / ReDoS)               |
|  - HTTP Hardened Security Headers (HSTS, CSP, X-Frame-Options: DENY, X-Content-Type-Options)          |
|  - Strict Origin Isolation & CORS Matrix (Vercel, Render, GitHub Pages, Local Extension ID)           |
+-----------------------------------------------|-------------------------------------------------------+
                                                |
                                                v
+-------------------------------------------------------------------------------------------------------+
|                                  EXTRACTION & SIGNAL NORMALIZATION                                    |
|                                                                                                       |
|  - EmailExtractor (RFC 5322 Lexical Parsing, Discarding Angle Brackets, Punctuation Stripping)        |
|  - PhoneExtractor (E.164 Standard, International Country Codes, Local Landline / Mobile Sanitization) |
|  - URLExtractor (RFC 3986 Tokenization, Scheme Normalization, Punycode / Homoglyph Parsing)          |
+-----------------------------------------------|-------------------------------------------------------+
                                                |
                                                v
+-------------------------------------------------------------------------------------------------------+
|                                  HYBRID DETECTION & ML INFERENCE PIPELINE                             |
|                                                                                                       |
|  +-------------------------------+   +-----------------------------+   +---------------------------+  |
|  | Production NLP Classifier     |   | Phone Pattern Classifier    |   | Email Spoofing Classifier |  |
|  | TF-IDF (15,000 N-Grams) +     |   | ITU-T E.164 Route Heuristics|   | Levenshtein Brand Metric  |  |
|  | Regularized Logistic Regress. |   | Entropy + Institutional Loss|   | Abuse TLD + Disposable    |  |
|  +---------------+---------------+   +--------------+--------------+   +-------------+-------------+  |
|                  |                                  |                                |                |
|                  +----------------------------------+--------------------------------+                |
|                                                     |                                                 |
|  +--------------------------------------------------+----------------------------------------------+  |
|  | Deterministic Security Heuristics (URL Typosquatting, Unencrypted HTTP, IP-in-Hostname, Urgency) |  |
|  +--------------------------------------------------+----------------------------------------------+  |
+-----------------------------------------------------|-------------------------------------------------+
                                                      |
                                                      v
+-------------------------------------------------------------------------------------------------------+
|                                  EXPLAINABLE AI (XAI) RISK ARBITRATION                                 |
|                                                                                                       |
|  - Weighted Multi-Vector Formulation (Text 40-50%, URL/Phone Vector 80%, Sender Discrepancy 30-40%)  |
|  - High-Confidence Override Gates (Toll Fraud >= 70, Brand Spoofing >= 80 -> Immediate Escalation)    |
|  - Output Calibrated Score (0-100), Verdict ('SAFE', 'SUSPICIOUS', 'CRITICAL'), Defense Playbook     |
+-----------------------------------------------------|-------------------------------------------------+
                                                      |
                                                      v
+-------------------------------------------------------------------------------------------------------+
|                                  ENTERPRISE PERSISTENCE & ANALYTICS                                   |
|                                                                                                       |
|  - MongoDB Atlas Cloud Database Engine                                                                |
|  - SHA-256 Cryptographic Record Fingerprinting (Zero-PII Storage Model)                               |
|  - Atomic Upsert Counters (`$inc: {duplicate_count: 1}`) with 30-Day TTL Data Retention              |
+-------------------------------------------------------------------------------------------------------+
```

---

## 2. In-Depth Programming Languages Breakdown

The system is constructed using four targeted programming languages, each chosen for its exact operational characteristics:

### 2.1. Python (v3.11.9) — Backend, ML Serving & Security Engine
* **Role**: Primary language for the threat detection API, machine learning model compilation, regex tokenizers, and database asynchronous drivers.
* **Why Python 3.11+**:
  - **Specializing Adaptive Interpreter**: Python 3.11 introduces faster bytecode execution (10–25% faster than 3.10), essential for parsing thousands of inbound strings per second without blocking the async event loop.
  - **AsyncIO Native Concurrency**: Enables asynchronous I/O via `async/await`, powering non-blocking MongoDB interactions through `motor` and ASGI execution via `uvicorn`.
  - **Scientific Ecosystem**: Provides native binding to C-accelerated linear algebra libraries (`numpy`, `scipy`, `scikit-learn`), allowing vector calculations to run in compiled C routines rather than interpreted loops.
* **Key Libraries Used**:
  - `fastapi` & `uvicorn`: Ultra-low latency ASGI web framework built on Starlette and Pydantic.
  - `scikit-learn` & `joblib`: Model serialization, TF-IDF sparse matrix computation, and logistic decision boundaries.
  - `pandas` & `numpy`: High-throughput dataset cleansing, deduplication, and vectorized feature transformations.
  - `motor` & `pymongo`: Asynchronous MongoDB client utilizing Python's native `asyncio` event loop.
  - `python-dotenv` & `pydantic-settings`: Strict type-safe environment variable parsing with fail-fast validation.

### 2.2. JavaScript (ES2022+ & JSX) — Frontend UI & Chrome Extension
* **Role**: Executes in browser execution contexts (DOM content scripts, background service workers, and reactive SOC dashboards).
* **Execution Paradigms**:
  - **React 18 (Concurrent Mode)**: Powers the SOC dashboard (`frontend/src/App.jsx`). Employs state transitions, virtual DOM reconciliation, and hooks (`useState`, `useEffect`, `useCallback`) to ingest live threat streams without UI lag.
  - **Vite 5 Bundler**: Uses Rollup and ESbuild under the hood for fast Hot Module Replacement (HMR) and optimized Tree-Shaken single-page bundle generation.
  - **Chrome Extension Manifest V3 Runtime**:
    - `background.js`: Chrome Extension Service Worker operating on an ephemeral event-driven lifecycle. Manages inter-tab messaging, icon badge indicators, and offloaded API telemetry.
    - `content.js`: DOM observer injected into active tabs. Uses `MutationObserver` APIs to detect dynamic DOM updates (e.g., incoming chats on WhatsApp Web) without polling the CPU.
* **Key Libraries Used**:
  - `lucide-react`: Lightweight, tree-shakable SVG icon system for threat categorization icons.
  - `tailwindcss` & `postcss`: Utility-first atomic CSS generation ensuring minimal production bundle size (< 15 KB gzipped).

### 2.3. PowerShell (v5.1 & v7 Core) — Enterprise Deployment & Zero-Trust Installer
* **Role**: Powers the enterprise one-liner endpoint installer (`install.ps1`) for multi-laptop corporate rollouts.
* **Why PowerShell**:
  - Native to every Windows endpoint since Windows 7, requiring zero third-party runtimes (no Python or Node.js needed on client machines).
  - Employs strict ErrorAction policies (`$ErrorActionPreference = 'Stop'`) and cryptographically safe download routines (`System.Net.WebClient` with TLS 1.2+ forced).
  - Direct integration with Windows Credential & AppData isolation scopes (`$env:LOCALAPPDATA`).

### 2.4. MongoDB Query Language (MQL) & JSON/BSON — Persistence & Auditing
* **Role**: Cryptographic record indexing, deduplication counters, and threat persistence.
* **Implementation**:
  - BSON document schemas enforce structural integrity while allowing flexible metadata storage (e.g., nested arrays of threat signals).
  - Employs compound unique indices (`{"fingerprint": 1}`) to convert record writes into atomic upserts, preventing database bloat under brute-force attacks.

---

## 3. In-Detail Machine Learning Models & Analytical Engines

Phishing Shield AI does not rely on a single vulnerable model. It coordinates **five specialized analytical engines**:

```
                                      RAW INBOUND CONTENT
                                              |
                     +------------------------+------------------------+
                     |                                                 |
                     v                                                 v
           [ Unstructured Text ]                             [ Structured Artifacts ]
                     |                                                 |
         +-----------+-----------+                     +---------------+---------------+
         |                       |                     |               |               |
         v                       v                     v               v               v
   [ TF-IDF Vector ]     [ Heuristic Signals ]   [ URLs ]       [ Phone #s ]     [ Email/Domain ]
         |                       |                     |               |               |
         v                       |                     v               v               v
  ( Logistic Reg. )              |              ( URL Graph )    ( ITU-T Model ) ( Brand Model )
  [ model.pkl ]                  |              [ Detector ]     [ phone_mdl ]   [ email_mdl ]
         |                       |                     |               |               |
         +----------+------------+                     +-------+-------+---------------+
                    |                                          |
                    v                                          v
             Text Threat Score                        Vector Threat Score
                    \                                         /
                     \                                       /
                      v                                     v
                  +---------------------------------------------+
                  |     Hybrid Explainability Risk Engine       |
                  |             (risk_engine.py)                |
                  +---------------------------------------------+
                                         |
                                         v
                         FINAL VERDICT & FORENSIC EVIDENCE
```

---

### 3.1. Primary NLP Threat Classifier (`model.pkl` + `vectorizer.pkl`)

#### Architecture & Mathematical Theory
The primary classifier combines **Sublinear Term Frequency-Inverse Document Frequency (TF-IDF)** with a **L2-Regularized Logistic Regression** classifier.

1. **Sublinear Term Frequency (Sublinear TF)**:
   In phishing communication, repeated spam words (e.g., "urgent urgent urgent") should not artificially skew the feature vector linearly. Sublinear TF applies logarithmic dampening:
   $$\text{TF}_{\text{sublinear}}(t, d) = 1 + \log(\text{TF}(t, d)) \quad \text{for } \text{TF} > 0$$

2. **Inverse Document Frequency (IDF) Smoothing**:
   $$\text{IDF}(t, D) = \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$
   The resulting feature vector $\mathbf{x} = \text{TF}_{\text{sublinear}} \times \text{IDF}$ is normalized under the Euclidean L2-norm:
   $$\|\mathbf{x}\|_2 = \sqrt{\sum_{i=1}^{n} x_i^2}$$

3. **Classification Decision Boundary**:
   Logistic Regression models the posterior probability of the class $Y \in \{0 (\text{Safe}), 1 (\text{Phishing})\}$ via the logistic sigmoid function:
   $$P(Y=1|\mathbf{x}) = \sigma(\mathbf{w}^T \mathbf{x} + b) = \frac{1}{1 + \exp\left(-\left(\sum_{i=1}^{m} w_i x_i + b\right)\right)}$$

4. **Objective Function with L2 Ridge Penalty**:
   $$\min_{\mathbf{w}, b} \frac{1}{2} \|\mathbf{w}\|_2^2 + C \sum_{j=1}^{N} \log\left(1 + \exp\left(-y_j (\mathbf{w}^T \mathbf{x}_j + b)\right)\right)$$
   Where $C = 3.0$ provides balanced regularization, penalizing overfitting while maintaining responsiveness to subtle threat patterns.

#### Dataset Composition (29,113 Verified Samples)
The model was trained on an aggregated, sanitized, and deduplicated multi-source corpus:
* **Kaggle Official Phishing Emails**: 18,000+ real-world malicious emails paired with legitimate newsletters.
* **Enron Corporate Email Corpus**: Authentic corporate discussions, business memos, and technical exchanges serving as the gold standard for legitimate (Ham) communication.
* **UCI & Kaggle SMS Spam/Smishing Collection**: 5,500+ mobile chat and SMS messages covering lottery scams, promo spam, and malicious links.
* **Dr. Jose Nazario Phishing Corpus**: Internationally recognized academic dataset of targeted spear-phishing campaigns.
* **Modern Curated Threat Patterns**: 2026-era specific attack vectors including UPI refund fraud, electricity disconnection threats, crypto wallet drainers, and fake WhatsApp Web session alerts.

#### Production Performance Metrics (20% Holdout Test Set)
* **Accuracy**: **96.84%**
* **Precision**: **95.42%** (minimizes disruptive false positives on benign corporate messages)
* **Recall**: **97.10%** (critical security metric: catches 97 out of 100 actual attacks)
* **F1-Score**: **0.9625**
* **ROC-AUC**: **0.9891** (near-perfect area under the receiver operating characteristic curve)

---

### 3.2. Mobile Smishing & Callback Pattern Engine (`phone_detector.py`)

Attackers frequently bypass web filters by initiating **Callback Phishing** (e.g., *"Your power will be cut tonight. Call officer at +91-9876543210"*). This engine evaluates three distinct dimensions:

1. **ITU-T E.164 Geopolitical Risk Analysis**:
   Maps phone country codes against known syndicates and cybercrime corridors:
   - `+855` (Cambodia) / `+95` (Myanmar) / `+856` (Laos): Southeast Asian forced-labor cyber compounds (+60 Risk).
   - `+234` (Nigeria): Advance-fee fraud, task scams, Telegram investment schemes (+55 Risk).
   - `+92` (Pakistan): WhatsApp lottery fraud / KBC impersonation schemes (+55 Risk).
   - `+4470` (UK Personal Numbering Service): Premium-rate callback traps designed to run up caller tolls (+50 Risk).

2. **Institutional Mismatch Heuristic**:
   Public utilities, major banks (SBI, HDFC, Chase, ICICI), and tax agencies (IRS, Income Tax) **never** dispatch urgent operational warnings referencing personal 10-digit mobile numbers. If institutional keywords (`electricity`, `power cut`, `kyc`, `bank account`, `customs`) coincide with a personal telephone number, a severe risk penalty (+60 to +80) is applied.

3. **Shannon Entropy of Digit Sequences**:
   Calculates information entropy over digit distributions to detect automated VoIP-generated or disposable sequential numbers:
   $$H(X) = -\sum_{i=1}^{k} P(x_i) \log_2 P(x_i)$$
   Extremely low entropy (repeated digits like `+1-800-000-0000`) or maximum uniform entropy flags synthetic VoIP routing.

---

### 3.3. Brand Impersonation & Typo-Squatting Engine (`email_detector.py` & `url_detector.py`)

This engine prevents **Business Email Compromise (BEC)** and credential-stealing domain spoofing:

1. **Levenshtein Distance Metric on Brand Registries**:
   Measures the minimum single-character edits (insertions, deletions, substitutions) required to transform a domain into an authoritative brand domain:
   $$D(s_1, s_2) = \begin{cases} 
      \max(i, j) & \text{if } \min(i, j) = 0, \\
      \min \begin{cases} 
         D(i-1, j) + 1 \\ 
         D(i, j-1) + 1 \\ 
         D(i-1, j-1) + \text{cost} 
      \end{cases} & \text{otherwise.}
   \end{cases}$$
   *Example*: `paypa1.com` vs `paypal.com` yields $D = 1$. The engine flags this as a **Critical Typosquatting Signal** (+70 Risk).

2. **Free Webmail Mismatch Analysis**:
   Detects institutional claims dispatched from consumer webmail addresses (e.g., display name *"State Bank of India Security"* sent from `sbi_alert_update@gmail.com`). This mismatch incurs an immediate +70 to +80 risk escalation.

3. **Abuse TLD & Disposable Email Gate**:
   Inspects Top-Level Domains against known abuse registries (`.xyz`, `.top`, `.buzz`, `.icu`, `.tk`, `.rest`) and flags disposable burner email providers (`tempmail.com`, `guerrillamail.com`, `mailinator.com`).

4. **Raw IP Hostname & Credential Paths**:
   Flags raw IPv4 hostnames (`http://192.168.1.1/login`) and sensitive URL targets (`/login`, `/verify`, `/signin`, `/wallet-connect`).

---

### 3.4. Hybrid Explainability Risk Engine (`risk_engine.py`)

The arbitration engine takes outputs from all detectors and executes multi-tiered scoring:

```python
# Multi-Tiered Threat Score Arbitration Formulation:
if url_analyses:
    raw_score = base_risk + (min(hybrid_text_score, max_url_risk) * 0.8) + (sender_risk * 0.3)
    if hybrid_text_score >= 20 and max_url_risk >= 20:
        raw_score += 35 # Compound threat amplification
elif phone_analyses and max_phone_risk >= 50:
    raw_score = max_phone_risk + (hybrid_text_score * 0.4)
else:
    raw_score = (hybrid_text_score * 0.5) + (sender_risk * 0.4)
```

#### Final Output Triaging
* **`SAFE` (Score: 0–39)**: Benign communication. Recommended Action: `SAFE_TO_OPEN`.
* **`SUSPICIOUS` (Score: 40–69)**: Ambiguous signals present (e.g., urgent language without links, or unfamiliar sender). Recommended Action: `WARN_USER`.
* **`CRITICAL` (Score: 70–100)**: Active malicious campaign detected (e.g., typosquatted bank URL + urgency, or institutional mismatch callback). Recommended Action: `BLOCK_ACCESS`.

---

## 4. Deep Cybersecurity Engineering & Threat Vector Analysis

Phishing Shield AI addresses key tactics, techniques, and procedures (TTPs) defined in the **MITRE ATT&CK Framework**:

| MITRE Technique | Attack Description | Phishing Shield AI Defense Mechanism |
| :--- | :--- | :--- |
| **T1566.001** (Spearphishing Attachment) | Malicious links or docs disguised as invoices | Contextual text analysis detects invoice urgency; URL extractor parses target domains. |
| **T1566.002** (Spearphishing Link) | Typosquatted links stealing credentials | Levenshtein distance checks against brand registries; abuse TLD detection. |
| **T1566.003** (Spearphishing via Service) | Messages sent over WhatsApp Web, Telegram | Client DOM MutationObserver intercepts messages directly in browser memory before click. |
| **T1598.003** (Phishing for Information) | KYC update, electricity cut, tax refund scams | Callback trap detection; institutional keyword vs. 10-digit mobile number mismatch. |
| **T1586.002** (Compromised Accounts) | Legitimate accounts used to send scam links | NLP engine evaluates payload semantics regardless of sender reputation. |

---

### 4.1. Defensive Hardening Implementations

#### 1. Denial-of-Service & ReDoS Mitigation
Inbound regex evaluators are vulnerable to Regular Expression Denial of Service (ReDoS) when processing malicious repeating strings. Phishing Shield AI enforces:
- **Hard Request Size Limit**: Middleware terminates any payload exceeding 256 KB (`ContentLengthLimitMiddleware`).
- **Bounded Regex**: All regex patterns use bounded matching and length caps before running evaluations.

#### 2. Defense Against Model Evasion & Zero-Width Obfuscation
Attackers frequently inject zero-width spaces (`\u200B`), invisible non-breaking spaces, or HTML entities to break signature matching. The system applies **aggressive lexical normalization** (`clean_text`):
- HTML tags stripped via standard entity decoding.
- Consecutive whitespaces and newline characters collapsed.
- Unicode homoglyphs converted to base ASCII representations before tokenization.

#### 3. Zero-PII Cryptographic Storage Model
To adhere to GDPR, CCPA, and enterprise confidentiality principles:
- Messages are not stored in raw plaintext inside the persistent database.
- A cryptographic **SHA-256 Fingerprint** is computed over the payload:
  $$\text{Fingerprint} = \text{SHA256}(\text{raw\_text} \,\|\, \text{sender\_id} \,\|\, \text{sorted\_urls})$$
- Only the threat score, verdict, signal breakdown, and timestamp are retained.
- If a duplicate message is received, MongoDB atomically increments `duplicate_count` via `$inc`, preserving storage and providing real-time telemetry on active distributed campaigns.

---

## 5. Complete Technology Stack Matrix

| Component Layer | Technology / Tool | Version / Spec | Primary Architectural Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | FastAPI | `0.115.x` | High-performance asynchronous REST API framework |
| **ASGI Server** | Uvicorn | `0.32.x` | High-throughput asynchronous HTTP/Websocket server |
| **Runtime Environment** | Python | `3.11.9` | Optimized core execution runtime |
| **Machine Learning** | Scikit-Learn | `1.5.x` | TF-IDF feature extraction & Logistic Regression |
| **Data Processing** | Pandas / NumPy | `2.2.x` | High-speed tabular sanitization and matrix math |
| **Model Persistence** | Joblib | `1.4.x` | High-efficiency disk serialization for compiled models |
| **Database Engine** | MongoDB Atlas | `v7.0+` | Cloud-hosted document database for threat telemetry |
| **Async DB Client** | Motor (PyMongo) | `3.6.x` | Non-blocking async MongoDB driver for AsyncIO |
| **Frontend Framework** | React | `18.2.0` | Reactive component architecture for SOC telemetry |
| **Frontend Bundler** | Vite | `5.0.0` | Next-generation frontend tooling and compilation |
| **Styling Engine** | Tailwind CSS | `3.3.5` | Utility-first responsive dark-mode cyber SOC design |
| **Iconography** | Lucide React | `0.292.0` | Lightweight SVG security indicators |
| **Client Extension** | Manifest V3 | `v3.0` | Service Worker-based browser protection client |
| **Cloud Hosting (API)**| Render | Python 3.11 | Containerized autoscaling FastAPI web service |
| **Cloud Hosting (Web)**| Vercel / GitHub Pages| Static Vite | Global Edge CDN hosting for the React dashboard |
| **Development Tunnel** | Cloudflare Tunnel | `2024.x` | Ephemeral secure ingress tunnel for live demo verification |
