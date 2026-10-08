# Architecture: Phishing Shield AI

## High-Level System Architecture

Phishing Shield AI utilizes a centralized backend API serving multiple edge clients.

```mermaid
graph TD
    subgraph Edge Clients
        C1[React Dashboard]
        C2[Chrome Extension]
        C3[Android Client]
    end

    subgraph Backend
        API[FastAPI Gateway]
        RE[Risk Engine]
        
        subgraph Detection Engines
            TE[Text Detector]
            UE[URL Detector]
            SE[Sender Detector]
            MLE[ML Engine - TF-IDF/LR]
        end
    end
    
    C1 -->|HTTP POST| API
    C2 -->|HTTP POST| API
    C3 -->|HTTP POST| API
    
    API --> RE
    RE --> TE
    RE --> UE
    RE --> SE
    RE --> MLE
```

## Hybrid Detection Model

The core innovation is the Hybrid Risk Engine:
1. **Machine Learning Pipeline:** Utilizes TF-IDF vectorization and Logistic Regression for semantic understanding of text.
2. **Deterministic Heuristics:** Uses rule-based engines (RegEx, string parsing) for URL security and explicit keywords.
3. **Weighting Algorithm:** Combines the highest probability threat vectors into a final 0-100 risk score.
