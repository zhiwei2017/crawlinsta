import logging
import random
import time
from urllib.parse import quote, urlencode
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import FriendshipStatus
from ..utils import search_request, get_json_data, filter_requests
from ..decorators import driver_implicit_wait
from ..constants import INSTAGRAM_DOMAIN, API_VERSION, JsonResponseContentType
from .base import UserIDRequiredCollect

logger = logging.getLogger("crawlinsta")


class GetFriendshipStatus(UserIDRequiredCollect):
    """Base class for collecting posts."""
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 searching_username: str):
        """Initialize CollectPostsBase.

        Args:
            driver ():
            username ():
            n ():
            target_url ():
            collect_type ():
            json_data_key ():
        """
        super().__init__(driver, username, f'{INSTAGRAM_DOMAIN}/{username}/')
        self.searching_username = searching_username
        self.json_requests = []
        self.json_data = None

    def extract_data(self):
        """Get posts data.

        Args:
            json_requests ():
            after ():

        Returns:

        """
        query_dict = dict(query=self.searching_username)
        query_str = urlencode(query_dict, quote_via=quote)
        target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{self.user_id}/following/?{query_str}"
        idx = search_request(self.json_requests, target_url,
                             JsonResponseContentType.application_json)

        if idx is None:
            return False

        request = self.json_requests.pop(idx)
        self.json_data = get_json_data(request.response)
        return True

    def fetch_data(self):
        """Loading action."""
        following_btn = self.driver.find_element(By.XPATH, f"//a[@href='/{self.username}/following/'][@role='link']")
        following_btn.click()
        time.sleep(random.SystemRandom().randint(4, 6))
        del self.driver.requests

        search_input_box = self.driver.find_element(
            By.XPATH, '//input[@aria-label="Search input"][@placeholder="Search"][@type="text"]')
        search_input_box.send_keys(self.searching_username)
        time.sleep(random.SystemRandom().randint(6, 8))

        self.json_requests = filter_requests(self.driver.requests,
                                             JsonResponseContentType.application_json)
        del self.driver.requests

    def collect(self):
        """Collect posts.

        Args:
            url ():
            primary_key ():
            secondary_key ():

        Returns:

        """
        self.load_webpage()

        # get the media id for later requests filtering
        is_private_account = self.get_user_id()
        del self.driver.requests

        if is_private_account:
            logger.warning(f"User '{self.username}' has a private account.")
            return False

        self.fetch_data()
        status = self.extract_data()
        if not status:
            logger.warning(f"Searching request for user '{self.searching_username}' in "
                           f"followings of user '{self.username}' not found.")
            return False

        for user_info in self.json_data["users"]:
            if user_info["username"] != self.searching_username:
                continue
            return True
        return False


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
    followed_by = GetFriendshipStatus(driver, username1, username2).collect()
    following = GetFriendshipStatus(driver, username2, username1).collect()
    return FriendshipStatus(following=following,
                            followed_by=followed_by).model_dump(mode="json")
