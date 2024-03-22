import logging
import random
import re
import time
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import Users
from ..utils import search_request, get_json_data, filter_requests
from ..decorators import driver_implicit_wait
from ..data_extraction import create_users_list
from ..constants import INSTAGRAM_DOMAIN, API_VERSION

logger = logging.getLogger("crawlinsta")


@driver_implicit_wait(10)
def collect_likers_of_post(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                           post_code: str,
                           n: int = 100) -> Json:
    """Collect the users, who likes a given post.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        post_code (str): post code, used for generating post directly accessible url.
        n (int): maximum number of likers, which should be collected. By default,
         it's 100. If it's set to 0, collect all likers.

    Returns:
        Json: all likers' user information of the given post in json format.

    Raises:
        ValueError: if the number of likers to collect is not a positive integer.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_likers_of_post
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_likers_of_post(driver, "WGDBS3D", 100)
        {
          "users": [
            {
              "id": "528817151",
              "username": "nasa",
              "fullname": "NASA",
              "is_private": false,
              "is_verified": true,
              "profile_pic_url": "https://dummy.pic.com",
            },
            ...
            ],
          "count": 100
        }
    """
    if n <= 0:
        raise ValueError("The number of likers to collect must be a positive integer.")

    results = []

    driver.get(f"{INSTAGRAM_DOMAIN}/p/{post_code}/")
    time.sleep(random.SystemRandom().randint(4, 6))
    del driver.requests

    # get the media id for later requests filtering
    meta_tag_xpath = "//meta[@property='al:ios:url']"
    meta_tag = driver.find_element(By.XPATH, meta_tag_xpath)
    post_id = re.findall("\d+", meta_tag.get_attribute("content"))  # noqa
    if not post_id:
        return Users(users=[], count=0).model_dump(mode="json")
    post_id = post_id[0]

    likes_btn_xpath = f"//a[@href='/p/{post_code}/liked_by/'][@role='link']"
    likes_btn = driver.find_element(By.XPATH, likes_btn_xpath)
    likes_btn.click()
    time.sleep(random.SystemRandom().randint(3, 5))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    # get 50 likers
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/media/{post_id}/likers/"
    idx = search_request(json_requests, target_url)

    if idx is None:
        logger.warning(f"No likers found for post '{post_code}'.")
        return Users(users=[], count=0).model_dump(mode="json")

    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)
    results.append(json_data)

    likers = create_users_list(results, "users")[:n]
    return Users(users=likers, count=len(likers)).model_dump(mode="json")
