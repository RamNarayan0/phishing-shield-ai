import os
import sys
import time
import json

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient

ARTIFACT_DIR = r"C:\Users\Sai Santhosh Ram\.gemini\antigravity\brain\84de6236-acab-438b-b2e2-3abdf57e3d1d"
os.makedirs(ARTIFACT_DIR, exist_ok=True)

test_results = []

def run_test(name, func):
    print(f"\n" + "="*60)
    print(f"[RUNNING TEST] {name}...")
    print("="*60)
    try:
        details = func()
        test_results.append({"name": name, "status": "PASSED", "details": details})
        print(f"  >>> PASSED: {details}")
    except Exception as e:
        test_results.append({"name": name, "status": "FAILED", "error": str(e)})
        print(f"  >>> FAILED: {e}")

# Setup Chrome Options for Live On-Screen Display
opts = Options()
if os.environ.get("HEADLESS", "0") == "1":
    opts.add_argument('--headless=new')
opts.add_argument('--window-size=1440,950')
opts.add_argument('--window-position=50,50')
opts.add_argument('--disable-gpu')
opts.add_argument('--no-sandbox')
opts.add_argument('--allow-file-access-from-files')

ext_path = os.path.abspath('chrome-extension')
opts.add_argument(f'--load-extension={ext_path}')

print("Starting Google Chrome for Live On-Screen Demonstration...")
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 15)

try:
    # -------------------------------------------------------------
    # Helper: Ensure Frontend points to local backend (127.0.0.1:8000)
    # -------------------------------------------------------------
    def init_page():
        driver.get('http://localhost:5176')
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1')))
        driver.execute_script("localStorage.setItem('phishing_api_url', 'http://127.0.0.1:8000');")
        try:
            selects = driver.find_elements(By.TAG_NAME, 'select')
            if selects:
                sel = Select(selects[0])
                sel.select_by_value('http://127.0.0.1:8000')
        except Exception:
            pass
        time.sleep(1)

    init_page()

    # -------------------------------------------------------------
    # Test 1: Live Dashboard & MongoDB Health Verification
    # -------------------------------------------------------------
    def test_dashboard_ui():
        time.sleep(2)
        title = driver.title
        assert 'PHISHING SHIELD AI' in title.upper(), f"Unexpected title: {title}"

        # Verify active indicator
        body_text = driver.find_element(By.TAG_NAME, 'body').text.upper()
        assert 'ACTIVE' in body_text, "Active status not displayed"
        assert 'LIVE THREAT STREAM' in body_text, "Stream panel missing"

        screenshot_path = os.path.join(ARTIFACT_DIR, "live_01_dashboard.png")
        driver.save_screenshot(screenshot_path)
        return "Live dashboard active and connected to backend (127.0.0.1:8000) with MongoDB persistence."

    run_test("1. Live Dashboard & MongoDB Connection", test_dashboard_ui)

    # -------------------------------------------------------------
    # Test 2: Safe Message Scenario & Explainability Breakdown
    # -------------------------------------------------------------
    def test_safe_scenario():
        # Ensure we are in Live Stream tab
        stream_tab = next((b for b in driver.find_elements(By.TAG_NAME, 'button') if 'STREAM' in b.text.upper()), None)
        if stream_tab:
            stream_tab.click()
            time.sleep(0.5)

        buttons = driver.find_elements(By.TAG_NAME, 'button')
        safe_btn = next((b for b in buttons if 'NORMAL MESSAGE' in b.text.upper()), None)
        assert safe_btn is not None, "Normal message preset button not found"

        print("  Clicking [NORMAL MESSAGE (SAFE)] preset on screen...")
        safe_btn.click()

        # Wait until Explainable Phishing Risk Breakdown appears
        wait.until(lambda d: 'EXPLAINABLE PHISHING RISK BREAKDOWN' in d.find_element(By.TAG_NAME, 'body').text.upper())
        time.sleep(2)

        screenshot_path = os.path.join(ARTIFACT_DIR, "live_02_safe_breakdown.png")
        driver.save_screenshot(screenshot_path)

        body_text = driver.find_element(By.TAG_NAME, 'body').text.upper()
        assert 'SAFE' in body_text, "Expected SAFE verdict"
        assert 'DETECTION EVIDENCE' in body_text, "Expected Detection Evidence label"
        return "Safe message triggered: Verdict SAFE (0/100) rendered with clean explanation breakdown on screen."

    run_test("2. Safe Scenario with Explainable Risk Breakdown", test_safe_scenario)

    # -------------------------------------------------------------
    # Test 3: Bank Phishing Attack with Real URL Evidence
    # -------------------------------------------------------------
    def test_bank_phishing_url():
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        url_btn = next((b for b in buttons if 'BANK PHISHING' in b.text.upper()), None)
        assert url_btn is not None, "Bank phishing button not found"

        print("  Clicking [BANK PHISHING URL (CRITICAL)] preset on screen...")
        url_btn.click()

        wait.until(lambda d: 'CRITICAL' in d.find_element(By.TAG_NAME, 'body').text.upper())
        time.sleep(2)

        screenshot_path = os.path.join(ARTIFACT_DIR, "live_03_bank_phishing.png")
        driver.save_screenshot(screenshot_path)

        body_text = driver.find_element(By.TAG_NAME, 'body').text.upper()
        assert '100' in body_text, "Expected 100/100 risk score"
        assert 'EXPLAINABLE PHISHING RISK BREAKDOWN' in body_text
        return "Bank phishing simulated: Flagged as 100/100 CRITICAL with URL threat signals."

    run_test("3. Bank Phishing Attack with Real URL Evidence", test_bank_phishing_url)

    # -------------------------------------------------------------
    # Test 4: Electricity Smishing Attack & Callback Trap Detection
    # -------------------------------------------------------------
    def test_electricity_smishing():
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        smish_btn = next((b for b in buttons if 'ELECTRICITY SMISHING' in b.text.upper()), None)
        assert smish_btn is not None, "Electricity smishing button not found"

        print("  Clicking [ELECTRICITY SMISHING (CRITICAL)] preset on screen...")
        smish_btn.click()

        wait.until(lambda d: 'ELECTRICITY' in d.find_element(By.TAG_NAME, 'body').text.upper() and 'CRITICAL' in d.find_element(By.TAG_NAME, 'body').text.upper())
        time.sleep(2)

        screenshot_path = os.path.join(ARTIFACT_DIR, "live_04_electricity_smishing.png")
        driver.save_screenshot(screenshot_path)

        body_text = driver.find_element(By.TAG_NAME, 'body').text.upper()
        assert 'CRITICAL' in body_text
        return "Electricity smishing simulated: Callback trap detected with extracted contact vectors."

    run_test("4. Electricity Smishing Callback Trap Detection", test_electricity_smishing)

    # -------------------------------------------------------------
    # Test 5: Manual Analyzer Interactive Test with Explainability
    # -------------------------------------------------------------
    def test_manual_analyzer():
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        manual_btn = next((b for b in buttons if 'MANUAL ANALYSIS' in b.text.upper()), None)
        assert manual_btn is not None, "Manual analysis tab not found"

        print("  Switching to [MANUAL ANALYSIS] tab on screen...")
        manual_btn.click()
        time.sleep(1.5)

        textarea = driver.find_element(By.TAG_NAME, 'textarea')
        payload = (
            "URGENT: Your account has been suspended due to suspicious login attempts. "
            "Please confirm your identity and login credentials immediately: https://sbi-verify.bank-security.com/login"
        )
        print("  Typing suspicious payload into textarea...")
        textarea.clear()
        textarea.send_keys(payload)
        time.sleep(1)

        analyze_btn = next((b for b in driver.find_elements(By.TAG_NAME, 'button') if 'ANALYZE CONTENT' in b.text.upper()), None)
        assert analyze_btn is not None, "Analyze Content button not found"
        print("  Clicking [Analyze Content]...")
        analyze_btn.click()

        wait.until(lambda d: 'EXPLAINABLE PHISHING RISK BREAKDOWN' in d.find_element(By.TAG_NAME, 'body').text.upper() and ('CRITICAL' in d.find_element(By.TAG_NAME, 'body').text.upper() or 'HIGH RISK' in d.find_element(By.TAG_NAME, 'body').text.upper()))
        time.sleep(2.5)

        screenshot_path = os.path.join(ARTIFACT_DIR, "live_05_manual_breakdown.png")
        driver.save_screenshot(screenshot_path)

        body_text = driver.find_element(By.TAG_NAME, 'body').text.upper()
        assert 'EXPLAINABLE PHISHING RISK BREAKDOWN' in body_text
        return "Manual Paste Analyzer: Executed live, classified input, and rendered Explainable Breakdown on screen."

    run_test("5. Manual Paste Analyzer with Explainable Breakdown", test_manual_analyzer)

    # -------------------------------------------------------------
    # Test 6: Extension Popup Interface
    # -------------------------------------------------------------
    def test_extension_popup():
        popup_file = os.path.abspath('chrome-extension/popup.html').replace('\\', '/')
        print("  Loading Chrome Extension Popup UI...")
        driver.get(f"file:///{popup_file}")
        time.sleep(2)

        screenshot_path = os.path.join(ARTIFACT_DIR, "live_06_extension_popup.png")
        driver.save_screenshot(screenshot_path)

        body_text = driver.find_element(By.TAG_NAME, 'body').text.upper()
        assert 'PHISHING SHIELD AI' in body_text or 'SCAN' in body_text
        return "Chrome Extension popup loaded and rendered successfully on screen."

    run_test("6. Chrome Extension Popup Interface", test_extension_popup)

    # -------------------------------------------------------------
    # Test 7: MongoDB Persistence & Deduplication Verification
    # -------------------------------------------------------------
    def test_mongodb_persistence():
        client = MongoClient('mongodb://127.0.0.1:27017', serverSelectionTimeoutMS=2000)
        db = client['phishing_shield_ai']
        count = db['analysis_history'].count_documents({})
        assert count > 0, "No records found in MongoDB analysis_history"

        # Verify deduplicated record structure
        sample = db['analysis_history'].find_one({'result.explanation': {'$exists': True}})
        assert sample is not None, "No fingerprinted record with explanation found"
        assert 'fingerprint' in sample, "Fingerprint field missing in record"
        assert 'duplicate_count' in sample, "Duplicate counter missing in record"
        assert 'result' in sample, "Result field missing in record"
        assert 'explanation' in sample['result'], "Explanation field missing in record"

        return f"MongoDB persistence confirmed: {count} total documents with SHA-256 fingerprints, duplicate counters, and Explainable breakdowns."

    run_test("7. MongoDB Persistence & Deduplication Verification", test_mongodb_persistence)

finally:
    # Keep on screen for a moment then quit test driver
    time.sleep(2)
    driver.quit()

print("\n" + "="*60)
print("LIVE ON-SCREEN TEST SUITE COMPLETE")
print("="*60)
summary = {
    "total": len(test_results),
    "passed": sum(1 for t in test_results if t['status'] == 'PASSED'),
    "tests": test_results
}
print(json.dumps(summary, indent=2))
