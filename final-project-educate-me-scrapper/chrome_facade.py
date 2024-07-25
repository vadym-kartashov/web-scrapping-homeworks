from selenium.common import StaleElementReferenceException
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def prepare_driver() -> ChromiumDriver:
    print("Preparing the Chrome driver")
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0.0.0 Safari/537.36")
    chrome_options.add_argument(f'user-agent={user_agent}')
    service = Service('./chromedriver')

    print("Chrome driver prepared successfully")
    return webdriver.ChromiumDriver(service=service, options=chrome_options)

def navigate_to_page(driver, url):
    if driver.current_url == url :
        print(f"Already on the URL: {url}")
        return
    print(f"Navigating to URL: {url}")
    current_url = driver.current_url
    driver.get(url)
    wait_for_page_load(driver, current_url)
    print(f"Navigation to {url} completed")




def find_elements_with_wait(driver, by: str, query: str):
    print(f"Waiting for elements by {by} with query: {query}")
    elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((by, query))
    )
    if not elements:
        raise StaleElementReferenceException(f"Element not found for {query}")
    print(f"Found {len(elements)} elements for {query}")
    return elements


def wait_for_page_load(driver, url_before_action):
    print("Waiting for the page to load")
    wait = WebDriverWait(driver, 10)

    def wait_for_url_to_change():
        wait.until(EC.url_changes(url_before_action))
        print("URL has changed")

    wait_for_url_to_change()
    print("Page load completed")