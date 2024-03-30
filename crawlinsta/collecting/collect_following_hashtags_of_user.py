import json
import logging
import random
import time
from urllib.parse import quote, urlencode
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import HashtagBasicInfo, HashtagBasicInfos
from ..utils import search_request, get_json_data, filter_requests
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_id
from ..constants import INSTAGRAM_DOMAIN, GRAPHQL_QUERY_PATH, FOLLOWING_DOC_ID, JsonResponseContentType
from .base import UserIDRequiredCollect

logger = logging.getLogger("crawlinsta")


class CollectFollowingHashtagsOfUser(UserIDRequiredCollect):
    """Base class for collecting posts."""
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 n: int):
        """Initialize CollectPostsBase.

        Args:
            driver ():
            username ():
            n ():
        """
        if n <= 0:
            raise ValueError(f"The number of following hashtags to collect "
                             f"must be a positive integer.")
        super().__init__(driver, username, f'{INSTAGRAM_DOMAIN}/{username}/')
        self.n = n
        self.json_data_list = []
        self.json_requests = []

    def get_target_url(self):
        variables = dict(id=self.user_id)
        query_dict = dict(doc_id=FOLLOWING_DOC_ID,
                          variables=json.dumps(variables, separators=(',', ':')))
        target_url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?{urlencode(query_dict, quote_via=quote)}"
        return target_url

    def extract_data(self):
        """Get posts data.

        Args:
            json_requests ():
            after ():

        Returns:

        """
        target_url = self.get_target_url()
        idx = search_request(self.json_requests, target_url,
                             JsonResponseContentType.application_json)
        if idx is None:
            return False

        request = self.json_requests.pop(idx)
        json_data = get_json_data(request.response)
        self.json_data_list.append(json_data)
        return True

    def fetch_data(self):
        """Loading action."""
        following_btn_xpath = f"//a[@href='/{self.username}/following/'][@role='link']"
        following_btn = self.driver.find_element(By.XPATH, following_btn_xpath)
        following_btn.click()
        time.sleep(random.SystemRandom().randint(3, 5))

        hashtag_btn = self.driver.find_element(By.XPATH, "//span[text()='Hashtags']")
        hashtag_btn.click()
        time.sleep(random.SystemRandom().randint(4, 6))

        self.json_requests += filter_requests(self.driver.requests,
                                              JsonResponseContentType.application_json)
        del self.driver.requests

    def generate_result(self, empty_result=False):
        """Create post list.

        Args:
            primary_key ():
            secondary_key ():

        Returns:

        """
        if empty_result:
            return HashtagBasicInfos(hashtags=[], count=0).model_dump(mode="json")
        hashtags = []
        for json_data in self.json_data_list:
            for item in json_data["data"]['user']['edge_following_hashtag']['edges']:
                hashtag = HashtagBasicInfo(id=extract_id(item["node"]),
                                           name=item["node"]["name"],
                                           post_count=item["node"]["media_count"],
                                           profile_pic_url=item["node"]["profile_pic_url"])
                hashtags.append(hashtag)
        hashtags = hashtags[:self.n]
        return HashtagBasicInfos(hashtags=hashtags, count=len(hashtags)).model_dump(mode="json")

    def collect(self):
        """Collect posts.

        Args:
            url ():
            primary_key ():
            secondary_key ():

        Returns:

        """
        self.load_webpage()

        is_private_account = self.get_user_id()
        del self.driver.requests

        if is_private_account:
            logger.warning(f"User '{self.username}' has a private account.")
            return self.generate_result(empty_result=True)

        self.fetch_data()

        status = self.extract_data()
        if not status:
            logger.warning(f"No following hashtags found for user '{self.username}'.")
            return self.generate_result(empty_result=True)

        return self.generate_result(empty_result=False)


@driver_implicit_wait(10)
def collect_following_hashtags_of_user(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                                       username: str,
                                       n: int = 100) -> Json:
    """Collect n followings hashtags of the given user.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of followings, which should be collected.
         By default, it's 100. If it's set to 0, collect all followings.

    Returns:
        Json: all visible followings hashtags' information of the given user in
        json format.

    Raises:
        ValueError: if the number of following hashtags to collect is not a positive integer.
        ValueError: if the user with the given username is not found.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_following_hashtags_of_user
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_following_hashtags_of_user(driver, "instagram_username", 100)
        {
          "hashtags": [
            {
              "id": "528817151",
              "name": "asiangames",
              "post_count": 1000000,
              "profile_pic_url": "https://dummy.pic.com",
            },
            ...
            ],
          "count": 100
        }
    """
    return CollectFollowingHashtagsOfUser(driver, username, n).collect()

