import json
import logging
import random
import time
from urllib.parse import quote, urlencode
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import UserInfo
from ..utils import search_request, get_json_data, filter_requests, get_user_data
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_id
from ..constants import INSTAGRAM_DOMAIN, GRAPHQL_QUERY_PATH, FOLLOWING_DOC_ID

logger = logging.getLogger("crawlinsta")


@driver_implicit_wait(10)
def collect_user_info(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                      username: str) -> Json:
    """Collect user information through `username`, including `user_id`, `username`,
    `profile_pic_url`, `biography`, `post_count`, `follower_count`, `following_count`.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.

    Returns:
        Json: user information in json format.

    Raises:
        ValueError: if the user with the given username is not found.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_user_info
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_user_info(driver, "nasa")
        {
          "id": "528817151",
          "username": "nasa",
          "fullname": "NASA",
          "biography": "Exploring the universe and our home planet.",
          "follower_count": 97956738,
          "following_count": 77,
          "following_tag_count": 10,
          "is_private": false,
          "is_verified": true,
          "profile_pic_url": "https://dummy.pic.com",
          "post_count": 4116,
        }
    """
    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.SystemRandom().randint(4, 6))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    if not json_requests:
        raise ValueError(f"User {username} not found.")

    user_data = get_user_data(json_requests, username)
    user_id = extract_id(user_data)

    following_hashtags_number = 0
    if not user_data["is_private"]:
        following_btn_xpath = f"//a[@href='/{username}/following/'][@role='link']"
        following_btn = driver.find_element(By.XPATH, following_btn_xpath)
        following_btn.click()

        time.sleep(random.SystemRandom().randint(3, 5))

        hashtag_btn = driver.find_element(By.XPATH, "//span[text()='Hashtags']")
        hashtag_btn.click()
        time.sleep(random.SystemRandom().randint(4, 6))

        json_requests += filter_requests(driver.requests)
        del driver.requests

        variables = dict(id=user_id)
        query_dict = dict(doc_id=FOLLOWING_DOC_ID, variables=json.dumps(variables, separators=(',', ':')))
        target_url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?{urlencode(query_dict, quote_via=quote)}"
        idx = search_request(json_requests, target_url)
        if idx is not None:
            request = json_requests.pop(idx)
            json_data = get_json_data(request.response)
            following_hashtags_number = json_data["data"]['user']['edge_following_hashtag']['count']
        else:
            logger.warning(f"Following hashtags number not found for user '{username}'.")

    result = UserInfo(id=user_id,
                      username=user_data["username"],
                      fullname=user_data["full_name"],
                      profile_pic_url=user_data["profile_pic_url"],
                      is_private=user_data["is_private"],
                      is_verified=user_data["is_verified"],
                      follower_count=user_data["edge_followed_by"]["count"],
                      following_count=user_data["edge_follow"]["count"],
                      following_tag_count=following_hashtags_number,
                      post_count=user_data["edge_owner_to_timeline_media"]["count"],
                      biography=user_data["biography"])
    return result.model_dump(mode="json")
