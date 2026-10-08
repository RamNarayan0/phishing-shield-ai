# Protocols & Methodology

## 1. Transport & Network Protocols
- **HTTP/1.1**: Serves as the primary application protocol for client-server communication.
- **REST (Representational State Transfer)**: Architectural style defining the API endpoints (`/api/verify-message`).
- **IPv4**: Addressing protocol utilized for LAN-based network discovery and testing.

## 2. Security Protocols (Production)
- **HTTPS/TLS**: Required in production environments to encrypt payloads.
- **OAuth 2.0**: The industry-standard protocol for authorization, utilized if integrating directly with email providers (e.g., Gmail API).

## 3. Machine Learning Methodology
- **Algorithm**: Logistic Regression
- **Feature Extraction**: Term Frequency-Inverse Document Frequency (TF-IDF)
- **Training Paradigm**: Supervised classification (Binary: 0 for Safe, 1 for Phishing)
- **Advantages**: Deterministic execution time, minimal CPU overhead, easily explainable weights compared to deep neural networks.

## 4. Data Serialization
- **JSON (JavaScript Object Notation)**: Standard payload format for request and response cycles. Validated statically using Pydantic.
