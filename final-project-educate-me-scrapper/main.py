from selenium.webdriver.common.by import By
import config
import chrome_facade
from chrome_facade import find_elements_with_wait, prepare_driver, navigate_to_page


def sign_in(driver):
    print("Signing in")
    username = driver.find_element(By.ID, "normal_login_username")
    password = driver.find_element(By.ID, "normal_login_password")
    login_button = driver.find_element(By.CLASS_NAME, "login-form-button")

    username.send_keys(config.LOGIN)
    password.send_keys(config.PASSWORD)
    current_url = driver.current_url
    login_button.click()
    chrome_facade.wait_for_page_load(driver, current_url)
    print("Sign-in completed")


def prepare_page_to_extract(driver):
    print("Preparing the page to extract content")
    enable_video_element = find_elements_with_wait(driver, By.XPATH, "//span[text()='play_circle']")
    enable_video_element[0].click()
    find_elements_with_wait(driver, By.TAG_NAME, "video")
    print("Page preparation completed")
    pass


def build_lesson_url(course_url, lesson_id):
    print(f"Building lesson URL for lesson ID: {lesson_id}")
    lesson_url = f"{course_url}?activeTab=content&lessonId={lesson_id}"
    print(f"Built lesson URL: {lesson_url}")
    return lesson_url


if __name__ == '__main__':
    print("Starting script execution")
    if not config.LOGIN or not config.PASSWORD or not config.COURSE_TO_DOWNLOAD:
        raise ValueError("Please provide LOGIN, PASSWORD and COURSE_TO_DOWNLOAD in config.py")
    driver = prepare_driver()
    try:
        navigate_to_page(driver, 'https://app.educate-me.co/')
        if "signIn" in driver.current_url:
            sign_in(driver)
        available_courses = find_elements_with_wait(driver, By.XPATH, f"//a[contains(@href, 'experiences/')]")
        print(f"Found {len(available_courses)} available courses")
        course_to_download_urls = [c.get_attribute('href') for c in available_courses if config.COURSE_TO_DOWNLOAD in c.get_attribute('text')]
        if not course_to_download_urls:
            raise ValueError(f"Course {config.COURSE_TO_DOWNLOAD} not found")
        course_to_download_url = course_to_download_urls[0]
        print(f"Course to download URL: {course_to_download_url}")
        navigate_to_page(driver, course_to_download_url)
        lessons = find_elements_with_wait(driver, By.XPATH, "//div[@id='timeLineContainer']//div[@id != ''][not(.//*[contains(text(), 'Assignment')])]")
        lesson_ids = [l.get_attribute('id') for l in lessons]
        print(f"Found {len(lesson_ids)} lesson IDs")
        for i in range(len(lesson_ids)):
            lesson_id = lesson_ids[i]
            lesson_url = build_lesson_url(course_to_download_url, lesson_id)
            navigate_to_page(driver, lesson_url)
            prepare_page_to_extract(driver)
            with open(f'lessons/lesson_{i}.html', 'w') as file:
                file.write(driver.page_source)
            print(f"Saved lesson {i} to file")
    finally:
        driver.quit()
        print("Driver quit")
