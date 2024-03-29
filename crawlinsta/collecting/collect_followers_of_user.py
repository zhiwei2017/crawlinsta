import logging
from pydantic import Json
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union, Dict, Any
from ..decorators import driver_implicit_wait
from ..constants import INSTAGRAM_DOMAIN, API_VERSION
from .base import CollectUsersBase

logger = logging.getLogger("crawlinsta")


class CollectFollowersOfUser(CollectUsersBase):
    """Collect followers of the given user.

    Attributes:
        driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
        username (str): The username of the user.
        n (int): The number of users to collect.
        target_url_format (str): The target URL format to search for.
        collect_type (str): The type of data to collect.
        json_data_list (List[Dict[str, Any]]): The list of json data.
        remaining (int): The remaining number of users to collect.
        json_requests (List[Dict[str, Any]]): The list of json requests.
        initial_load_data_btn_xpath (str): The xpath of the initial load data button.
    """
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 n: int = 100) -> None:
        """Initialize the CollectFollowersOfUser class.

        Args:
            driver (Union[Chrome, Edge, Firefox, Safari, Remote]):
            username (str): The username of the user.
            n (int): The number of users to collect.
        """
        target_url_format = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/" + "{user_id}/followers/?{query_str}"
        collect_type = "followers"
        initial_load_data_btn_xpath = f"//a[@href='/{username}/followers/'][@role='link']"
        url = f'{INSTAGRAM_DOMAIN}/{username}/'
        super().__init__(driver, username, n, url, target_url_format,
                         collect_type, initial_load_data_btn_xpath)

    def get_request_query_dict(self) -> Dict[str, Any]:
        """Get request query dict.

        Returns:
            Dict[str, Any]: The request query dictionary.
        """
        if not self.json_data_list:
            return dict(count=12, search_surface="follow_list_page")
        return dict(count=12, max_id=self.json_data_list[-1]['next_max_id'],
                    search_surface="follow_list_page")


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
    return CollectFollowersOfUser(driver, username, n).collect()
