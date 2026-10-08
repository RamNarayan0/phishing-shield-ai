import collections
import collections.abc
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def apply_dark_theme(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(15, 23, 42)  # Dark slate background

def format_title(title_shape, text):
    title_shape.text = text
    title_shape.top = Inches(0.4)
    for p in title_shape.text_frame.paragraphs:
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.font.name = "Arial"
        p.font.size = Pt(28)
        p.font.bold = True
        p.alignment = PP_ALIGN.LEFT

def add_box(slide, text, left, top, width, height, bg_color=RGBColor(30, 41, 59), font_size=14, bold=False):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = RGBColor(51, 65, 85)
    
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = RGBColor(240, 248, 255)
    p.font.bold = bold
    p.alignment = PP_ALIGN.CENTER
    return shape

def add_text(slide, text, left, top, width, height, font_size=16, color=RGBColor(200, 210, 225), bold=False):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    return txBox

def create_presentation():
    prs = Presentation()
    
    # Use blank layout for complete control
    blank_layout = prs.slide_layouts[6]
    title_layout = prs.slide_layouts[5]

    # --- SLIDE 1: Title ---
    slide = prs.slides.add_slide(blank_layout)
    apply_dark_theme(slide)
    add_text(slide, "SHIELD AI", Inches(0.5), Inches(1), Inches(8), Inches(1), font_size=44, color=RGBColor(255,255,255), bold=True)
    add_text(slide, "Multi-channel intelligent phishing\ndetection with explainable risk scoring", Inches(0.5), Inches(2), Inches(8), Inches(1), font_size=20, color=RGBColor(148, 163, 184))
    
    add_text(slide, "Tomorrow's demo strategy\nSelect single live content, explain the\nthreat, and show exactly how the decision was\ncomputed.", Inches(0.5), Inches(5), Inches(5), Inches(1.5), font_size=14, color=RGBColor(56, 189, 248))

    # --- SLIDE 2: Problem ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "The problem is not just the link")
    add_text(slide, "Phishing follows the user across channels.", Inches(0.5), Inches(1.5), Inches(9), Inches(0.5), font_size=24, color=RGBColor(255,255,255), bold=True)
    add_text(slide, "A user may encounter the same social engineering attack as a message,\nemail, notification, or browser link. The hard part is recognizing the\npattern before the user acts.", Inches(0.5), Inches(2.2), Inches(9), Inches(1))
    
    add_box(slide, "ANDROID NOTIFICATIONS", Inches(0.5), Inches(3.5), Inches(2), Inches(1), bg_color=RGBColor(6, 78, 59))
    add_box(slide, "CHROME / WEB", Inches(2.8), Inches(3.5), Inches(2), Inches(1), bg_color=RGBColor(12, 74, 110))
    add_box(slide, "EMAIL", Inches(5.1), Inches(3.5), Inches(2), Inches(1), bg_color=RGBColor(127, 29, 29))
    add_box(slide, "SMS", Inches(7.4), Inches(3.5), Inches(2), Inches(1), bg_color=RGBColor(69, 26, 3))
    
    add_text(slide, "Human weakness is the common attack surface.\nThe prototype therefore focuses on automated, explainable detection instead of\nforcing the user to manually inspect every message.", Inches(0.5), Inches(5.5), Inches(9), Inches(1), font_size=16)

    # --- SLIDE 3: Detection Core ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "One detection core, multiple input edges")
    add_box(slide, "ANDROID NOTIFICATIONS", Inches(0.5), Inches(2), Inches(2.5), Inches(0.8))
    add_box(slide, "CHROME / WEB", Inches(0.5), Inches(3.2), Inches(2.5), Inches(0.8))
    add_box(slide, "EMAIL / API", Inches(0.5), Inches(4.4), Inches(2.5), Inches(0.8))
    
    add_box(slide, "FASTAPI CENTRAL BACKEND\n\n- TEXT ENGINE\n- URL ENGINE\n- SENDER / CONTEXT", Inches(3.5), Inches(2), Inches(3.5), Inches(3.2), bg_color=RGBColor(15, 23, 42))
    
    add_box(slide, "CRITICAL\n92 / 100", Inches(7.5), Inches(3.2), Inches(2), Inches(1), bg_color=RGBColor(153, 27, 27), font_size=20, bold=True)
    
    add_text(slide, "Design principle: Ingest once -> analyze consistently -> explain the decision.", Inches(0.5), Inches(6), Inches(9), Inches(0.5), font_size=16, color=RGBColor(255, 255, 255))

    # --- SLIDE 4: End-to-end architecture ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "End-to-end architecture")
    cols = ["INPUT EDGES", "DETECTION", "MACHINE LEARNING", "VERDICT"]
    for i, col in enumerate(cols):
        add_text(slide, col, Inches(0.5 + i*2.3), Inches(1.5), Inches(2), Inches(0.5), font_size=14, bold=True, color=RGBColor(56,189,248))
    
    # Layer 1
    add_box(slide, "Android Notification", Inches(0.5), Inches(2.2), Inches(2.1), Inches(0.8))
    add_box(slide, "Text Analysis", Inches(2.8), Inches(2.2), Inches(2.1), Inches(0.8))
    add_box(slide, "TF-IDF + Logistic Regression", Inches(5.1), Inches(2.2), Inches(2.1), Inches(0.8))
    add_box(slide, "Explainable Verdict", Inches(7.4), Inches(2.2), Inches(2.1), Inches(0.8))
    # Layer 2
    add_box(slide, "Chrome / DOM Web", Inches(0.5), Inches(3.2), Inches(2.1), Inches(0.8))
    add_box(slide, "URL Extraction", Inches(2.8), Inches(3.2), Inches(2.1), Inches(0.8))
    add_box(slide, "URL Heuristics", Inches(5.1), Inches(3.2), Inches(2.1), Inches(0.8))
    add_box(slide, "SAFE / CRITICAL", Inches(7.4), Inches(3.2), Inches(2.1), Inches(0.8))
    
    add_text(slide, "The same verdict context is used by every client edge.", Inches(0.5), Inches(6), Inches(9), Inches(0.5), font_size=16)

    # --- SLIDE 5: What the prototype can receive ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "What the prototype can receive")
    
    add_box(slide, "ANDROID NOTIFICATIONS\n\nReceives notification events via\nNotificationListenerService. The message\nis extracted securely without direct app\ndatabase access.", Inches(0.5), Inches(2), Inches(2.8), Inches(2.5), bg_color=RGBColor(6, 78, 59))
    add_box(slide, "CHROME / WEB\n\nA browser extension observing\nDOM elements. Extracts visible text\nand links on suspicious pages.", Inches(3.6), Inches(2), Inches(2.8), Inches(2.5), bg_color=RGBColor(12, 74, 110))
    add_box(slide, "EMAIL / GMAIL API\n\nAuthorized OAuth access to messages.\nThe payload structure remains the\nsame for the risk engine.", Inches(6.7), Inches(2), Inches(2.8), Inches(2.5), bg_color=RGBColor(30, 41, 59))

    # --- SLIDE 6: The detection pipeline ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "The detection pipeline")
    
    steps = ["RAW PAYLOAD", "EXTRACT URLS", "ANALYZE TEXT", "ML + HEURISTICS", "RISK SCORE", "EXPLAIN + ALERT"]
    for i, step in enumerate(steps):
        add_box(slide, step, Inches(0.2 + i*1.6), Inches(3), Inches(1.4), Inches(1), bg_color=RGBColor(15, 23, 42), font_size=11, bold=True)
        if i < len(steps)-1:
            add_text(slide, "→", Inches(1.6 + i*1.6), Inches(3.3), Inches(0.2), Inches(0.5), font_size=20, color=RGBColor(56,189,248))
            
    add_text(slide, "Why this matters: A single suspicious keyword should not decide the case. The\nsystem combines independent signals so the final verdict is based on a richer\nthreat pattern.", Inches(0.5), Inches(5), Inches(9), Inches(1))

    # --- SLIDE 7: Machine Learning ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "Machine learning: a lightweight, explainable baseline")
    
    add_box(slide, "Raw Text\n↓\nTF-IDF Vectorizer\n↓\nLogistic Regression\n↓\nProbability Score", Inches(0.5), Inches(2), Inches(4), Inches(4))
    
    add_text(slide, "WHY TF-IDF?", Inches(5), Inches(2), Inches(4), Inches(0.3), font_size=12, bold=True, color=RGBColor(56,189,248))
    add_text(slide, "Transforms text into a numerical feature representation without requiring a massive deep learning framework.", Inches(5), Inches(2.3), Inches(4.5), Inches(0.6), font_size=12)
    
    add_text(slide, "WHY LOGISTIC REGRESSION?", Inches(5), Inches(3.1), Inches(4), Inches(0.3), font_size=12, bold=True, color=RGBColor(56,189,248))
    add_text(slide, "Provides a fast, CPU-friendly probability score. Perfect for local/prototype environments.", Inches(5), Inches(3.4), Inches(4.5), Inches(0.6), font_size=12)
    
    add_text(slide, "EVALUATION PIPELINE", Inches(5), Inches(4.2), Inches(4), Inches(0.3), font_size=12, bold=True, color=RGBColor(56,189,248))
    add_text(slide, "Machine learning provides the classification score, but it is one signal in the final risk engine. This prevents false positives on safe messages.", Inches(5), Inches(4.5), Inches(4.5), Inches(1), font_size=12)

    # --- SLIDE 8: URL Security ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "URL security is a second line of defense")
    
    add_box(slide, "https://secure-bank-login-example.com/verify", Inches(0.5), Inches(2), Inches(9), Inches(0.8), bg_color=RGBColor(30,41,59), font_size=18)
    
    add_box(slide, "HTTPS STATUS\nChecks TLS/SSL presence", Inches(0.5), Inches(3.5), Inches(2.1), Inches(1.2), bg_color=RGBColor(15,23,42), font_size=12)
    add_box(slide, "DOMAIN STRUCTURE\nLength / Hyphens / Subdomains", Inches(2.8), Inches(3.5), Inches(2.1), Inches(1.2), bg_color=RGBColor(15,23,42), font_size=12)
    add_box(slide, "PATH\nLogin, verify, credential terms", Inches(5.1), Inches(3.5), Inches(2.1), Inches(1.2), bg_color=RGBColor(15,23,42), font_size=12)
    add_box(slide, "SUSPICIOUS\nCredential-oriented indicators", Inches(7.4), Inches(3.5), Inches(2.1), Inches(1.2), bg_color=RGBColor(15,23,42), font_size=12)
    
    add_text(slide, "Important: A safe domain does not mean safe intent if it belongs to a known host. The engine combines URL and Text signals.", Inches(0.5), Inches(6), Inches(9), Inches(0.5), font_size=14, color=RGBColor(148,163,184))

    # --- SLIDE 9: Risk Score ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "From independent signals to one risk score")
    
    add_box(slide, "91\nCRITICAL", Inches(1), Inches(2.5), Inches(2.5), Inches(2.5), font_size=32, bg_color=RGBColor(15,23,42), bold=True)
    
    add_text(slide, "HYBRID DECISION", Inches(4.5), Inches(2), Inches(5), Inches(0.5), font_size=16, bold=True, color=RGBColor(56,189,248))
    add_text(slide, "Text ML Probability .......................... 0.91\n\nURL risk signals ............................... High\n\nSender/Context signals ................... Unknown\n\nFinal normalized score ................... 91 / 100", Inches(4.5), Inches(3), Inches(5), Inches(2), font_size=16)
    
    add_text(slide, "Design rule: Avoid double-counting the same signal and cap the score at 100.", Inches(0.5), Inches(6), Inches(9), Inches(0.5), font_size=14)

    # --- SLIDE 10: Explainability ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "Explainability turns a classifier into a security tool")
    
    add_box(slide, "CRITICAL\n91 / 100\n\n✓ Urgent language\n✓ Financial context\n✓ Account suspension threat\n✓ Credential request\n✓ Suspicious URL", Inches(0.5), Inches(2), Inches(5), Inches(3.5), bg_color=RGBColor(30,41,59))
    
    add_box(slide, "WHY EXPLAINABILITY?\n\nThe user and the system can see\nexactly which features contributed to the\nverdict, instead of accepting the\ndecision from a black-box AI.", Inches(6), Inches(2), Inches(3.5), Inches(2), bg_color=RGBColor(12,74,110), font_size=12)
    add_box(slide, "RECOMMENDED ACTION\nDO NOT OPEN", Inches(6), Inches(4.5), Inches(3.5), Inches(1), bg_color=RGBColor(153,27,27), bold=True)

    # --- SLIDE 11: Chrome Extension ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "Browser safety net: same brain, different edge")
    
    add_box(slide, "Phishing Shield AI (Chrome Extension)\n\n🚨 SECURITY ALERT\nYour account has been suspended. Verify:\nhttps://secure-bank-login-example.com/verify", Inches(1), Inches(2), Inches(4.5), Inches(3), bg_color=RGBColor(255,255,255), font_size=12)
    add_box(slide, "CRITICAL\n91 / 100", Inches(6), Inches(2.5), Inches(2), Inches(2), bg_color=RGBColor(153,27,27), font_size=20, bold=True)
    
    add_text(slide, "For the prototype, use a controlled demo page for a reliable live recording.", Inches(0.5), Inches(6), Inches(9), Inches(1), font_size=14)

    # --- SLIDE 12: Android ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "Android: notification-level ingestion")
    
    add_box(slide, "Notification event", Inches(0.5), Inches(2), Inches(4), Inches(0.6), bg_color=RGBColor(15,23,42))
    add_box(slide, "Listener service", Inches(0.5), Inches(2.8), Inches(4), Inches(0.6), bg_color=RGBColor(15,23,42))
    add_box(slide, "Payload extraction", Inches(0.5), Inches(3.6), Inches(4), Inches(0.6), bg_color=RGBColor(15,23,42))
    add_box(slide, "REST API", Inches(0.5), Inches(4.4), Inches(4), Inches(0.6), bg_color=RGBColor(15,23,42))
    
    add_text(slide, "Prototype boundary: notification context, not decrypted app databases.", Inches(0.5), Inches(6), Inches(9), Inches(1), font_size=14)

    # --- SLIDE 13: Technology Stack ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "Technology stack — what each layer is doing")
    
    stacks = [
        ("FRONTEND", "- React\n- Vite\n- Tailwind CSS"),
        ("BACKEND", "- Python\n- FastAPI\n- Pydantic"),
        ("ML", "- scikit-learn\n- TF-IDF\n- Logistic Regression"),
        ("BROWSER", "- Chrome Extension\n- Manifest V3\n- Content Scripts"),
        ("ANDROID", "- Android SDK\n- NotificationListenerService\n- REST Client"),
        ("DATA", "- SQLite\n- JSON\n- CSV dataset")
    ]
    
    for i, (layer, tech) in enumerate(stacks):
        x = 0.5 + (i % 3) * 3
        y = 2 + (i // 3) * 2
        add_box(slide, f"{layer}\n\n{tech}", Inches(x), Inches(y), Inches(2.8), Inches(1.5), bg_color=RGBColor(15,23,42), font_size=12)

    # --- SLIDE 14: Protocols ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "Protocols and standards — where the data moves")
    
    protocols = [
        ("HTTP / REST", "Client -> FastAPI"),
        ("JSON", "Payload serialization"),
        ("HTTPS / TLS", "Encrypt production transport"),
        ("OAuth 2.0", "Authorized Gmail API access"),
        ("DNS", "Resolves domain records for URL analysis")
    ]
    
    for i, (proto, desc) in enumerate(protocols):
        add_text(slide, proto, Inches(0.5), Inches(2 + i*0.7), Inches(2.5), Inches(0.5), font_size=14, bold=True, color=RGBColor(56,189,248))
        add_text(slide, desc, Inches(3.5), Inches(2 + i*0.7), Inches(5), Inches(0.5), font_size=14)
        
    add_text(slide, "Current prototype uses HTTP/REST + JSON for local execution. The real production path requires HTTPS/TLS.", Inches(0.5), Inches(6), Inches(9), Inches(0.5), font_size=12)

    # --- SLIDE 15: Security & Privacy ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "Security and privacy are part of the design")
    
    add_box(slide, "Least privilege\nThe system does not require root access or decryption of app databases.", Inches(0.5), Inches(1.8), Inches(9), Inches(0.7), bg_color=RGBColor(15,23,42), font_size=12)
    add_box(slide, "No secrets in code\nEnvironment variables manage API keys.", Inches(0.5), Inches(2.7), Inches(9), Inches(0.7), bg_color=RGBColor(15,23,42), font_size=12)
    add_box(slide, "Minimal retention\nMessage content is analyzed and scored. No long-term storage.", Inches(0.5), Inches(3.6), Inches(9), Inches(0.7), bg_color=RGBColor(15,23,42), font_size=12)
    add_box(slide, "Transport security\nProduction deployments encrypt all API payloads over HTTPS.", Inches(0.5), Inches(4.5), Inches(9), Inches(0.7), bg_color=RGBColor(15,23,42), font_size=12)
    add_box(slide, "Client isolation\nEach endpoint integrates via standard schemas.", Inches(0.5), Inches(5.4), Inches(9), Inches(0.7), bg_color=RGBColor(15,23,42), font_size=12)

    # --- SLIDE 16: Claims ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "What this prototype can and cannot claim")
    
    add_box(slide, "CAN DEMONSTRATE\n\nReal-time event stream analysis, heuristic detection, URL extraction, and explainable ML scoring.", Inches(0.5), Inches(2), Inches(4.3), Inches(2.5), bg_color=RGBColor(6,78,59))
    add_box(slide, "DOES NOT GUARANTEE\n\nZero-day production accuracy, interception of encrypted traffic, or replacing commercial antivirus software.", Inches(5.2), Inches(2), Inches(4.3), Inches(2.5), bg_color=RGBColor(153,27,27))
    
    add_text(slide, "Prototype ML baseline: Small synthetic dataset -> useful proof of pipeline, not a production benchmark.", Inches(0.5), Inches(5.5), Inches(9), Inches(0.5), font_size=14, color=RGBColor(255,255,255))

    # --- SLIDE 17: Demonstration ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "Tomorrow's 3-minute live demonstration")
    
    add_box(slide, "SAFE MESSAGE\n'Hey, are you coming to college tomorrow?' -> SAFE", Inches(0.5), Inches(2), Inches(9), Inches(1), bg_color=RGBColor(6,78,59))
    add_box(slide, "SUSPICIOUS\n'Account requires verification...' -> SUSPICIOUS", Inches(0.5), Inches(3.2), Inches(9), Inches(1), bg_color=RGBColor(180,83,9))
    add_box(slide, "BANK PHISHING\n'URGENT bank suspension. Verify at secure-bank-login.com' -> CRITICAL", Inches(0.5), Inches(4.4), Inches(9), Inches(1), bg_color=RGBColor(153,27,27))
    
    add_text(slide, "Live event flow: Payload -> JSON -> API -> URL / ML / Text -> Risk Engine -> Dashboard Warning", Inches(0.5), Inches(6), Inches(9), Inches(0.5), font_size=14, color=RGBColor(56,189,248), bold=True)

    # --- SLIDE 18: Roadmap ---
    slide = prs.slides.add_slide(title_layout)
    apply_dark_theme(slide)
    format_title(slide.shapes.title, "Roadmap: from prototype to production research")
    
    add_box(slide, "NOW\n\nTF-IDF + Logistic Regression\nURL Heuristics\nEvent-Driven Dashboard", Inches(0.5), Inches(2), Inches(2.8), Inches(2.5), bg_color=RGBColor(30,41,59))
    add_box(slide, "NEXT\n\nTransformer NLP (BERT)\nLarger labelled datasets\nThreat intelligence", Inches(3.6), Inches(2), Inches(2.8), Inches(2.5), bg_color=RGBColor(12,74,110))
    add_box(slide, "LATER\n\nGraph-based URL relationships\nFederated learning\nEnterprise gateway", Inches(6.7), Inches(2), Inches(2.8), Inches(2.5), bg_color=RGBColor(88,28,135))
    
    add_text(slide, "The research question is answered: How do we build lightweight, explainable detection that balances accuracy, privacy and latency at the edge?", Inches(0.5), Inches(5.5), Inches(9), Inches(1), font_size=12)

    # Save
    prs.save("docs/presentation/Phishing_Shield_AI.pptx")

    print("Created docs/presentation/Phishing_Shield_AI.pptx successfully!")

if __name__ == '__main__':
    create_presentation()
