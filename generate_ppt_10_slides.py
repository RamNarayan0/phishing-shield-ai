import collections
import collections.abc
import os
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# ── Color Palette ────────────────────────────────────────────────────────
BG_DARK     = RGBColor(15, 23, 42)      # Deep slate #0F172A
CARD_DARK   = RGBColor(30, 41, 59)      # Slate #1E293B
CARD_DEEP   = RGBColor(20, 30, 48)      # Alternate container
ACCENT_CYAN = RGBColor(56, 189, 248)    # Cyan #38BDF8
ACCENT_BLUE = RGBColor(96, 165, 250)    # Blue #60A5FA
WHITE       = RGBColor(255, 255, 255)
MUTED_GRAY  = RGBColor(148, 163, 184)   # Slate gray #94A3B8
TEXT_BODY   = RGBColor(226, 232, 240)   # Light gray #E2E8F0
BORDER_COL  = RGBColor(51, 65, 85)      # Border #334155
GREEN_BG    = RGBColor(6, 78, 59)       # Emerald #064E3B
RED_BG      = RGBColor(153, 27, 27)     # Crimson #991B1B
ORANGE_BG   = RGBColor(180, 83, 9)      # Amber #B45309
PURPLE_BG   = RGBColor(88, 28, 135)     # Violet #581C87

def apply_dark_bg(slide):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG_DARK

def add_header(slide, title, category="PHISHING SHIELD AI  |  3RD YEAR - 1ST SEM"):
    # Category tag
    tb_cat = slide.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(8.8), Inches(0.3))
    p_cat = tb_cat.text_frame.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = ACCENT_CYAN
    p_cat.font.name = "Arial"
    
    # Title
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.65), Inches(8.8), Inches(0.6))
    p = tb.text_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = "Arial"

def add_slide_footer(slide, current, total=10):
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(7.05), Inches(8.8), Inches(0.35))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = f"Batch 3B2  |  Department of Computer Science & Engineering  |  Slide {current} of {total}"
    p.font.size = Pt(9.5)
    p.font.color.rgb = MUTED_GRAY
    p.alignment = PP_ALIGN.RIGHT

def make_card(slide, text, left, top, width, height, bg=CARD_DARK, font_size=12, bold=False, font_col=TEXT_BODY, align=PP_ALIGN.LEFT, border=BORDER_COL):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg
    shape.line.color.rgb = border
    shape.line.width = Pt(1)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.12)
    tf.margin_right = Inches(0.12)
    tf.margin_top = Inches(0.1)
    tf.margin_bottom = Inches(0.1)
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = font_col
    p.font.bold = bold
    p.font.name = "Arial"
    p.alignment = align
    return shape

def make_text(slide, text, left, top, width, height, font_size=12, color=TEXT_BODY, bold=False, align=PP_ALIGN.LEFT):
    tx = slide.shapes.add_textbox(left, top, width, height)
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = "Arial"
    p.alignment = align
    return tx

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    TOTAL_SLIDES = 10

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 1: Title Slide (With Exact User Metadata Table)
    # ══════════════════════════════════════════════════════════════════════════
    s1 = prs.slides.add_slide(blank)
    apply_dark_bg(s1)

    # Accent decorative bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(0.5), Inches(0.08), Inches(1.3))
    bar.fill.solid(); bar.fill.fore_color.rgb = ACCENT_CYAN; bar.line.fill.background()

    make_text(s1, "B.TECH CSE — 3RD YEAR 1ST SEMESTER  |  MAJOR PROJECT PRESENTATION", Inches(0.8), Inches(0.48), Inches(8.5), Inches(0.3), font_size=11, color=ACCENT_CYAN, bold=True)
    make_text(s1, "Phishing Shield AI", Inches(0.8), Inches(0.75), Inches(8.5), Inches(0.6), font_size=32, color=WHITE, bold=True)
    make_text(s1, "Multi-Vector AI-Powered Phishing Threat Detection and Real-Time Mitigation System", Inches(0.8), Inches(1.35), Inches(8.5), Inches(0.45), font_size=14, color=MUTED_GRAY)

    # Project Metadata Table
    # Table dimensions: 5 rows (Header, 4 students), 4 columns or structured table
    table_shape = s1.shapes.add_table(7, 3, Inches(0.6), Inches(2.0), Inches(8.8), Inches(4.5))
    table = table_shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(2.6)
    table.columns[2].width = Inches(4.0)

    rows_data = [
        ("Batch No.", "3B2", "Academic Year: 3rd Year - 1st Sem"),
        ("Title of the Project", "Phishing Shield AI – Multi-Vector AI-Powered Phishing Threat Detection and Real-Time Mitigation System", ""),
        ("Student Details", "Roll No", "Name of the Student"),
        ("", "24891A0594", "KOTHAPALLY BINDUSREE"),
        ("", "24891A0596", "MALLEPAKULA BHUVANISHWARI"),
        ("", "24891A0575", "DUNGROTHU NIKHIL"),
        ("", "24891A0573", "DEVARASHETTY RAM NARAYAN"),
    ]

    for row_idx, rdata in enumerate(rows_data):
        for col_idx in range(3):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            # Background coloring
            if row_idx == 0:
                cell.fill.fore_color.rgb = RGBColor(12, 74, 110) # dark blue header
            elif row_idx == 1:
                cell.fill.fore_color.rgb = CARD_DARK
            elif row_idx == 2:
                cell.fill.fore_color.rgb = RGBColor(30, 58, 138) # table column headers
            else:
                cell.fill.fore_color.rgb = CARD_DARK if row_idx % 2 == 0 else CARD_DEEP

            p = cell.text_frame.paragraphs[0]
            p.font.name = "Arial"
            
            # Text assignment & span handling
            if row_idx == 1 and col_idx == 1:
                p.text = rdata[1]
                p.font.bold = True
                p.font.size = Pt(11)
                p.font.color.rgb = WHITE
            elif row_idx == 1 and col_idx == 2:
                p.text = ""
            elif row_idx >= 3 and col_idx == 0:
                p.text = "Student Details" if row_idx == 3 else ""
                p.font.bold = True
                p.font.size = Pt(11)
                p.font.color.rgb = ACCENT_CYAN
            else:
                p.text = rdata[col_idx]
                p.font.size = Pt(11 if row_idx <= 2 else 11.5)
                p.font.bold = (row_idx in [0, 2] or col_idx in [0, 1])
                p.font.color.rgb = WHITE if (row_idx in [0, 2] or col_idx == 1) else TEXT_BODY

    # Guide Name Card below table
    make_card(s1, "Guide Name:   Mr. VSSPLN Balaji Lanka  (Assistant Professor, Dept. of CSE)", Inches(0.6), Inches(6.6), Inches(8.8), Inches(0.55), bg=RGBColor(6, 78, 59), font_size=12, bold=True, font_col=WHITE, align=PP_ALIGN.CENTER)
    add_slide_footer(s1, 1, TOTAL_SLIDES)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 2: Problem Statement & Motivation
    # ══════════════════════════════════════════════════════════════════════════
    s2 = prs.slides.add_slide(blank)
    apply_dark_bg(s2)
    add_header(s2, "The Problem: Cross-Channel Social Engineering")

    make_card(s2, "Traditional Security Defenses Are Broken\n\n"
                  "- Static URL Blacklists: Blind to freshly registered Zero-Day phishing domains during the critical initial 2-4 hours.\n\n"
                  "- Email-Only Filters: Completely miss SMS smishing, WhatsApp lottery calls, and direct browser attacks.\n\n"
                  "- Opaque Black-Box AI: High false alarms without actionable explanations cause severe alert fatigue for users and SOC teams.",
              Inches(0.6), Inches(1.4), Inches(4.2), Inches(5.4), bg=CARD_DARK, font_size=12, font_col=TEXT_BODY)

    threats = [
        ("Phishing (Email / Web)", "Spoofed sender headers, fake login portals, brand impersonation.", RED_BG),
        ("Smishing (SMS / WhatsApp)", "Panic text traps: 'Power disconnection tonight! Call officer immediately.'", ORANGE_BG),
        ("Typosquatting Domains", "Visual deception: paypa1.com, rnicrosoft.com, goog1e.com.", PURPLE_BG),
        ("Callback Vishing Traps", "VoIP-generated phone scams (+92, +44) exploiting trust & fear.", RGBColor(12, 74, 110)),
    ]
    for i, (ttitle, tdesc, tcol) in enumerate(threats):
        y = Inches(1.4 + i * 1.35)
        make_card(s2, f"{ttitle}\n{tdesc}", Inches(5.0), y, Inches(4.4), Inches(1.2), bg=tcol, font_size=11.5, bold=False, font_col=WHITE)

    add_slide_footer(s2, 2, TOTAL_SLIDES)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 3: System Workflow & Ingestion Pipeline
    # ══════════════════════════════════════════════════════════════════════════
    s3 = prs.slides.add_slide(blank)
    apply_dark_bg(s3)
    add_header(s3, "End-to-End System Workflow")

    wf_steps = [
        ("Step 1", "Ingestion", "Web Dashboard, Chrome Ext, or SIEM API submits raw content"),
        ("Step 2", "Perimeter Defense", "FastAPI validates payload, enforces 256 KB ReDoS cap & headers"),
        ("Step 3", "Multi-Vector Analysis", "Text NLP + URL scanner + Phone trap + Email spoofing engines"),
        ("Step 4", "Hybrid Risk Engine", "Arbitrates weighted threat factors & compound penalties (0–100)"),
        ("Step 5", "Explainable Output", "Returns risk score, signals, action, & stores zero-PII hash"),
    ]
    for i, (num, title, desc) in enumerate(wf_steps):
        x = Inches(0.5 + i * 1.8)
        make_card(s3, f"{num}\n{title}", x, Inches(1.5), Inches(1.65), Inches(0.8), bg=RGBColor(12, 74, 110), font_size=12, bold=True, font_col=WHITE, align=PP_ALIGN.CENTER)
        make_card(s3, desc, x, Inches(2.4), Inches(1.65), Inches(2.0), bg=CARD_DARK, font_size=11, font_col=TEXT_BODY, align=PP_ALIGN.CENTER)
        if i < len(wf_steps) - 1:
            make_text(s3, "➔", Inches(2.17 + i * 1.8), Inches(1.7), Inches(0.2), Inches(0.4), font_size=18, color=ACCENT_CYAN, bold=True)

    make_card(s3, "Architecture Invariants:\n"
                  "1. Single Analysis Core: Centralized FastAPI brain powers both Chrome Extension and Web Dashboard uniformly.\n"
                  "2. Deterministic + ML Fusion: Combines mathematical NLP probability with rule-based security heuristics.\n"
                  "3. Privacy-by-Design: Raw user messages are never saved; only deterministic SHA-256 hashes are indexed.",
              Inches(0.5), Inches(4.7), Inches(9.0), Inches(2.1), bg=CARD_DEEP, font_size=12, font_col=TEXT_BODY, border=ACCENT_CYAN)

    add_slide_footer(s3, 3, TOTAL_SLIDES)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 4: Machine Learning Architecture (The 4 Models)
    # ══════════════════════════════════════════════════════════════════════════
    s4 = prs.slides.add_slide(blank)
    apply_dark_bg(s4)
    add_header(s4, "Machine Learning Architecture (The 4 Models)")

    models = [
        ("Model 1: Primary NLP Classifier",
         "model.pkl + vectorizer.pkl",
         "• Sublinear TF-IDF (unigrams + bigrams) + L2 Logistic Regression\n"
         "• Trained on 29,113 samples (Kaggle Phishing, Enron, UCI SMS)\n"
         "• 96.84% Accuracy | 97.10% Recall | 0.9891 ROC-AUC\n"
         "• Latency: Under 15 ms (runs on lightweight CPU instances)",
         RGBColor(12, 74, 110)),
        ("Model 2: Smishing & Phone Classifier",
         "phone_pattern_model.pkl",
         "• ITU-T E.164 phone structure & country-code analysis (+92, +44)\n"
         "• Digit entropy evaluation for automated VoIP-generated numbers\n"
         "• Detects institutional keyword + personal mobile mismatch\n"
         "• Flags callback traps: 'Power will be cut! Call officer immediately'",
         RGBColor(6, 78, 59)),
        ("Model 3: Email Spoofing Classifier",
         "email_pattern_model.pkl",
         "• Detects official display names originating from free webmail\n"
         "  (e.g., 'SBI Security Team' <sbi.kyc.alert@gmail.com>)\n"
         "• Flags disposable burner domains (tempmail, mailinator)\n"
         "• Evaluates high-abuse Top-Level Domains (.xyz, .top, .buzz)",
         RGBColor(88, 28, 135)),
        ("Model 4: Hybrid Risk Arbitration Engine",
         "risk_engine.py",
         "• URL Factor (up to 80%) + Text NLP Factor (40-50%)\n"
         "• Compound Escalation: Urgent text + suspicious link = +35 penalty\n"
         "• Instant Override: Brand spoofing/toll fraud = CRITICAL\n"
         "• Calibrated Output: SAFE (0-39) | SUSP (40-69) | CRIT (70-100)",
         RGBColor(153, 27, 27)),
    ]
    for i, (mtitle, mfile, mdesc, mcol) in enumerate(models):
        x = Inches(0.5 + (i % 2) * 4.6)
        y = Inches(1.4 + (i // 2) * 2.7)
        make_card(s4, f"{mtitle}\n[{mfile}]\n\n{mdesc}", x, y, Inches(4.4), Inches(2.5), bg=mcol, font_size=11, font_col=WHITE)

    add_slide_footer(s4, 4, TOTAL_SLIDES)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 5: Core Cybersecurity Concepts Implemented
    # ══════════════════════════════════════════════════════════════════════════
    s5 = prs.slides.add_slide(blank)
    apply_dark_bg(s5)
    add_header(s5, "Core Cybersecurity Concepts Implemented")

    concepts = [
        ("1. Social Engineering & Urgency Exploitation",
         "Attackers exploit fear and artificial urgency to bypass logical evaluation. The NLP engine detects urgency patterns ('action required within 2 hours', 'account suspended') as primary risk indicators."),
        ("2. Typosquatting Defense (Levenshtein Distance)",
         "Computes edit distance against known financial & tech brands. Domains like 'paypa1.com' or 'rnicrosoft.com' with single-character replacements trigger high-severity typosquatting alerts."),
        ("3. Zero-Day Threat Interception",
         "Newly created scam domains bypass commercial blacklists. Structural heuristics (raw IP in hostname, excess subdomains, unencrypted HTTP, login paths) intercept malicious links instantly."),
        ("4. Defense in Depth (Layered Perimeter)",
         "Six independent defensive layers: Client DOM Interception -> API Gateway Limits -> Normalization Sanitization -> NLP Vectorization -> Specialized Rule Engines -> Risk Engine Arbitration."),
        ("5. ReDoS & Denial-of-Service Defense",
         "Protects backend CPUs from catastrophic regular expression backtracking attacks by capping inbound request payloads at 256 KB and enforcing bounded, linear-time regex matching."),
    ]
    for i, (ctitle, cdesc) in enumerate(concepts):
        y = Inches(1.4 + i * 1.1)
        make_card(s5, f"{ctitle}\n{cdesc}", Inches(0.6), y, Inches(8.8), Inches(1.0), bg=CARD_DARK, font_size=11.5, font_col=TEXT_BODY, border=ACCENT_CYAN if i==1 else BORDER_COL)

    add_slide_footer(s5, 5, TOTAL_SLIDES)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 6: Complete Technology Stack Matrix
    # ══════════════════════════════════════════════════════════════════════════
    s6 = prs.slides.add_slide(blank)
    apply_dark_bg(s6)
    add_header(s6, "Complete Technology Stack")

    stack_cards = [
        ("Frontend Dashboard", "React 18.2.0 + Vite 5.0\nTailwind CSS + Lucide Icons\nReal-time threat feed & stats", RGBColor(12, 74, 110)),
        ("Backend REST API", "Python 3.11 + FastAPI\nUvicorn ASGI + Pydantic v2\nSub-15ms inference latency", RGBColor(6, 78, 59)),
        ("Machine Learning", "Scikit-Learn 1.5 + Joblib\nSublinear TF-IDF + Logistic Reg\n29,113 sample dataset", RGBColor(88, 28, 135)),
        ("Browser Extension", "Chrome Manifest V3\nBackground Service Worker\nActive DOM text & link scanner", RGBColor(180, 83, 9)),
        ("Database & Storage", "MongoDB Atlas 7.0+\nPyMongo async connection pool\nSHA-256 Zero-PII hashing", RGBColor(153, 27, 27)),
        ("Cloud & Deployment", "Frontend: Vercel (Production)\nBackend: Render / Cloudflare\nRepository: GitHub CI/CD", RGBColor(30, 41, 59)),
    ]
    for i, (stitle, sbody, scol) in enumerate(stack_cards):
        x = Inches(0.6 + (i % 3) * 3.0)
        y = Inches(1.5 + (i // 3) * 2.6)
        make_card(s6, f"{stitle}\n\n{sbody}", x, y, Inches(2.8), Inches(2.3), bg=scol, font_size=12, font_col=WHITE, align=PP_ALIGN.CENTER)

    add_slide_footer(s6, 6, TOTAL_SLIDES)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 7: Chrome Extension & Real-Time Browser Protection
    # ══════════════════════════════════════════════════════════════════════════
    s7 = prs.slides.add_slide(blank)
    apply_dark_bg(s7)
    add_header(s7, "Chrome Extension: Real-Time Browser Protection")

    make_card(s7, "Manifest V3 Architecture\n\n"
                  "• Non-Blocking Service Worker: Handles asynchronous communication with the central API gateway.\n"
                  "• DOM Content Extraction: Injects lightweight scripting to extract selected text on any webpage.\n"
                  "• Multi-Environment Support: Switches seamlessly between Local Dev (127.0.0.1:8000) and Cloud API.\n"
                  "• Zero Performance Overhead: Does not modify DOM or slow down regular browsing.",
              Inches(0.6), Inches(1.4), Inches(4.3), Inches(4.0), bg=CARD_DARK, font_size=12, font_col=TEXT_BODY)

    make_card(s7, "User Workflow & Live Output\n\n"
                  "1. User highlights any suspicious text or link on WhatsApp Web, Gmail, or banking portals.\n"
                  "2. Clicks the Phishing Shield AI extension icon in the Chrome toolbar.\n"
                  "3. Clicks 'Scan' -> Instant verdict is rendered:\n"
                  "   - Threat Score: e.g., 91 / 100\n"
                  "   - Verdict Badge: CRITICAL / HIGH RISK\n"
                  "   - Extracted Entities: Phone numbers & emails\n"
                  "   - Explanations: 'Urgent language + fake KYC link'\n"
                  "   - Recommended Action: 'DO NOT OPEN / BLOCK'",
              Inches(5.1), Inches(1.4), Inches(4.3), Inches(4.0), bg=RGBColor(12, 74, 110), font_size=12, font_col=WHITE)

    make_card(s7, "Deployment Status: Fully compatible with Chrome MV3 standards; installable via 'Load Unpacked' Developer Mode.", Inches(0.6), Inches(5.6), Inches(8.8), Inches(0.8), bg=GREEN_BG, font_size=12, bold=True, font_col=WHITE, align=PP_ALIGN.CENTER)

    add_slide_footer(s7, 7, TOTAL_SLIDES)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 8: Security, Privacy & Data Protection (Zero-PII)
    # ══════════════════════════════════════════════════════════════════════════
    s8 = prs.slides.add_slide(blank)
    apply_dark_bg(s8)
    add_header(s8, "Security, Privacy & Data Protection (Zero-PII)")

    priv_points = [
        ("Zero-PII Cryptographic Hashing", "Raw message texts, emails, and phone numbers are NEVER permanently stored in the database. Only deterministic SHA-256 cryptographic fingerprints are indexed for deduplication and cross-channel threat correlation."),
        ("Principle of Least Privilege", "The Chrome extension only accesses the actively highlighted text selection. It does not inspect full browsing history, unhighlighted tabs, or stored browser passwords."),
        ("Strict Payload & ReDoS Limits", "The API enforces a 256 KB content-length cap on all inbound payloads via custom ASGI middleware, blocking Denial-of-Service and catastrophic memory exhaustion exploits."),
        ("Transport Encryption & Strict CORS", "All communication between client edges and API gateways is enforced over HTTPS/TLS with strict CORS domain whitelisting preventing unauthorized cross-origin requests."),
        ("Automated Threat Deduplication", "MongoDB unique indexing on SHA-256 fingerprints automatically increments attack frequency counts rather than creating duplicate redundant database entries."),
    ]
    for i, (ptitle, pdesc) in enumerate(priv_points):
        y = Inches(1.4 + i * 1.1)
        make_card(s8, f"{ptitle}\n{pdesc}", Inches(0.6), y, Inches(8.8), Inches(1.0), bg=CARD_DARK, font_size=11.5, font_col=TEXT_BODY, border=GREEN_BG if i==0 else BORDER_COL)

    add_slide_footer(s8, 8, TOTAL_SLIDES)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 9: Results & Live Demonstration Scenarios
    # ══════════════════════════════════════════════════════════════════════════
    s9 = prs.slides.add_slide(blank)
    apply_dark_bg(s9)
    add_header(s9, "Results & Live Demonstration Scenarios")

    # Metrics summary header
    make_card(s9, "Model Metrics:   Accuracy: 96.84%   |   Precision: 95.42%   |   Recall: 97.10%   |   ROC-AUC: 0.9891   |   Inference: <15ms",
              Inches(0.6), Inches(1.35), Inches(8.8), Inches(0.5), bg=RGBColor(12, 74, 110), font_size=11.5, bold=True, font_col=WHITE, align=PP_ALIGN.CENTER)

    test_cases = [
        ("NORMAL MESSAGE", "'Hey, are you coming to college tomorrow? Let me know.'", "Score: 05 / 100", "SAFE", GREEN_BG),
        ("VERIFICATION PROMPT", "'Your account needs verification. Click here to confirm details.'", "Score: 58 / 100", "SUSPICIOUS", ORANGE_BG),
        ("BANK PHISHING LINK", "'URGENT: Bank account suspended! Verify: secure-bank-login.com'", "Score: 92 / 100", "CRITICAL", RED_BG),
        ("ELECTRICITY SMISHING", "'Power will be cut tonight! Call officer 09876543210 immediately.'", "Score: 88 / 100", "CRITICAL", RGBColor(120, 30, 30)),
        ("SPOOFED SENDER EMAIL", "From 'SBI Security' <sbi.alert@gmail.com> - 'Immediate KYC required'", "Score: 85 / 100", "CRITICAL", PURPLE_BG),
    ]
    for i, (tname, tcontent, tscore, tverdict, tcol) in enumerate(test_cases):
        y = Inches(2.0 + i * 0.98)
        make_card(s9, f"[{tname}]\n{tcontent}", Inches(0.6), y, Inches(6.0), Inches(0.88), bg=CARD_DARK, font_size=11, font_col=TEXT_BODY)
        make_card(s9, f"{tverdict}\n{tscore}", Inches(6.8), y, Inches(2.6), Inches(0.88), bg=tcol, font_size=12, bold=True, font_col=WHITE, align=PP_ALIGN.CENTER)

    add_slide_footer(s9, 9, TOTAL_SLIDES)

    # ══════════════════════════════════════════════════════════════════════════
    # SLIDE 10: Conclusion & Project Deliverables
    # ══════════════════════════════════════════════════════════════════════════
    s10 = prs.slides.add_slide(blank)
    apply_dark_bg(s10)
    add_header(s10, "Conclusion & Project Deliverables")

    make_card(s10, "Key Achievements & Summary\n\n"
                   "• Comprehensive Defense: Built an operational end-to-end phishing protection system protecting users across Web, Email, and SMS vectors.\n\n"
                   "• High-Speed Explainability: Delivered sub-15ms AI inference with transparent threat explanations, eliminating black-box distrust.\n\n"
                   "• Practical Security Engineering: Implemented Zero-PII SHA-256 data storage, ReDoS mitigation, and Levenshtein typosquatting defense.",
              Inches(0.6), Inches(1.4), Inches(4.3), Inches(4.2), bg=CARD_DARK, font_size=12, font_col=TEXT_BODY)

    make_card(s10, "Live Deliverables & Links\n\n"
                   "🌐 Live Web App:\nhttps://phishing-shield-ai-web.vercel.app\n\n"
                   "💻 GitHub Repository:\nhttps://github.com/RamNarayan0/phishing-shield-ai\n\n"
                   "🧩 Chrome Extension:\nManifest V3 (Installed on Chrome)\n\n"
                   "📄 Technical Documentation:\n4-Page PDF on Desktop",
              Inches(5.1), Inches(1.4), Inches(4.3), Inches(4.2), bg=RGBColor(12, 74, 110), font_size=12, font_col=WHITE)

    make_card(s10, "Thank you! Open for Questions & Demonstration.", Inches(0.6), Inches(5.8), Inches(8.8), Inches(0.9), bg=GREEN_BG, font_size=16, bold=True, font_col=WHITE, align=PP_ALIGN.CENTER)

    add_slide_footer(s10, 10, TOTAL_SLIDES)

    # ── Save Presentation ─────────────────────────────────────────────────────
    out_dir = "docs/presentation"
    os.makedirs(out_dir, exist_ok=True)
    
    # Save to primary and v2
    v2_path = os.path.join(out_dir, "Phishing_Shield_AI_v2.pptx")
    prs.save(v2_path)
    print(f"[OK] Created {v2_path} - {TOTAL_SLIDES} slides")

    desktop_path = r"c:\Users\Sai Santhosh Ram\OneDrive\Ram Narayan\OneDrive\Desktop\Phishing_Shield_AI_Presentation.pptx"
    try:
        prs.save(desktop_path)
        print(f"[OK] Saved directly to Desktop: {desktop_path}")
    except Exception as e:
        print(f"[NOTE] Desktop save: {e}")

    primary_path = os.path.join(out_dir, "Phishing_Shield_AI.pptx")
    try:
        prs.save(primary_path)
        print(f"[OK] Updated primary file: {primary_path}")
    except Exception as e:
        print(f"[INFO] Primary file was locked, accessible at {v2_path} and Desktop")

if __name__ == "__main__":
    create_deck()
