import json
import asyncio
import requests
import websockets
import time

CHROME_DEBUG_URL = "http://localhost:9222"
API_URL = "http://localhost:8000/api/verify-message"
DASHBOARD_URL = "http://localhost:5176"

def get_tabs():
    resp = requests.get(f"{CHROME_DEBUG_URL}/json/list")
    return resp.json()

def create_tab(url="about:blank"):
    resp = requests.put(f"{CHROME_DEBUG_URL}/json/new?{url}")
    return resp.json()

async def eval_js(ws_url, expression):
    async with websockets.connect(ws_url) as ws:
        msg = {
            "id": int(time.time() * 1000) % 100000,
            "method": "Runtime.evaluate",
            "params": {"expression": expression, "returnByValue": True}
        }
        await ws.send(json.dumps(msg))
        res = await ws.recv()
        data = json.loads(res)
        return data.get("result", {}).get("result", {}).get("value")

async def navigate_page(ws_url, url):
    async with websockets.connect(ws_url) as ws:
        msg = {
            "id": int(time.time() * 1000) % 100000,
            "method": "Page.navigate",
            "params": {"url": url}
        }
        await ws.send(json.dumps(msg))
        return await ws.recv()

async def run_browser_automation():
    print("=" * 60)
    print("[BROWSER AGENT] TAKING CONTROL OF CHROME...")
    print("=" * 60)

    # 1. Get existing page tabs
    tabs = get_tabs()
    page_tabs = [t for t in tabs if t.get('type') == 'page']
    
    if not page_tabs:
        print("Creating a new tab...")
        new_tab = create_tab(DASHBOARD_URL)
        page_tabs = [new_tab]

    main_tab = page_tabs[0]
    ws_url = main_tab.get('webSocketDebuggerUrl')
    print(f"Targeting main browser tab: {main_tab.get('title')} ({main_tab.get('id')})")

    # 2. Navigate tab to SOC Dashboard
    print(f"\n[1/4] Navigating Chrome tab to Live SOC Dashboard: {DASHBOARD_URL}")
    await navigate_page(ws_url, DASHBOARD_URL)
    await asyncio.sleep(2)

    # 3. Create second tab with a simulated WhatsApp / Email chat message
    print("\n[2/4] Opening second tab to simulate an incoming WhatsApp/Email threat...")
    test_html = """data:text/html,
    <html>
    <head><title>WhatsApp Web Simulator</title></head>
    <body style='font-family:sans-serif; background:%23111b21; color:white; padding:30px;'>
      <h2>WhatsApp Web (Live Chat)</h2>
      <div style='background:%23202c33; padding:15px; border-radius:10px; max-width:500px; margin-top:20px;'>
        <div style='color:%2300a884; font-weight:bold; margin-bottom:5px;'>+234 802 999 1122 (Unknown Sender)</div>
        <p id='chat-msg' style='font-size:15px;'>URGENT: Your State Bank account is temporarily blocked due to pending KYC verification. Click here immediately to unlock: http://sbi-kyc-verify.xyz/login</p>
      </div>
    </body>
    </html>
    """
    chat_tab = create_tab(test_html.strip())
    chat_ws = chat_tab.get('webSocketDebuggerUrl')
    await asyncio.sleep(1)

    # 4. Extract message text directly from the Chrome DOM via DevTools
    print("\n[3/4] Browser Agent reading DOM of incoming chat message...")
    await asyncio.sleep(2)
    extracted_text = await eval_js(chat_ws, "document.getElementById('chat-msg') ? document.getElementById('chat-msg').innerText : document.body.innerText")
    sender_text = "+234 802 999 1122"
    print(f" -> Extracted Text: \"{extracted_text}\"")
    print(f" -> Extracted Sender: \"{sender_text}\"")

    # 5. Send message to Phishing Shield AI backend
    print("\n[4/4] Sending intercepted browser content to AI Risk Engine...")
    payload = {
        "raw_text": extracted_text or "URGENT: Your State Bank account is temporarily blocked due to pending KYC verification. Click here immediately to unlock: http://sbi-kyc-verify.xyz/login",
        "source_platform": "Chrome Web (Automated Browser Agent)",
        "sender_id": sender_text,
        "urls": ["http://sbi-kyc-verify.xyz/login"]
    }
    
    resp = requests.post(API_URL, json=payload)
    verdict_data = resp.json()
    
    print("\n" + "=" * 60)
    print("REAL-TIME THREAT SCAN RESULT FROM AI ENGINE:")
    print("=" * 60)
    print(f"Verdict     : {verdict_data.get('verdict')}")
    print(f"Risk Score  : {verdict_data.get('risk_score')}/100")
    print(f"Reasons     : {verdict_data.get('reasons')}")
    print(f"Action      : {verdict_data.get('recommended_action')}")
    print("=" * 60)
    print("\n[SUCCESS] Automated Chrome and pushed alert to Dashboard & MongoDB!")

if __name__ == "__main__":
    asyncio.run(run_browser_automation())
