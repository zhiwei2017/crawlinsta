import logging
import random
import time
from urllib.parse import quote, urlencode
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import Users
from ..utils import search_request, get_json_data, filter_requests, get_user_data
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_id, create_users_list
from ..constants import INSTAGRAM_DOMAIN, API_VERSION

logger = logging.getLogger("crawlinsta")


@driver_implicit_wait(10)
def collect_followers_of_user(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                              username: str,
                              n: int = 100) -> Json:
    """Collect n followers of the given user. This action depends on the account privacy.
    if the account user limites the visibility of the followers, only the account owner can
    view all followers and anyone besides the account owner can get maximal 50 followers.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of followers, which should be collected. By default,
         it's 100. If it's set to 0, collect all followers.

    Returns:
        Json: all visible followers' user information of the given user in json format.

    Raises:
        ValueError: if the number of followers to collect is not a positive integer.
        ValueError: if the user with the given username is not found.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_followers_of_user
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_followers_of_user(driver, "instagram_username", 100)
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
        raise ValueError("The number of followers to collect must be a positive integer.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.SystemRandom().randint(4, 6))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    if not json_requests:
        raise ValueError(f"User '{username}' not found.")

    # get user data
    user_data = get_user_data(json_requests, username)
    user_id = extract_id(user_data)

    if user_data["is_private"]:
        logger.warning(f"User '{username}' has a private account.")
        return Users(users=[], count=0).model_dump(mode="json")

    followers_btn = driver.find_element(By.XPATH, f"//a[@href='/{username}/followers/'][@role='link']")
    followers_btn.click()
    time.sleep(random.SystemRandom().randint(4, 6))

    json_requests += filter_requests(driver.requests)
    del driver.requests

    # get 50 followers
    query_dict = dict(count=12, search_surface="follow_list_page")
    query_str = urlencode(query_dict, quote_via=quote)
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_id}/followers/?{query_str}"
    idx = search_request(json_requests, target_url)

    if idx is None:
        logger.warning(f"No followers found for user '{username}'.")
        return Users(users=[], count=0).model_dump(mode="json")

    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)
    results.append(json_data)
    remaining -= len(json_data["users"])

    while 'next_max_id' in results[-1] and remaining > 0:
        followers_bottom = driver.find_element(By.XPATH, "//div[@class='_aano']//div[@role='progressbar']")
        driver.execute_script("return arguments[0].scrollIntoView(true);", followers_bottom)

        time.sleep(random.SystemRandom().randint(4, 6))

        json_requests += filter_requests(driver.requests)
        del driver.requests

        query_dict = dict(count=12, max_id=results[-1]['next_max_id'], search_surface="follow_list_page")
        query_str = urlencode(query_dict, quote_via=quote)
        target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_id}/followers/?{query_str}"
        idx = search_request(json_requests, target_url)
        if idx is None:
            break
        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)
        results.append(json_data)
        remaining -= len(json_data["users"])

    users = create_users_list(results, "users")[:n]
    return Users(users=users, count=len(users)).model_dump(mode="json")
