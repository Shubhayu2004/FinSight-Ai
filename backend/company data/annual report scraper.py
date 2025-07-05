from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time
import random
import requests

def scrape_nse_latest_annual_report(symbol_or_name, download_path=None, headless=True):
    """
    Scrape NSE annual reports page for the latest annual report.
    
    Args:
        symbol_or_name (str): Company symbol or name
        download_path (str): Optional path to download the PDF
        headless (bool): Run browser in headless mode
    
    Returns:
        dict: Contains 'pdf_url', 'title', and optionally 'local_path' if downloaded
    """
    # Setup Chrome options
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")

    try:
        print(f"🔍 Starting scraper for: {symbol_or_name}")
        
        # Launch driver (let Selenium find chromedriver automatically)
        driver = webdriver.Chrome(options=options)
        
        # Hide Selenium automation flag
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        # Go to NSE annual reports page
        print("🌐 Loading NSE annual reports page...")
        driver.get("https://www.nseindia.com/companies-listing/corporate-filings-annual-reports")
        time.sleep(random.uniform(2, 3))

        # Find the input box and type company name
        print(f"🔎 Searching for company: {symbol_or_name}")
        search_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "ARCompanyInput"))
        )
        search_box.clear()
        search_box.send_keys(symbol_or_name)
        time.sleep(2)  # wait for suggestions

        # Check if suggestions appeared
        try:
            suggestions = driver.find_elements(By.CSS_SELECTOR, "ul#ARCompanyInput_listbox li")
            print(f"📋 Found {len(suggestions)} suggestions")
            if suggestions:
                for i, suggestion in enumerate(suggestions[:3]):  # Show first 3
                    print(f"   {i+1}. {suggestion.text}")
            else:
                print("❌ No suggestions found - company might not exist on NSE")
                return {'success': False, 'error': 'Company not found on NSE'}
        except Exception as e:
            print(f"⚠️ Could not check suggestions: {e}")

        # Wait and click the first suggestion
        try:
            first_suggestion = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "ul#ARCompanyInput_listbox li"))
            )
            first_suggestion.click()
            print(f"✅ Selected company: {symbol_or_name}")
            time.sleep(3)  # Wait for table to load
        except Exception as e:
            print(f"❌ Could not select company: {e}")
            return {'success': False, 'error': 'Could not select company from suggestions'}

        # Wait for PDF rows to appear
        try:
            rows = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'table tbody tr'))
            )
            print(f"📊 Found {len(rows)} rows in the table")
        except Exception as e:
            print(f"❌ No table rows found: {e}")
            return {'success': False, 'error': 'No filings found for this company'}

        # Loop through rows and find first one with a PDF icon
        pdf_url = None
        report_title = None
        for i, row in enumerate(rows):
            try:
                row_text = row.text.strip()
                print(f"Row {i+1}: {row_text[:100]}...")  # Show first 100 chars
                
                pdf_icon = row.find_element(By.CSS_SELECTOR, "img[alt$='pdf ATTACHMENT']")
                parent = pdf_icon.find_element(By.XPATH, "./ancestor::a")
                pdf_url = parent.get_attribute("href")
                report_title = row_text.split('\n')[0]
                print(f"✅ Found PDF in row {i+1}")
                break
            except Exception as e:
                print(f"Row {i+1}: No PDF icon found")
                continue

        if pdf_url:
            print(f"✅ Found latest annual report for {symbol_or_name}:")
            print(f"Title: {report_title}")
            print(f"Link: {pdf_url}")

            result = {
                'pdf_url': pdf_url,
                'title': report_title,
                'success': True
            }

            # Optional: Download PDF
            if download_path:
                try:
                    os.makedirs(os.path.dirname(download_path), exist_ok=True)
                    response = requests.get(pdf_url, stream=True, timeout=30)
                    with open(download_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    result['local_path'] = download_path
                    print(f"📥 PDF downloaded to: {download_path}")
                except Exception as e:
                    print(f"❌ Failed to download PDF: {e}")
                    result['download_error'] = str(e)

            return result
        else:
            print(f"❌ No PDF annual report found for {symbol_or_name}")
            return {'success': False, 'error': 'No annual report found'}

    except Exception as e:
        print(f"❌ Error scraping annual report for {symbol_or_name}: {e}")
        return {'success': False, 'error': str(e)}
    
    finally:
        try:
            driver.quit()
        except:
            pass

# Example usage:
# result = scrape_nse_latest_annual_report("RELIANCE", "reports/reliance_report.pdf")
# print(result)
