import logging
from pydantic import Json
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union, Dict, Any
from ..decorators import driver_implicit_wait
from ..constants import INSTAGRAM_DOMAIN, API_VERSION
from .base import CollectUsersBase

logger = logging.getLogger("crawlinsta")


class CollectFollowingsOfUser(CollectUsersBase):
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 n: int = 100):
        target_url_format = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/" + "{user_id}/following/?{query_str}"
        fetch_data_btn_xpath = f"//a[@href='/{username}/following/'][@role='link']"
        url = f'{INSTAGRAM_DOMAIN}/{username}/'
        super().__init__(driver, username, n, url, target_url_format, "followings", fetch_data_btn_xpath)

    def get_request_query_dict(self) -> Dict[str, Any]:
        """Get request query dict."""
        if not self.json_data_list:
            return dict(count=12)
        return dict(count=12, max_id=self.json_data_list[-1]['next_max_id'])


@driver_implicit_wait(10)
def collect_followings_of_user(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                               username: str,
                               n: int = 100) -> Json:
    """Collect n followings of the given user.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of followings, which should be collected. By default,
         it's 100. If it's set to 0, collect all followings.

    Returns:
        Json: all visible followings' user information of the given user in json format.

    Raises:
        ValueError: if the number of followings to collect is not a positive integer.
        ValueError: if the user with the given username is not found.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_followings_of_user
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_followings_of_user(driver, "instagram_username", 100)
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
    return CollectFollowingsOfUser(driver, username, n).collect()
