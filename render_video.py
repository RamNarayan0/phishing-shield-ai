import os
import pyttsx3
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import math

def create_text_image(text, filename, size=(1280, 720), bg_color=(15, 23, 42), text_color=(255, 255, 255)):
    img = Image.new('RGB', size, color=bg_color)
    d = ImageDraw.Draw(img)
    
    # Simple text wrapping and centering (crude but works without external fonts)
    # We will just draw text roughly
    lines = text.split('\n')
    y = 100
    for line in lines:
        # Default font is usually very small, but it's the only guaranteed one without loading a TTF
        # To make it readable, we scale the image up later or just draw multiple times
        d.text((100, y), line, fill=text_color)
        y += 40
        
    img.save(filename)
    return filename

def generate_scene(scene_id, text_content, narration_text, engine):
    # 1. Generate Image
    img_file = f"scene_{scene_id}.png"
    create_text_image(text_content, img_file)
    
    # 2. Generate Audio
    audio_file = f"scene_{scene_id}.wav"
    engine.save_to_file(narration_text, audio_file)
    
    return img_file, audio_file

def main():
    print("Initializing TTS Engine...")
    engine = pyttsx3.init()
    engine.setProperty('rate', 160) # Slower, professional pacing
    
    scenes = [
        {
            "id": 1,
            "visual": "PHISHING SHIELD AI\n\nMulti-Channel Intelligent Phishing Detection System",
            "narration": "Phishing Shield AI is a multi-channel intelligent phishing detection prototype. The purpose of the system is to analyze suspicious communication content, identify phishing and social-engineering signals, calculate a threat score, and explain why the content may be dangerous."
        },
        {
            "id": 2,
            "visual": "THE PROBLEM\n\nSMS | WhatsApp | Email | Browser\nPhishing can appear through multiple channels.",
            "narration": "Modern phishing is not limited to traditional email. The same social-engineering technique can appear as an account warning, KYC message, delivery notification, fake job offer, or suspicious link. Users need real-time, multi-channel protection."
        },
        {
            "id": 3,
            "visual": "AUTOMATIC EVENT INGESTION\n\nEvent -> Ingestion -> Analysis -> Risk Engine -> Alert",
            "narration": "Our solution separates the communication channel from the detection core. Different supported clients can send content to one central analysis engine, transforming a passive scanner into an active, event-driven security monitor."
        },
        {
            "id": 4,
            "visual": "THE HERO DEMONSTRATION\n\nAndroid Notification Arrives:\n'URGENT SECURITY ALERT...'",
            "narration": "Let's observe an actual demonstration. A suspicious Android notification arrives. It is instantly intercepted at the boundary, converted into a normalized JSON payload, and routed to the central engine."
        },
        {
            "id": 5,
            "visual": "BACKEND: FASTAPI\n\nClient -> JSON -> FastAPI -> Validation",
            "narration": "At the backend, the message hits our FastAPI endpoints. The raw text is validated, and any embedded URLs are automatically extracted for independent analysis."
        },
        {
            "id": 6,
            "visual": "TEXT ANALYSIS\n\nUrgency | Financial context | Credential request",
            "narration": "The text engine categorizes semantic signals, identifying urgency, financial threats, credential requests, and impersonation language. It does not rely solely on simple keywords."
        },
        {
            "id": 7,
            "visual": "MACHINE LEARNING\n\nRaw Text -> TF-IDF -> Logistic Regression",
            "narration": "Simultaneously, the text is vectorized using TF-IDF and passed through a Logistic Regression model. This provides a fast, CPU-friendly baseline classification probability to complement our security heuristics."
        },
        {
            "id": 8,
            "visual": "URL ANALYSIS\n\nhttps://secure-bank-login.com\n- structural risk\n- credential-oriented path",
            "narration": "The URL engine evaluates the domain structure, path anomalies, and lexical risk indicators. This provides a second, independent security signal."
        },
        {
            "id": 9,
            "visual": "RISK ENGINE\n\nTEXT ML + URL + CONTEXT -> RISK ENGINE -> 91/100",
            "narration": "The Risk Engine combines these independent signals. Rather than allowing one keyword to determine the result, it aggregates the data into a final normalized score from 0 to 100."
        },
        {
            "id": 10,
            "visual": "EXPLAINABILITY\n\nCRITICAL (91/100)\n\n✓ Urgent language\n✓ Financial context\n✓ Suspicious URL",
            "narration": "This leads to our explainability layer. The system doesn't just say 'YES' or 'NO'. It explicitly lists the exact signals that contributed to the critical verdict, helping the user understand the exact nature of the threat."
        },
        {
            "id": 11,
            "visual": "SAFE MESSAGE DEMONSTRATION\n\n'Hey, are you coming to college tomorrow?'\nResult: SAFE",
            "narration": "To prove the system isn't simply classifying everything as malicious, when a normal conversational message arrives, the system correctly analyzes the intent and returns a Safe verdict with a zero risk score."
        },
        {
            "id": 12,
            "visual": "CHROME INTEGRATION\n\nWeb Page -> Content Script -> JSON -> FastAPI",
            "narration": "This same exact backend powers our Chrome Extension. A Manifest V3 content script extracts suspicious page context and routes it to the Risk Engine, providing seamless cross-platform security."
        },
        {
            "id": 13,
            "visual": "ANDROID INTEGRATION\n\nNotification -> Listener Service -> REST API",
            "narration": "On Android, the prototype architecture uses a Notification Listener Service. It operates securely at the notification boundary, extracting text without needing to decrypt the private databases of other applications."
        },
        {
            "id": 14,
            "visual": "TECHNOLOGY STACK\n\nFrontend: React, Vite\nBackend: Python, FastAPI\nML: scikit-learn",
            "narration": "The technology stack is built for speed and integration. React provides the interactive dashboard, FastAPI powers the high-performance backend, and scikit-learn drives the machine learning pipeline."
        },
        {
            "id": 15,
            "visual": "PROTOCOLS\n\nCURRENT: HTTP/REST, JSON\nPRODUCTION: HTTPS/TLS, OAuth 2.0",
            "narration": "The prototype communicates using HTTP REST and JSON. A production deployment would seamlessly integrate HTTPS, TLS, and OAuth 2.0 for secure email ingestions."
        },
        {
            "id": 16,
            "visual": "SECURITY & LIMITATIONS\n\nLeast Privilege | Prototype Dataset",
            "narration": "The system follows least privilege principles, never storing passwords or OTPs. Current limitations include reliance on a prototype dataset and a lightweight ML baseline model."
        },
        {
            "id": 17,
            "visual": "FUTURE SCOPE\n\nTransformers (BERT)\nThreat Intelligence\nGraph Analysis",
            "narration": "Future developments include upgrading to Transformer models like BERT, expanding the training dataset, and integrating external threat intelligence feeds."
        },
        {
            "id": 18,
            "visual": "PHISHING SHIELD AI\n\nDetect . Explain . Protect",
            "narration": "Phishing Shield AI demonstrates a complete security analysis pipeline. The prototype provides the foundation for a larger real-time phishing protection system. Detect, Explain, Protect."
        }
    ]
    
    scene_files = []
    print("Generating Scenes (Text + Queuing Audio)...")
    for s in scenes:
        img, aud = generate_scene(s['id'], s['visual'], s['narration'], engine)
        scene_files.append((img, aud))
        
    print("Rendering Audio...")
    engine.runAndWait()
    
    print("Creating MoviePy Clips...")
    clips = []
    for img_file, audio_file in scene_files:
        audio_clip = AudioFileClip(audio_file)
        video_clip = ImageClip(img_file).set_duration(audio_clip.duration)
        video_clip = video_clip.set_audio(audio_clip)
        clips.append(video_clip)
        
    print("Concatenating clips...")
    final_video = concatenate_videoclips(clips, method="compose")
    
    print("Writing final MP4...")
    # Low fps to render fast enough for the environment constraints
    final_video.write_videofile("Phishing_Shield_AI_Real_Project_Explainer.mp4", fps=2, codec="libx264", audio_codec="aac")
    print("Done!")

if __name__ == "__main__":
    main()
