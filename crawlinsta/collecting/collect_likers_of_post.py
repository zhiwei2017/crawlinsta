import logging
import random
import time
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import Users
from ..utils import search_request, get_json_data, filter_requests
from ..decorators import driver_implicit_wait
from ..data_extraction import create_users_list
from ..constants import INSTAGRAM_DOMAIN, API_VERSION, JsonResponseContentType
from .base import CollectPostInfoBase

logger = logging.getLogger("crawlinsta")


class CollectLikersOfPost(CollectPostInfoBase):
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 post_code: str,
                 n: int = 100):
        super().__init__(driver,
                         post_code,
                         n,
                         "likers",
                         f"{INSTAGRAM_DOMAIN}/p/{post_code}/")

    def fetch_data(self) -> None:
        likes_btn_xpath = f"//a[@href='/p/{self.post_code}/liked_by/'][@role='link']"
        likes_btn = self.driver.find_element(By.XPATH, likes_btn_xpath)
        likes_btn.click()
        time.sleep(random.SystemRandom().randint(3, 5))

        self.json_requests += filter_requests(self.driver.requests)
        del self.driver.requests

    def extract_data(self) -> bool:
        target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/media/{self.post_id}/likers/"
        idx = search_request(self.json_requests,
                             target_url,
                             JsonResponseContentType.application_json)

        if idx is None:
            return False

        request = self.json_requests.pop(idx)
        json_data = get_json_data(request.response)
        self.json_data_list.append(json_data)
        return True

    def generate_result(self, empty_result=False) -> Json:
        if empty_result:
            return Users(users=[], count=0).model_dump(mode="json")

        likers = create_users_list(self.json_data_list, "users")[:self.n]
        return Users(users=likers, count=len(likers)).model_dump(mode="json")

    def collect(self) -> Json:
        """Collect the users, who likes a given post.

        Returns:
            Json: all likers' user information of the given post in json format.
        """
        self.load_webpage()

        # get the media id for later requests filtering
        self.get_post_id()
        if not self.post_id:
            logger.warning(f"No post id found for post '{self.post_code}'.")
            return self.generate_result(empty_result=True)
        del self.driver.requests

        self.fetch_data()
        status = self.extract_data()
        if not status:
            logger.warning(f"No likers found for post '{self.post_code}'.")
            return self.generate_result(empty_result=True)

        return self.generate_result(empty_result=False)


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
    return CollectLikersOfPost(driver, post_code, n).collect()
