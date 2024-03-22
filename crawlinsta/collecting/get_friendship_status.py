import logging
import random
import time
from urllib.parse import quote, urlencode
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import FriendshipStatus
from ..utils import search_request, get_json_data, filter_requests, get_user_data
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_id
from ..constants import INSTAGRAM_DOMAIN, API_VERSION

logger = logging.getLogger("crawlinsta")


@driver_implicit_wait(10)
def get_friendship_status(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                          username1: str,
                          username2: str) -> Json:
    """Get the relationship between the user with `username1` and the user with `username2`, i.e. finding out who is
    following whom.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        username1 (str): username of the person A.
        username2 (str): username of the person B.

    Returns:
        Json: friendship indication between person A with `username1` and person B with `username2`.

    Raises:
        ValueError: if the user with the given username is not found.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import get_friendship_status
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> get_friendship_status(driver, "instagram_username1", "instagram_username1")
        {
          "following": false,
          "followed_by": true
        }
    """
    following, followed_by = False, False
    for username in [username1, username2]:
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
            continue

        following_btn = driver.find_element(By.XPATH, f"//a[@href='/{username}/following/'][@role='link']")
        following_btn.click()
        time.sleep(random.SystemRandom().randint(4, 6))
        del driver.requests

        searching_username = username2 if username == username1 else username1

        search_input_box = driver.find_element(
            By.XPATH, '//input[@aria-label="Search input"][@placeholder="Search"][@type="text"]')
        search_input_box.send_keys(searching_username)
        time.sleep(random.SystemRandom().randint(6, 8))

        json_requests = filter_requests(driver.requests)
        del driver.requests

        # get first 12 followings
        query_dict = dict(query=searching_username)
        query_str = urlencode(query_dict, quote_via=quote)
        target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_id}/following/?{query_str}"
        idx = search_request(json_requests, target_url)

        if idx is None:
            logger.warning(f"Searching request for user '{searching_username}' in "
                           f"followings of user '{username}' not found.")
            continue

        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)

        for user_info in json_data["users"]:
            if user_info["username"] not in {username1, username2}:
                continue
            elif user_info["username"] == username1:
                following = True
            else:
                followed_by = True
            break

    return FriendshipStatus(following=following, followed_by=followed_by).model_dump(mode="json")

