from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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
            # Wait up to 10 seconds for the element to be present
            input_s = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, search_id))
            )
            input_s.clear()
            input_s.send_keys(company)
            time.sleep(1)
            driver.find_element(By.XPATH, xpath).click()
            f.write(driver.current_url + "\n")
            print(f"done: {company}")
        except Exception as e:
            print(f"Error for {company}: {e}")
            continue

driver.quit()