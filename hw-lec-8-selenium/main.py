import json
import time

from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def time_logger(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        return result

    return wrapper


@time_logger
def extract_jobs_from_current_page(driver):
    print("Extracting jobs from page")
    jobs = []
    job_elements = driver.find_elements(By.XPATH, '//li[@class="ais-Hits-item"]')
    for job_element in job_elements:
        title = job_element.find_element(By.XPATH, './/h3').text
        url = job_element.find_element(By.XPATH, ".//a[@data-track-trigger='job_listing_link']").get_attribute('href')
        jobs.append({
            "title": title,
            "url": url
        })
    return jobs


@time_logger
def navigate_to_root(driver):
    print("Navigating to root url")
    current_url = driver.current_url
    root_url = 'https://jobs.marksandspencer.com/job-search'
    driver.get(root_url)
    wait_for_page_load(driver, current_url)


@time_logger
def navigate_to_next_page(driver):
    print("Navigating to next page")
    current_url = driver.current_url
    next_button = driver.find_element(By.XPATH, '//a[@aria-label="Next"]')
    next_button.click()
    wait_for_page_load(driver, current_url)


@time_logger
def wait_for_page_load(driver, url_before_action):
    print("Waiting for page to load")
    wait = WebDriverWait(driver, 10)

    @time_logger
    def wait_for_url_to_change():
        wait.until(EC.url_changes(url_before_action))

    @time_logger
    def wait_for_elements_to_appear():
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//li[@class="ais-Hits-item"]')))

    wait_for_url_to_change()
    wait_for_elements_to_appear()


def prepare_driver() -> ChromiumDriver:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0.0.0 Safari/537.36")
    chrome_options.add_argument(f'user-agent={user_agent}')
    service = Service('./chromedriver')
    return webdriver.Chrome(service=service, options=chrome_options)


if __name__ == '__main__':
    driver = prepare_driver()
    jobs = []
    try:
        navigate_to_root(driver)
        jobs += extract_jobs_from_current_page(driver)
        navigate_to_next_page(driver)
        jobs += extract_jobs_from_current_page(driver)
    except StaleElementReferenceException:
        # print(driver.page_source)
        raise
    finally:
        driver.quit()

    with open('jobs.json', 'w') as file:
        json.dump(jobs, file, indent=4)
