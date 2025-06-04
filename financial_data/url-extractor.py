from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service

# Use a raw string for Windows paths to avoid unicode errors
PATH = r"C:\Users\shubh\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"  

options = webdriver.ChromeOptions()
options.add_argument("--headless")

service = Service(PATH)
driver = webdriver.Chrome(service=service, options=options)

search_id = "Menu_ctrlAutoCompleteExtender1_TxtAutoComplete"
xpath = "/html/body/ul/li[1]/a/div"
URL = "http://www.religareonline.com/"

with open('ind_nifty500list.csv', 'r') as f:
    data = f.read()

companies = [c.strip() for c in data.split("\n") if c.strip()]
urls = []

with open("company_urls.txt", 'a') as f:
    for company in companies:
        try:
            driver.get(URL)
            driver.find_element("id", search_id).clear()
            input_s = driver.find_element("id", search_id)
            input_s.send_keys(company)
            time.sleep(1)
            driver.find_element("xpath", xpath).click()
            f.write(driver.current_url + "\n")
            print(f"done: {company}")
        except Exception as e:
            print(f"Error for {company}: {e}")
            continue

driver.quit()