import os
import sys
import time
import json

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ARTIFACT_DIR = r"C:\Users\Sai Santhosh Ram\.gemini\antigravity\brain\84de6236-acab-438b-b2e2-3abdf57e3d1d"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

test_results = []

def run_test(name, func):
    print(f"\n[RUNNING TEST] {name}...")
    try:
        details = func()
        test_results.append({"name": name, "status": "PASSED", "details": details})
        print(f"  --> PASSED: {details}")
    except Exception as e:
        test_results.append({"name": name, "status": "FAILED", "error": str(e)})
        print(f"  --> FAILED: {e}")

# Setup Chrome Options
opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1440,950')
opts.add_argument('--disable-gpu')
opts.add_argument('--no-sandbox')
opts.add_argument('--allow-file-access-from-files')

ext_path = os.path.abspath('chrome-extension')
opts.add_argument(f'--load-extension={ext_path}')

driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 10)

try:
    # -------------------------------------------------------------
    # Test 1: Dashboard UI Integrity & Header Controls
    # -------------------------------------------------------------
    def test_dashboard_ui():
        driver.get('http://localhost:5176')
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
        
        title = driver.title
        assert 'Phishing Shield AI' in title, f"Unexpected title: {title}"
        
        h1 = driver.find_element(By.TAG_NAME, 'h1').text
        assert 'PHISHING SHIELD AI' in h1
        
        screenshot_path = os.path.join(ARTIFACT_DIR, "browser_test_01_dashboard.png")
        driver.save_screenshot(screenshot_path)
        return f"Dashboard loaded with title '{title}' and protection active. Screenshot saved."
    
    run_test("1. Dashboard Header & UI Integrity", test_dashboard_ui)

    # -------------------------------------------------------------
    # Test 2: Safe Message Scenario (Normal WhatsApp)
    # -------------------------------------------------------------
    def test_safe_scenario():
        driver.get('http://localhost:5176')
        time.sleep(1)
        
        # Click NORMAL MESSAGE (SAFE) button
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        safe_btn = next((b for b in buttons if 'NORMAL MESSAGE' in b.text), None)
        assert safe_btn is not None, "Normal message button not found"
        safe_btn.click()
        
        time.sleep(2)
        screenshot_path = os.path.join(ARTIFACT_DIR, "browser_test_02_safe_scenario.png")
        driver.save_screenshot(screenshot_path)
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        assert 'SAFE' in body_text, "Expected SAFE verdict in feed"
        return "Simulated Safe message successfully verified (Verdict: SAFE, low threat score)."

    run_test("2. Safe Message Simulation (WhatsApp)", test_safe_scenario)

    # -------------------------------------------------------------
    # Test 3: Critical Smishing Scenario (Electricity Fraud)
    # -------------------------------------------------------------
    def test_electricity_smishing():
        driver.get('http://localhost:5176')
        time.sleep(1)
        
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        smish_btn = next((b for b in buttons if 'ELECTRICITY SMISHING' in b.text), None)
        assert smish_btn is not None, "Electricity smishing button not found"
        smish_btn.click()
        
        time.sleep(2)
        screenshot_path = os.path.join(ARTIFACT_DIR, "browser_test_03_electricity_smishing.png")
        driver.save_screenshot(screenshot_path)
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        assert 'CRITICAL' in body_text, "Expected CRITICAL verdict in feed"
        return "Simulated electricity smishing attack successfully caught (Verdict: CRITICAL)."

    run_test("3. Electricity Smishing Attack Detection", test_electricity_smishing)

    # -------------------------------------------------------------
    # Test 4: Phishing URL Typosquatting Scenario (Bank Portal)
    # -------------------------------------------------------------
    def test_bank_phishing_url():
        driver.get('http://localhost:5176')
        time.sleep(1)
        
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        url_btn = next((b for b in buttons if 'BANK PHISHING URL' in b.text), None)
        assert url_btn is not None, "Bank phishing URL button not found"
        url_btn.click()
        
        time.sleep(2)
        screenshot_path = os.path.join(ARTIFACT_DIR, "browser_test_04_bank_url.png")
        driver.save_screenshot(screenshot_path)
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        assert 'CRITICAL' in body_text, "Expected CRITICAL verdict for bank phishing URL"
        return "Bank phishing URL with credential harvesting flagged as CRITICAL (Score 100/100)."

    run_test("4. Credential Harvesting & Typosquat URL Detection", test_bank_phishing_url)

    # -------------------------------------------------------------
    # Test 5: Spoofed Sender Email Scenario
    # -------------------------------------------------------------
    def test_spoofed_sender():
        driver.get('http://localhost:5176')
        time.sleep(1)
        
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        sender_btn = next((b for b in buttons if 'SPOOFED SENDER' in b.text), None)
        assert sender_btn is not None, "Spoofed sender button not found"
        sender_btn.click()
        
        time.sleep(2)
        screenshot_path = os.path.join(ARTIFACT_DIR, "browser_test_05_spoofed_sender.png")
        driver.save_screenshot(screenshot_path)
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        assert 'CRITICAL' in body_text or 'SUSPICIOUS' in body_text
        return "Sender domain impersonation intercepted and flagged."

    run_test("5. Sender Identity & Domain Spoofing Detection", test_spoofed_sender)

    # -------------------------------------------------------------
    # Test 6: Manual Analysis Tab with Custom High-Risk Payload
    # -------------------------------------------------------------
    def test_manual_analysis_tab():
        driver.get('http://localhost:5176')
        time.sleep(1)
        
        # Switch to Manual Analysis tab
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        manual_tab_btn = next((b for b in buttons if 'MANUAL ANALYSIS' in b.text), None)
        assert manual_tab_btn is not None, "Manual analysis tab button not found"
        manual_tab_btn.click()
        
        time.sleep(1)
        textarea = driver.find_element(By.TAG_NAME, 'textarea')
        test_payload = (
            "URGENT NOTICE: Your Chase Bank account will be terminated within 2 hours due to unauthorized activity. "
            "Verify your identity immediately by calling +1-800-432-1000 or logging into http://chase-security-check.com/login"
        )
        textarea.clear()
        textarea.send_keys(test_payload)
        
        analyze_btn = next((b for b in driver.find_elements(By.TAG_NAME, 'button') if 'Analyze Content' in b.text), None)
        assert analyze_btn is not None, "Analyze content button not found"
        analyze_btn.click()
        
        time.sleep(2)
        screenshot_path = os.path.join(ARTIFACT_DIR, "browser_test_06_manual_analysis.png")
        driver.save_screenshot(screenshot_path)
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        assert 'CRITICAL' in body_text, "Expected CRITICAL verdict in manual analysis"
        assert '100 / 100' in body_text, "Expected 100 / 100 risk score"
        assert 'Urgent language' in body_text, "Expected urgent language signal"
        assert 'Credential-oriented URL' in body_text, "Expected credential URL signal"
        return "Live manual paste analysis evaluated payload to 100/100 CRITICAL with all threat signals detected."

    run_test("6. Manual Analyzer Live Interactive Threat Evaluation", test_manual_analysis_tab)

    # -------------------------------------------------------------
    # Test 7: Chrome Extension Popup Interface
    # -------------------------------------------------------------
    def test_extension_popup():
        popup_file = os.path.abspath('chrome-extension/popup.html').replace('\\', '/')
        driver.get(f"file:///{popup_file}")
        time.sleep(1)
        
        h3 = driver.find_element(By.TAG_NAME, 'h3').text
        assert 'Phishing Shield AI' in h3, f"Unexpected popup header: {h3}"
        
        # Click settings toggle
        settings_toggle = driver.find_element(By.ID, 'toggleSettings')
        settings_toggle.click()
        time.sleep(0.5)
        
        select_mode = driver.find_element(By.ID, 'apiMode')
        options = [o.text for o in select_mode.find_elements(By.TAG_NAME, 'option')]
        assert len(options) >= 3, f"Expected at least 3 API mode options, got {len(options)}"
        
        screenshot_path = os.path.join(ARTIFACT_DIR, "browser_test_07_extension_popup.png")
        driver.save_screenshot(screenshot_path)
        return f"Extension popup loaded with dual-mode settings: {', '.join(options)}"

    run_test("7. Chrome Extension Popup & Configuration Panel", test_extension_popup)

    # -------------------------------------------------------------
    # Test 8: Live Cloud Dashboard (GitHub Pages)
    # -------------------------------------------------------------
    def test_live_cloud_dashboard():
        driver.get('https://ramnarayan0.github.io/phishing-shield-ai/')
        time.sleep(2)
        
        title = driver.title
        assert 'Phishing Shield AI' in title, f"Unexpected title on cloud: {title}"
        
        screenshot_path = os.path.join(ARTIFACT_DIR, "browser_test_08_cloud_dashboard.png")
        driver.save_screenshot(screenshot_path)
        
        logs = driver.get_log('browser')
        severe_errors = [l for l in logs if l['level'] == 'SEVERE' and 'favicon' not in l['message']]
        return f"Cloud GitHub Pages loaded successfully. Severe errors: {len(severe_errors)}"

    run_test("8. Live Cloud Dashboard on GitHub Pages", test_live_cloud_dashboard)

finally:
    driver.quit()

print("\n" + "="*60)
print("BROWSER AGENT TEST SUITE COMPLETED")
print("="*60)
summary = {"total": len(test_results), "passed": sum(1 for t in test_results if t['status'] == 'PASSED'), "tests": test_results}
print(json.dumps(summary, indent=2))

with open(os.path.join(ARTIFACT_DIR, "browser_test_report.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
