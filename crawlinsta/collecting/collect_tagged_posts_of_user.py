import json
from urllib.parse import parse_qs
from pydantic import Json
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..utils import filter_requests, get_user_data
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_id
from ..constants import INSTAGRAM_DOMAIN, JsonResponseContentType
from .base import CollectPostsBase


class CollectTaggedPostsOfUser(CollectPostsBase):
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 n: int = 100):
        target_url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        collect_type = "tagged posts"
        json_data_key = "xdt_api__v1__usertags__user_id__feed_connection"
        url = f'{INSTAGRAM_DOMAIN}/{username}/tagged/'
        primary_key = "node"
        secondary_key = None
        super().__init__(driver, username, n, url, target_url, collect_type,
                         json_data_key, primary_key, secondary_key)
        self.user_id = None

    def check_request_data(self, request, after=""):
        request_data = parse_qs(request.body.decode())
        variables = json.loads(request_data.get("variables", ["{}"])[0])
        if request_data.get("av", [''])[0] != "17841461911219001":
            return False
        elif not variables:
            return False
        elif variables.get("user_id", "") != self.user_id:
            return False
        elif variables.get("after", "") != after:
            return False
        return True

    def get_user_id(self):
        json_requests = filter_requests(self.driver.requests,
                                        JsonResponseContentType.application_json)

        if not json_requests:
            raise ValueError(f"User '{self.username}' not found.")

        user_data = get_user_data(json_requests, self.username)
        self.user_id = extract_id(user_data)
        return user_data["is_private"]


@driver_implicit_wait(10)
def collect_tagged_posts_of_user(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                                 username: str,
                                 n: int = 100) -> Json:
    """Collect n posts in which user was tagged. If n is set to 0, collect all tagged posts.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of tagged posts, which should be collected. By
         default, it's 100. If it's set to 0, collect all posts.

    Returns:
        Json: all visible tagged posts in json format.

    Raises:
        ValueError: if the number of tagged posts to collect is not a positive integer.
        ValueError: if the user with the given username is not found.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_tagged_posts_of_user
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_tagged_posts_of_user(driver, "dummy_instagram_username", 100)
        {
          "tagged_posts": [
            {
              "like_count": 817982,
              "comment_count": 3000,
              "id": "3215769692664507668",
              "code": "CygtX9ivC0U",
              "user": {
                "id": "50269116275",
                "username": "dummy_instagram_username",
                "fullname": "",
                "profile_pic_url": "https://scontent.cdninstagram.com/v",
                "is_private": false,
                "is_verified": false
              },
              "taken_at": 1697569769,
              "media_type": "Reel",
              "caption": {
                "id": "17985380039262083",
                "text": "I know what she’s gonna say before she even has the chance 😂",
                "created_at_utc": null
              },
              "accessibility_caption": "",
              "original_width": 1080,
              "original_height": 1920,
              "urls": [
                "https://scontent.cdninstagram.com/o1"
              ],
              "has_shared_to_fb": false,
              "usertags": [],
              "location": null,
              "music": {
                "id": "2614441095386924",
                "is_trending_in_clips": false,
                "artist": {
                  "id": "50269116275",
                  "username": "dummy_instagram_username",
                  "fullname": "",
                  "profile_pic_url": "",
                  "is_private": null,
                  "is_verified": null
                },
                "title": "Original audio",
                "duration_in_ms": null,
                "url": null
              }
            },
            ...
            ],
          "count": 100
        }
    """
    return CollectTaggedPostsOfUser(driver, username, n).collect()
