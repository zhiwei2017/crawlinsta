import pickle
import time
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union


def login(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
          username: str,
          password: str,
          cookies_path: str = "instagram_cookies.pkl") -> bool:
    """Login to instagram with given credential, and return True if success,
    else False.

    Args:
        driver (:obj:`selenium.webdriver.remote.webdriver.WebDriver`): selenium
         driver for controlling the browser to perform certain actions.
        username (str): username for login.
        password (str): corresponding password for login.

    Returns:
        bool: True, if login successes; otherwise False.

    Examples:
        >>> from crawlinsta import webdriver
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> from crawlinsta.login import login
        >>> login(driver, "your_username", "your_password")
        >>> time.sleep(5)
        >>> driver.quit()
    """
    # Navigate to Instagram's login page
    driver.get('https://www.instagram.com/accounts/login/')

    # Sleep to ensure the page loads properly
    time.sleep(5)

    username_field = driver.find_element(By.NAME, 'username')
    password_field = driver.find_element(By.NAME, 'password')

    username_field.send_keys(username)
    password_field.send_keys(password)

    # Locate and click the login button
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()

    # Sleep to ensure the login process completes
    time.sleep(10)

    # Store cookies in a file
    pickle.dump(driver.get_cookies(), open(cookies_path, "wb"))

    not_turn_on_notifications_btn = driver.find_element(By.XPATH, '//button[@tabindex="0"][text()="Not Now"]')
    not_turn_on_notifications_btn.click()
    return True


def login_with_cookies(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                       cookies_path: str = "instagram_cookies.pkl"):
    """Log into Instagram using stored cookies.

    Args:
        driver (:obj:`selenium.webdriver.remote.webdriver.WebDriver`): selenium
         driver for controlling the browser to perform certain actions.
        cookies_path (str): The path to the file containing cookies.
            Default is "instagram_cookies.pkl".

    Examples:
        >>> from crawlinsta import webdriver
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> from crawlinsta.login import login_with_cookies
        >>> login_with_cookies(driver, 'path_to_cookies_file.pkl')
        >>> time.sleep(5)
        >>> driver.quit()
    """
    driver.get('https://www.instagram.com/')
    cookies = pickle.load(open(cookies_path, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(5)  # Example: Wait for the page to load after setting cookies

    not_turn_on_notifications_btn = driver.find_element(By.XPATH, '//button[@tabindex="0"][text()="Not Now"]')
    not_turn_on_notifications_btn.click()
