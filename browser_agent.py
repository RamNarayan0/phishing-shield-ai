import json
import asyncio
import requests
import websockets

CHROME_DEBUG_URL = "http://localhost:9222"

def get_tabs():
    try:
        resp = requests.get(f"{CHROME_DEBUG_URL}/json/list", timeout=3)
        return resp.json()
    except Exception as e:
        print(f"Error getting tabs: {e}")
        return []

def print_open_tabs():
    tabs = get_tabs()
    print(f"\n--- ACTIVE CHROME TABS ({len(tabs)}) ---")
    for i, t in enumerate(tabs):
        print(f"[{i}] {t.get('type')}: {t.get('title')} ({t.get('url')})")
    return tabs

async def eval_js_in_tab(ws_url, js_code):
    async with websockets.connect(ws_url) as ws:
        msg = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": js_code,
                "returnByValue": True
            }
        }
        await ws.send(json.dumps(msg))
        res = await ws.recv()
        data = json.loads(res)
        result = data.get("result", {}).get("result", {}).get("value")
        return result

async def navigate_tab(ws_url, target_url):
    async with websockets.connect(ws_url) as ws:
        msg = {
            "id": 2,
            "method": "Page.navigate",
            "params": {"url": target_url}
        }
        await ws.send(json.dumps(msg))
        res = await ws.recv()
        return json.loads(res)

async def main():
    print("Connecting to Chrome on port 9222...")
    tabs = print_open_tabs()
    
    # Find page tabs (ignore internal iframes / browser UI)
    page_tabs = [t for t in tabs if t.get('type') == 'page']
    print(f"\nUser-visible Page Tabs: {len(page_tabs)}")
    for p in page_tabs:
        print(f" -> {p.get('title')} : {p.get('url')}")

    if page_tabs:
        target = page_tabs[0]
        ws_url = target.get('webSocketDebuggerUrl')
        if ws_url:
            title = await eval_js_in_tab(ws_url, "document.title")
            print(f"\n[SUCCESS] Connected to tab '{title}' via DevTools Protocol!")
            
            # Check current URL
            current_url = await eval_js_in_tab(ws_url, "window.location.href")
            print(f"Current tab URL: {current_url}")

if __name__ == "__main__":
    asyncio.run(main())
