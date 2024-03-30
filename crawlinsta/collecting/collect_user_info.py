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
from ..utils import search_request, get_json_data, filter_requests
from ..decorators import driver_implicit_wait
from ..constants import INSTAGRAM_DOMAIN, GRAPHQL_QUERY_PATH, FOLLOWING_DOC_ID, JsonResponseContentType
from .base import UserIDRequiredCollect

logger = logging.getLogger("crawlinsta")


class CollectUserInfo(UserIDRequiredCollect):
    def __init__(self, driver: Union[Chrome, Edge, Firefox, Safari, Remote], username: str):
        super().__init__(driver, username, f"{INSTAGRAM_DOMAIN}/{username}/")
        self.json_requests = []

    def load_following_hashtags(self):
        following_btn_xpath = f"//a[@href='/{self.username}/following/'][@role='link']"
        following_btn = self.driver.find_element(By.XPATH, following_btn_xpath)
        following_btn.click()

        time.sleep(random.SystemRandom().randint(3, 5))

        hashtag_btn = self.driver.find_element(By.XPATH, "//span[text()='Hashtags']")
        hashtag_btn.click()
        time.sleep(random.SystemRandom().randint(4, 6))

        self.json_requests += filter_requests(self.driver.requests)
        del self.driver.requests

    def get_following_hashtags_number(self):
        variables = dict(id=self.user_id)
        query_dict = dict(doc_id=FOLLOWING_DOC_ID, variables=json.dumps(variables, separators=(',', ':')))
        target_url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?{urlencode(query_dict, quote_via=quote)}"
        idx = search_request(self.json_requests, target_url, JsonResponseContentType.application_json)
        if idx is None:
            logger.warning(f"Following hashtags number not found for user '{self.username}'.")
            return 0
        request = self.json_requests.pop(idx)
        json_data = get_json_data(request.response)
        return json_data["data"]['user']['edge_following_hashtag']['count']

    def collect(self):
        self.load_webpage()

        is_private_account = self.get_user_id()

        following_hashtags_number = 0
        if not is_private_account:
            del self.driver.requests
            self.load_following_hashtags()
            following_hashtags_number = self.get_following_hashtags_number()

        result = UserInfo(id=self.user_id,
                          username=self.user_data["username"],
                          fullname=self.user_data["full_name"],
                          profile_pic_url=self.user_data["profile_pic_url"],
                          is_private=self.user_data["is_private"],
                          is_verified=self.user_data["is_verified"],
                          follower_count=self.user_data["edge_followed_by"]["count"],
                          following_count=self.user_data["edge_follow"]["count"],
                          following_tag_count=following_hashtags_number,
                          post_count=self.user_data["edge_owner_to_timeline_media"]["count"],
                          biography=self.user_data["biography"])
        return result.model_dump(mode="json")


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
    return CollectUserInfo(driver, username).collect()
