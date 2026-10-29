import collections
import collections.abc
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── colour palette ──────────────────────────────────────────────
BG_DARK   = RGBColor(15, 23, 42)     # slide background
CARD_DARK = RGBColor(30, 41, 59)     # card background
CARD_ALT  = RGBColor(15, 23, 42)     # alternate card
ACCENT    = RGBColor(56, 189, 248)   # cyan accent
WHITE     = RGBColor(255, 255, 255)
MUTED     = RGBColor(148, 163, 184)  # muted grey
TEXT_BODY = RGBColor(200, 210, 225)
GREEN_BG  = RGBColor(6, 78, 59)
BLUE_BG   = RGBColor(12, 74, 110)
RED_BG    = RGBColor(153, 27, 27)
ORANGE_BG = RGBColor(180, 83, 9)
PURPLE_BG = RGBColor(88, 28, 135)
BORDER    = RGBColor(51, 65, 85)

# ── helpers ─────────────────────────────────────────────────────
def dark_bg(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG_DARK

def add_title(slide, text, top=Inches(0.3)):
    txBox = slide.shapes.add_textbox(Inches(0.6), top, Inches(8.8), Inches(0.7))
    tf = txBox.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(30); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = "Arial"
    p.alignment = PP_ALIGN.LEFT

def add_subtitle(slide, text, top=Inches(1.0)):
    txBox = slide.shapes.add_textbox(Inches(0.6), top, Inches(8.8), Inches(0.5))
    tf = txBox.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(16); p.font.color.rgb = MUTED
    p.font.name = "Arial"

def add_slide_num(slide, num, total):
    txBox = slide.shapes.add_textbox(Inches(8.5), Inches(7.0), Inches(1.3), Inches(0.4))
    p = txBox.text_frame.paragraphs[0]
    p.text = f"{num} / {total}"
    p.font.size = Pt(10); p.font.color.rgb = MUTED
    p.alignment = PP_ALIGN.RIGHT

def card(slide, text, left, top, width, height,
         bg=CARD_DARK, font_size=13, bold=False, align=PP_ALIGN.LEFT, font_color=TEXT_BODY):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid(); shape.fill.fore_color.rgb = bg
    shape.line.color.rgb = BORDER; shape.line.width = Pt(1)
    tf = shape.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.15); tf.margin_right = Inches(0.15)
    tf.margin_top = Inches(0.1); tf.margin_bottom = Inches(0.1)
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size); p.font.color.rgb = font_color
    p.font.bold = bold; p.alignment = align
    return shape

def text_block(slide, text, left, top, width, height,
               font_size=14, color=TEXT_BODY, bold=False, align=PP_ALIGN.LEFT):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size); p.font.color.rgb = color
    p.font.bold = bold; p.alignment = align; p.font.name = "Arial"
    return txBox

def accent_bar(slide, left, top, width=Inches(0.06), height=Inches(0.6), color=ACCENT):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid(); shape.fill.fore_color.rgb = color
    shape.line.fill.background()

def arrow_right(slide, left, top):
    text_block(slide, "→", left, top, Inches(0.3), Inches(0.5),
               font_size=22, color=ACCENT, bold=True, align=PP_ALIGN.CENTER)

# ── build presentation ─────────────────────────────────────────
def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    TOTAL = 18

    # ════════════════════════════════════════════════════════════
    # SLIDE 1 — Title
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    # accent line
    shape = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(2.0), Inches(0.08), Inches(2.0))
    shape.fill.solid(); shape.fill.fore_color.rgb = ACCENT; shape.line.fill.background()

    text_block(s, "PHISHING SHIELD AI", Inches(0.9), Inches(1.8), Inches(8), Inches(0.8),
               font_size=42, color=WHITE, bold=True)
    text_block(s, "Real-Time AI-Powered Phishing Detection\n& Explainable Cybersecurity Risk Scoring",
               Inches(0.9), Inches(2.6), Inches(7), Inches(1.0), font_size=20, color=MUTED)

    card(s, "🌐 Chrome Extension    🖥️ Web Dashboard    🔬 4 ML Models    📊 Explainable AI",
         Inches(0.9), Inches(4.2), Inches(8), Inches(0.7), bg=CARD_ALT, font_size=14,
         bold=True, align=PP_ALIGN.CENTER, font_color=ACCENT)

    text_block(s, "B.Tech CSE Cybersecurity — Final Year Project",
               Inches(0.9), Inches(5.6), Inches(8), Inches(0.4), font_size=14, color=MUTED)
    add_slide_num(s, 1, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 2 — Problem Statement
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "The Problem")
    add_subtitle(s, "Phishing is not just an email problem — it follows users across every channel")

    items = [
        ("📧 Email", "Spoofed sender names, fake bank alerts, credential-harvesting links", RED_BG),
        ("📱 SMS / WhatsApp", "Smishing attacks with urgent calls-to-action and callback traps", ORANGE_BG),
        ("🌐 Web / Browser", "Typosquatting domains, fake login pages, obfuscated URLs", BLUE_BG),
        ("📞 Phone / Vishing", "Lottery call scams from +92/+44 prefixes impersonating officials", PURPLE_BG),
    ]
    for i, (title, desc, bg) in enumerate(items):
        y = Inches(1.8 + i * 1.2)
        card(s, f"{title}\n{desc}", Inches(0.6), y, Inches(8.8), Inches(1.0), bg=bg, font_size=13)

    text_block(s, "Human psychology is the attack surface. Automated, explainable detection is the answer.",
               Inches(0.6), Inches(6.6), Inches(9), Inches(0.5), font_size=13, color=ACCENT, bold=True)
    add_slide_num(s, 2, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 3 — System Workflow
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "How It Works — Step by Step")

    steps = [
        ("Step 1", "User submits message\nvia Web Dashboard or\nChrome Extension"),
        ("Step 2", "FastAPI backend receives\npayload, enforces 256 KB\nsize limit & headers"),
        ("Step 3", "Multi-vector analysis:\nText ML + URL scanner +\nPhone + Email engines"),
        ("Step 4", "Hybrid Risk Engine\ncalculates weighted\nscore (0–100)"),
        ("Step 5", "Explainable verdict\nreturned with detected\nthreat signals"),
    ]
    for i, (label, desc) in enumerate(steps):
        x = Inches(0.3 + i * 1.9)
        card(s, label, x, Inches(1.8), Inches(1.7), Inches(0.5),
             bg=ACCENT, font_size=12, bold=True, align=PP_ALIGN.CENTER, font_color=BG_DARK)
        card(s, desc, x, Inches(2.4), Inches(1.7), Inches(1.6),
             bg=CARD_DARK, font_size=11, align=PP_ALIGN.CENTER)
        if i < len(steps) - 1:
            arrow_right(s, Inches(2.0 + i * 1.9), Inches(3.0))

    card(s, "Design Principle: Ingest once → Analyze consistently → Explain the decision → Never store raw PII",
         Inches(0.6), Inches(5.0), Inches(8.8), Inches(0.6), bg=CARD_ALT, font_size=12, font_color=ACCENT, bold=True, align=PP_ALIGN.CENTER)
    add_slide_num(s, 3, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 4 — System Architecture
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "End-to-End Architecture")

    # Column headers
    cols = ["INPUT SOURCES", "PROCESSING", "ML & RULES", "OUTPUT"]
    for i, c in enumerate(cols):
        text_block(s, c, Inches(0.4 + i * 2.4), Inches(1.5), Inches(2.2), Inches(0.4),
                   font_size=12, color=ACCENT, bold=True, align=PP_ALIGN.CENTER)

    # Row 1
    card(s, "Chrome Extension\n(DOM Scanner)", Inches(0.4), Inches(2.1), Inches(2.2), Inches(0.9), font_size=11, align=PP_ALIGN.CENTER)
    card(s, "Text Normalization\n& URL Extraction", Inches(2.8), Inches(2.1), Inches(2.2), Inches(0.9), font_size=11, align=PP_ALIGN.CENTER)
    card(s, "TF-IDF + Logistic\nRegression (NLP)", Inches(5.2), Inches(2.1), Inches(2.2), Inches(0.9), font_size=11, align=PP_ALIGN.CENTER)
    card(s, "Risk Score\n0 – 100", Inches(7.6), Inches(2.1), Inches(2.0), Inches(0.9),
         bg=RED_BG, font_size=13, bold=True, align=PP_ALIGN.CENTER, font_color=WHITE)

    # Row 2
    card(s, "Web Dashboard\n(React + Vite)", Inches(0.4), Inches(3.2), Inches(2.2), Inches(0.9), font_size=11, align=PP_ALIGN.CENTER)
    card(s, "Phone Number\n& Sender Analysis", Inches(2.8), Inches(3.2), Inches(2.2), Inches(0.9), font_size=11, align=PP_ALIGN.CENTER)
    card(s, "URL Heuristic\nEngine", Inches(5.2), Inches(3.2), Inches(2.2), Inches(0.9), font_size=11, align=PP_ALIGN.CENTER)
    card(s, "Explainable\nVerdict", Inches(7.6), Inches(3.2), Inches(2.0), Inches(0.9),
         bg=GREEN_BG, font_size=13, bold=True, align=PP_ALIGN.CENTER, font_color=WHITE)

    # Row 3
    card(s, "REST API\n(SIEM / Webhook)", Inches(0.4), Inches(4.3), Inches(2.2), Inches(0.9), font_size=11, align=PP_ALIGN.CENTER)
    card(s, "Email Spoofing\nDetection", Inches(2.8), Inches(4.3), Inches(2.2), Inches(0.9), font_size=11, align=PP_ALIGN.CENTER)
    card(s, "Hybrid Risk\nArbitration Engine", Inches(5.2), Inches(4.3), Inches(2.2), Inches(0.9), font_size=11, align=PP_ALIGN.CENTER)
    card(s, "Recommended\nAction", Inches(7.6), Inches(4.3), Inches(2.0), Inches(0.9),
         bg=BLUE_BG, font_size=13, bold=True, align=PP_ALIGN.CENTER, font_color=WHITE)

    # Arrows between columns
    for row in range(3):
        y = Inches(2.4 + row * 1.1)
        for col in range(3):
            arrow_right(s, Inches(2.55 + col * 2.4), y)

    add_slide_num(s, 4, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 5 — ML Model 1: Primary NLP Classifier
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "ML Model 1 — Primary NLP Text Classifier")
    add_subtitle(s, "TF-IDF Vectorization + L2-Regularized Logistic Regression")

    # Pipeline boxes
    pipeline = ["Raw Text", "Clean &\nTokenize", "TF-IDF\nVectorizer", "Logistic\nRegression", "Probability\n(0.0 – 1.0)"]
    for i, step in enumerate(pipeline):
        card(s, step, Inches(0.3 + i * 1.9), Inches(1.8), Inches(1.7), Inches(1.0),
             bg=CARD_ALT if i % 2 == 0 else CARD_DARK, font_size=12, bold=True, align=PP_ALIGN.CENTER, font_color=WHITE)
        if i < len(pipeline) - 1:
            arrow_right(s, Inches(2.0 + i * 1.9), Inches(2.1))

    # Stats
    metrics = [
        ("Accuracy", "96.84%"),
        ("Precision", "95.42%"),
        ("Recall", "97.10%"),
        ("ROC-AUC", "0.9891"),
    ]
    for i, (label, value) in enumerate(metrics):
        x = Inches(0.6 + i * 2.3)
        card(s, f"{label}\n{value}", x, Inches(3.3), Inches(2.0), Inches(0.9),
             bg=CARD_DARK, font_size=14, bold=True, align=PP_ALIGN.CENTER, font_color=ACCENT)

    text_block(s, "Training Dataset: 29,113 verified samples from Kaggle Phishing, Enron, UCI SMS Spam, Nazario archives",
               Inches(0.6), Inches(4.6), Inches(8.8), Inches(0.4), font_size=12, color=MUTED)

    text_block(s, "Why Not Deep Learning?", Inches(0.6), Inches(5.2), Inches(3), Inches(0.3),
               font_size=13, color=ACCENT, bold=True)
    items_text = ("• Predictions in under 15 ms (real-time browser scanning)\n"
                  "• Zero hallucination — pure mathematical classification\n"
                  "• Runs on CPU-only cloud servers, no GPU needed")
    text_block(s, items_text, Inches(0.6), Inches(5.5), Inches(8.8), Inches(1.2), font_size=12, color=TEXT_BODY)
    add_slide_num(s, 5, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 6 — ML Model 2: Phone Scam Classifier
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "ML Model 2 — Smishing & Phone Scam Classifier")
    add_subtitle(s, "phone_pattern_model.pkl — Detects SMS scams and callback fraud traps")

    card(s, "🔍 What It Detects\n\n"
         "• Mobile text scams: \"Your power will be cut tonight!\"\n"
         "• Callback fraud: \"Call our officer at 09876543210\"\n"
         "• KBC lottery scams from +92 / +44 prefixes\n"
         "• VoIP-generated automated numbers",
         Inches(0.6), Inches(1.8), Inches(4.2), Inches(3.0), bg=CARD_DARK, font_size=13)

    card(s, "⚙️ Detection Mechanics\n\n"
         "• Phone number structure analysis (ITU-T E.164)\n"
         "• Digit entropy evaluation for VoIP detection\n"
         "• Institutional keyword + personal number mismatch\n"
         "  (e.g., \"Bank\" paired with 10-digit mobile)\n"
         "• Known cybercrime country code prefixes",
         Inches(5.2), Inches(1.8), Inches(4.4), Inches(3.0), bg=CARD_DARK, font_size=13)

    card(s, "Example: \"URGENT — Your electricity bill is overdue. Call 09123456789 immediately to avoid disconnection.\"\n→ Verdict: CRITICAL (Institutional claim + personal mobile number = callback fraud)",
         Inches(0.6), Inches(5.2), Inches(9.0), Inches(1.0), bg=RED_BG, font_size=12, font_color=WHITE)
    add_slide_num(s, 6, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 7 — ML Model 3: Email Spoofing Classifier
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "ML Model 3 — Email Spoofing Classifier")
    add_subtitle(s, "email_pattern_model.pkl — Detects spoofed senders and Business Email Compromise (BEC)")

    card(s, "🔍 What It Detects\n\n"
         "• Official-sounding names from free email addresses\n"
         "  → \"SBI Security Team\" <sbi.alert@gmail.com>\n"
         "• Disposable / burner email domains\n"
         "  → tempmail.com, mailinator.com, guerrillamail.com\n"
         "• High-abuse Top-Level Domains\n"
         "  → .xyz, .top, .buzz, .icu, .click",
         Inches(0.6), Inches(1.8), Inches(4.2), Inches(3.2), bg=CARD_DARK, font_size=13)

    card(s, "⚙️ How It Works\n\n"
         "• Extracts sender display name & email domain\n"
         "• Cross-checks brand keywords against domain\n"
         "• Flags mismatch: brand claim + free/burner domain\n"
         "• Classifies TLD reputation risk tier\n"
         "• Applies sender trust score to Risk Engine",
         Inches(5.2), Inches(1.8), Inches(4.4), Inches(3.2), bg=CARD_DARK, font_size=13)

    card(s, "Example: From \"HDFC Bank Alert\" <hdfc.verify2024@yahoo.com>\n→ Verdict: CRITICAL (Bank brand name + free webmail domain = spoofed sender)",
         Inches(0.6), Inches(5.4), Inches(9.0), Inches(1.0), bg=RED_BG, font_size=12, font_color=WHITE)
    add_slide_num(s, 7, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 8 — ML Model 4: Hybrid Risk Engine
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "ML Model 4 — Hybrid Risk Arbitration Engine")
    add_subtitle(s, "Combines all models into a single calibrated 0–100 threat score")

    signals = [
        ("Text ML Score", "40–50%", "NLP classifier probability", BLUE_BG),
        ("URL Risk", "Up to 80%", "Typosquatting, raw IP, HTTP", ORANGE_BG),
        ("Phone Pattern", "+15–25", "Callback fraud detection", PURPLE_BG),
        ("Email Spoof", "+20–30", "Sender domain mismatch", RED_BG),
    ]
    for i, (label, weight, desc, bg) in enumerate(signals):
        x = Inches(0.4 + i * 2.4)
        card(s, f"{label}\n\nWeight: {weight}\n{desc}",
             x, Inches(1.8), Inches(2.2), Inches(1.6), bg=bg, font_size=12, bold=False,
             align=PP_ALIGN.CENTER, font_color=WHITE)

    card(s, "Compound Escalation Rule\n\nIf text panic language AND suspicious URL are BOTH present → automatic +35 point amplification penalty.\n"
         "If confirmed brand spoofing or toll-fraud callback → immediate CRITICAL override.",
         Inches(0.6), Inches(3.8), Inches(8.8), Inches(1.3), bg=CARD_ALT, font_size=12, font_color=WHITE)

    # Score bands
    bands = [("SAFE", "0 – 39", GREEN_BG), ("SUSPICIOUS", "40 – 69", ORANGE_BG), ("CRITICAL", "70 – 100", RED_BG)]
    for i, (label, rng, bg) in enumerate(bands):
        card(s, f"{label}  ({rng})", Inches(0.6 + i * 3.1), Inches(5.5), Inches(2.9), Inches(0.6),
             bg=bg, font_size=14, bold=True, align=PP_ALIGN.CENTER, font_color=WHITE)
    add_slide_num(s, 8, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 9 — URL Security Engine
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "URL Security Engine")
    add_subtitle(s, "Structural heuristics that catch zero-day phishing domains before blacklists")

    card(s, "https://secure-bank-login-example.com/verify-account",
         Inches(0.6), Inches(1.8), Inches(8.8), Inches(0.6), bg=CARD_DARK, font_size=16,
         bold=True, align=PP_ALIGN.CENTER, font_color=RGBColor(239, 68, 68))

    checks = [
        ("HTTPS Status", "Checks TLS/SSL\npresence"),
        ("Domain Length", "Long domains with\nexcess hyphens"),
        ("Typosquatting", "Levenshtein distance\nvs trusted brands"),
        ("Path Keywords", "/login, /verify,\n/credential"),
        ("Raw IP Host", "IP address instead\nof domain name"),
    ]
    for i, (label, desc) in enumerate(checks):
        x = Inches(0.3 + i * 1.9)
        card(s, f"{label}\n\n{desc}", x, Inches(2.8), Inches(1.8), Inches(1.5),
             bg=CARD_ALT, font_size=11, align=PP_ALIGN.CENTER, font_color=TEXT_BODY)

    text_block(s, "Why this matters: Static blacklists miss newly registered domains. Structural heuristics catch them within minutes.",
               Inches(0.6), Inches(4.8), Inches(9), Inches(0.4), font_size=13, color=ACCENT, bold=True)
    add_slide_num(s, 9, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 10 — Explainability (XAI)
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "Explainable AI — Why, Not Just What")
    add_subtitle(s, "Every scan shows exactly which signals contributed to the verdict")

    card(s, "🚨 CRITICAL — 91 / 100\n\n"
         "✓ Urgent language pattern detected\n"
         "✓ Financial context (\"account suspended\")\n"
         "✓ Credential request (\"verify your identity\")\n"
         "✓ Suspicious URL with typosquatting\n"
         "✓ Unverified sender domain\n\n"
         "Recommended Action: DO NOT OPEN",
         Inches(0.6), Inches(1.8), Inches(5.0), Inches(4.0), bg=CARD_DARK, font_size=13)

    card(s, "Why Explainability Matters\n\n"
         "• Users see WHY something is flagged\n"
         "  (not just a black-box \"blocked\")\n\n"
         "• Builds trust — users learn threat patterns\n\n"
         "• SOC analysts can validate alerts faster\n\n"
         "• Reduces alert fatigue from false positives\n\n"
         "• GDPR / compliance — transparent decisions",
         Inches(6.0), Inches(1.8), Inches(3.6), Inches(4.0), bg=BLUE_BG, font_size=12, font_color=WHITE)
    add_slide_num(s, 10, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 11 — Cybersecurity Concept 1-3
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "Cybersecurity Concepts (1/3)")

    concepts = [
        ("Social Engineering & Urgency Exploitation",
         "Attackers exploit fear, curiosity, or greed to force rushed decisions.\n"
         "Countermeasure: NLP model detects panic language like \"action required within 2 hours\"."),
        ("Phishing & Spear Phishing",
         "Deceptive messages trick users into revealing passwords, PINs, or credit card numbers.\n"
         "Countermeasure: Evaluates message semantics and sender identity to catch credential harvesting."),
        ("Smishing & Callback Vishing",
         "SMS traps instructing victims to call fake support numbers for manufactured emergencies.\n"
         "Countermeasure: Phone analyzer flags institutional mismatches and known cybercrime prefixes."),
    ]
    for i, (title, desc) in enumerate(concepts):
        y = Inches(1.6 + i * 1.8)
        accent_bar(s, Inches(0.5), y, height=Inches(1.4), color=ACCENT)
        text_block(s, title, Inches(0.8), y, Inches(8.6), Inches(0.3), font_size=15, color=WHITE, bold=True)
        text_block(s, desc, Inches(0.8), Inches(y.inches + 0.35), Inches(8.6), Inches(1.0), font_size=12, color=TEXT_BODY)
    add_slide_num(s, 11, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 12 — Cybersecurity Concept 4-6
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "Cybersecurity Concepts (2/3)")

    concepts = [
        ("Typosquatting & Homoglyph Attacks",
         "Fake domains resembling trusted brands (paypa1.com, goog1e.com).\n"
         "Countermeasure: Levenshtein Distance measures single-character edits against known brand list."),
        ("Zero-Day Threat Interception",
         "New phishing domains bypass static blacklists in the first hours of a campaign.\n"
         "Countermeasure: Structural URL heuristics (raw IP, suspicious subdomains, HTTP protocol) flag threats immediately."),
        ("Defense in Depth (Layered Security)",
         "Six defensive layers: Chrome DOM interception → API Gateway limits → Text normalization →\n"
         "ML classification → Rule engines (URL, phone, email) → Risk engine correlation."),
    ]
    for i, (title, desc) in enumerate(concepts):
        y = Inches(1.6 + i * 1.8)
        accent_bar(s, Inches(0.5), y, height=Inches(1.4), color=ACCENT)
        text_block(s, title, Inches(0.8), y, Inches(8.6), Inches(0.3), font_size=15, color=WHITE, bold=True)
        text_block(s, desc, Inches(0.8), Inches(y.inches + 0.35), Inches(8.6), Inches(1.0), font_size=12, color=TEXT_BODY)
    add_slide_num(s, 12, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 13 — Cybersecurity Concept 7-9
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "Cybersecurity Concepts (3/3)")

    concepts = [
        ("Explainable AI (XAI) in Cybersecurity",
         "SOC analysts need to know WHY an alert was triggered, not just trust a black-box.\n"
         "Countermeasure: Every scan provides a detailed breakdown of detected threat factors."),
        ("ReDoS Defense (Regex Denial-of-Service)",
         "Crafted text strings cause regex engines to enter catastrophic backtracking, freezing the CPU.\n"
         "Countermeasure: 256 KB payload cap via ContentLengthLimitMiddleware + bounded, non-catastrophic patterns."),
        ("Zero-PII Storage (SHA-256 Hashing)",
         "Security tools must not become targets for data leaks by storing raw user messages.\n"
         "Countermeasure: Only SHA-256 hashes are stored for deduplication — zero personally identifiable information."),
    ]
    for i, (title, desc) in enumerate(concepts):
        y = Inches(1.6 + i * 1.8)
        accent_bar(s, Inches(0.5), y, height=Inches(1.4), color=ACCENT)
        text_block(s, title, Inches(0.8), y, Inches(8.6), Inches(0.3), font_size=15, color=WHITE, bold=True)
        text_block(s, desc, Inches(0.8), Inches(y.inches + 0.35), Inches(8.6), Inches(1.0), font_size=12, color=TEXT_BODY)
    add_slide_num(s, 13, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 14 — Technology Stack
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "Technology Stack")

    stacks = [
        ("🖥️ FRONTEND", "React 18.2\nVite 5.0\nTailwind CSS 3.3\nLucide Icons", BLUE_BG),
        ("⚡ BACKEND", "Python 3.11\nFastAPI 0.115\nUvicorn (ASGI)\nPydantic 2.x", GREEN_BG),
        ("🧠 ML / AI", "Scikit-Learn 1.5\nTF-IDF Vectorizer\nLogistic Regression\nJoblib (serialization)", PURPLE_BG),
        ("🔒 BROWSER", "Chrome Extension\nManifest V3\nService Worker\nDOM Scanning", ORANGE_BG),
        ("🗄️ DATABASE", "MongoDB Atlas 7.0+\nPyMongo 3.6\nSHA-256 Hashing\nZero-PII Storage", RED_BG),
        ("☁️ CLOUD", "Vercel (Frontend)\nRender (Backend)\nGitHub (VCS)\nHTTPS / TLS", CARD_DARK),
    ]
    for i, (label, tech, bg) in enumerate(stacks):
        x = Inches(0.3 + (i % 3) * 3.2)
        y = Inches(1.6 + (i // 3) * 2.8)
        card(s, f"{label}\n\n{tech}", x, y, Inches(3.0), Inches(2.3), bg=bg, font_size=12,
             align=PP_ALIGN.CENTER, font_color=WHITE, bold=False)
    add_slide_num(s, 14, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 15 — Chrome Extension Demo
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "Chrome Extension — Live Browser Protection")

    card(s, "How to Use\n\n"
         "1. Install extension from chrome://extensions (Developer Mode)\n"
         "2. Navigate to any webpage — Gmail, WhatsApp Web, news sites\n"
         "3. Highlight suspicious text with your mouse\n"
         "4. Click the Phishing Shield AI extension icon\n"
         "5. Click \"Scan\" — instant risk score with explanation",
         Inches(0.6), Inches(1.6), Inches(4.5), Inches(3.2), bg=CARD_DARK, font_size=13)

    card(s, "Extension Architecture\n\n"
         "• Manifest V3 (latest Chrome standard)\n"
         "• Background Service Worker for API calls\n"
         "• Content script extracts selected text from DOM\n"
         "• Connects to local backend (127.0.0.1:8000)\n"
         "• Supports cloud backend auto-failover\n"
         "• Shows: Score, Verdict, Signals, Action",
         Inches(5.5), Inches(1.6), Inches(4.1), Inches(3.2), bg=BLUE_BG, font_size=12, font_color=WHITE)

    card(s, "⚡ Result Example:  CRITICAL — 91/100  |  Signals: Urgent language, credential request, suspicious URL  |  Action: DO NOT OPEN",
         Inches(0.6), Inches(5.2), Inches(9.0), Inches(0.8), bg=RED_BG, font_size=12, bold=True,
         align=PP_ALIGN.CENTER, font_color=WHITE)
    add_slide_num(s, 15, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 16 — Security & Privacy
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "Security & Privacy by Design")

    items = [
        ("🔐 Least Privilege", "No root access, no app database decryption. Reads only selected text or notification content."),
        ("🔑 No Secrets in Code", "API keys stored as environment variables. .env files excluded from version control."),
        ("🗑️ Minimal Retention", "Raw messages are never stored. Only SHA-256 fingerprints kept for deduplication."),
        ("🔒 Transport Security", "Production API encrypted over HTTPS/TLS. CORS whitelisting for trusted origins."),
        ("📦 Content Size Limits", "256 KB payload cap blocks ReDoS attempts and prevents resource exhaustion."),
        ("🛡️ Security Headers", "X-Content-Type-Options, X-Frame-Options, CSP headers enforced on all responses."),
    ]
    for i, (label, desc) in enumerate(items):
        y = Inches(1.4 + i * 0.9)
        card(s, f"{label}  —  {desc}", Inches(0.6), y, Inches(8.8), Inches(0.75),
             bg=CARD_ALT if i % 2 == 0 else CARD_DARK, font_size=11)
    add_slide_num(s, 16, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 17 — Live Demo Scenarios
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    add_title(s, "Live Demonstration Scenarios")

    demos = [
        ("✅ SAFE", "\"Hey, are you coming to college tomorrow? Let me know.\"", "→ Score: 5 / 100 — SAFE", GREEN_BG),
        ("⚠️ SUSPICIOUS", "\"Your account needs verification. Click here to update your details.\"", "→ Score: 58 / 100 — SUSPICIOUS", ORANGE_BG),
        ("🚨 CRITICAL", "\"URGENT: Your bank account is suspended! Verify now: secure-bank-login.com\"", "→ Score: 92 / 100 — CRITICAL", RED_BG),
        ("📱 SMISHING", "\"Your electricity will be cut tonight. Call 09876543210 to pay immediately.\"", "→ Score: 88 / 100 — CRITICAL (Callback Fraud)", RGBColor(120, 30, 30)),
        ("📧 SPOOFED", "From \"SBI Alert\" <sbi.security@gmail.com> — \"Verify your KYC immediately\"", "→ Score: 85 / 100 — CRITICAL (Spoofed Sender)", PURPLE_BG),
    ]
    for i, (label, msg, result, bg) in enumerate(demos):
        y = Inches(1.5 + i * 1.1)
        card(s, f"{label}   {msg}\n{result}", Inches(0.6), y, Inches(8.8), Inches(0.95),
             bg=bg, font_size=11, font_color=WHITE)

    text_block(s, "Live flow: Payload → JSON → FastAPI → ML + URL + Phone + Email → Risk Engine → Dashboard Alert",
               Inches(0.6), Inches(6.8), Inches(9), Inches(0.4), font_size=12, color=ACCENT, bold=True)
    add_slide_num(s, 17, TOTAL)

    # ════════════════════════════════════════════════════════════
    # SLIDE 18 — Thank You / Q&A
    # ════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank); dark_bg(s)
    shape = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(2.2), Inches(0.08), Inches(2.2))
    shape.fill.solid(); shape.fill.fore_color.rgb = ACCENT; shape.line.fill.background()

    text_block(s, "Thank You", Inches(0.9), Inches(2.0), Inches(8), Inches(0.8),
               font_size=44, color=WHITE, bold=True)
    text_block(s, "Questions & Discussion", Inches(0.9), Inches(2.9), Inches(8), Inches(0.6),
               font_size=24, color=MUTED)

    card(s, "🌐 Live Site:  phishing-shield-ai-web.vercel.app\n"
         "💻 GitHub:  github.com/RamNarayan0/phishing-shield-ai\n"
         "🔒 Chrome Extension:  Loaded via Developer Mode",
         Inches(0.9), Inches(4.4), Inches(8), Inches(1.4), bg=CARD_DARK, font_size=14,
         font_color=ACCENT)
    add_slide_num(s, 18, TOTAL)

    # ── save ────────────────────────────────────────────────────
    import shutil
    import os
    out_dir = "docs/presentation"
    os.makedirs(out_dir, exist_ok=True)
    
    # Save to v2 first
    v2_path = os.path.join(out_dir, "Phishing_Shield_AI_v2.pptx")
    prs.save(v2_path)
    print(f"[OK] Created {v2_path} - {TOTAL} slides")

    # Save to desktop directly
    desktop_path = r"c:\Users\Sai Santhosh Ram\OneDrive\Ram Narayan\OneDrive\Desktop\Phishing_Shield_AI_Presentation.pptx"
    try:
        prs.save(desktop_path)
        print(f"[OK] Saved directly to Desktop: {desktop_path}")
    except Exception as e:
        print(f"[NOTE] Desktop save: {e}")

    # Attempt to overwrite Phishing_Shield_AI.pptx if unlocked
    primary_path = os.path.join(out_dir, "Phishing_Shield_AI.pptx")
    try:
        prs.save(primary_path)
        print(f"[OK] Updated primary file: {primary_path}")
    except Exception as e:
        print(f"[INFO] Primary file was locked, accessible at {v2_path} and Desktop")

if __name__ == '__main__':
    create_presentation()
