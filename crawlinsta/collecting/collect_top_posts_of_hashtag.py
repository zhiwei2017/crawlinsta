import logging
import random
import time
from pydantic import Json
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import Hashtag
from ..utils import search_request, get_json_data, filter_requests
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_post, extract_id
from ..constants import INSTAGRAM_DOMAIN, API_VERSION
from .base import CollectBase

logger = logging.getLogger("crawlinsta")


class CollectTopPostsOfHashtag(CollectBase):
    """A class to collect top posts of a given hashtag.

    Attributes:
        driver (Union[Chrome, Edge, Firefox, Safari, Remote]): selenium
         driver for controlling the browser to perform certain actions.
        hashtag (str): hashtag.
        json_requests (list): list of json requests.
        hashtag_data (dict): hashtag data.
    """
    def __init__(self, driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 hashtag: str) -> None:
        """Constructs all the necessary attributes for the CollectTopPostsOfHashtag object.

        Args:
            driver (Union[Chrome, Edge, Firefox, Safari, Remote]): selenium
             driver for controlling the browser to perform certain actions.
            hashtag (str): hashtag.
        """
        super().__init__(driver, f'{INSTAGRAM_DOMAIN}/explore/tags/{hashtag}')
        self.hashtag = hashtag
        self.json_requests = []
        self.hashtag_data = None

    def fetch_data(self) -> None:
        """Fetch data from the requests.

        Raises:
            ValueError: if the hashtag is not found.
        """
        self.json_requests += filter_requests(self.driver.requests)
        del self.driver.requests

        if not self.json_requests:
            raise ValueError(f"Hashtag '{self.hashtag}' not found.")

    def extract_data(self) -> bool:
        """Extract data from the fetched requests.

        Returns:
            bool: True if data is found, False otherwise.
        """
        target_url = f'{INSTAGRAM_DOMAIN}/{API_VERSION}/tags/web_info/?tag_name={self.hashtag}'
        idx = search_request(self.json_requests, target_url)
        if idx is None:
            return False
        request = self.json_requests.pop(idx)
        json_data = get_json_data(request.response)
        self.hashtag_data = json_data
        return True

    def generate_result(self, empty_result: bool = False) -> Json:
        """Generate the result in a json format.

        Args:
            empty_result (bool, optional): if True, return an empty result. Defaults to False.

        Returns:
            Json: Hashtag information in a json format.
        """
        if empty_result:
            return Hashtag(id=None,
                           name=self.hashtag).model_dump(mode="json")  # type: ignore
        posts = []
        for section in self.hashtag_data["data"]["top"]["sections"]:
            if section["layout_type"] == "one_by_two_left":
                items = section["layout_content"].get("fill_items", [])
                items += section["layout_content"].get("one_by_two_item", dict()).get("clips", dict()).get("items", [])

            else:
                items = section["layout_content"].get("medias", [])
            for item in items:
                post = extract_post(item["media"])
                posts.append(post)
        tag = Hashtag(id=extract_id(self.hashtag_data["data"]),
                      name=self.hashtag_data["data"]["name"],
                      post_count=self.hashtag_data["data"]["media_count"],
                      profile_pic_url=self.hashtag_data["data"]["profile_pic_url"],
                      is_trending=self.hashtag_data["data"]["is_trending"],
                      related_tags=self.hashtag_data["data"]["related_tags"],
                      subtitle=self.hashtag_data["data"]["subtitle"],
                      posts=posts)
        return tag.model_dump(mode="json")

    def collect(self) -> Json:
        """Collect top posts of a given hashtag.

        Returns:
            Json: Hashtag information in a json format.
        """
        self.load_webpage()

        self.fetch_data()

        status = self.extract_data()
        if not status:
            logger.warning(f"No data found for hashtag '{self.hashtag}'.")
            return self.generate_result(empty_result=True)

        return self.generate_result(empty_result=False)


@driver_implicit_wait(10)
def collect_top_posts_of_hashtag(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                                 hashtag: str) -> Json:
    """Collect top posts of a given hashtag.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        hashtag (str): hashtag.

    Returns:
        Json: Hashtag information in a json format.

    Raises:
        ValueError: if the hashtag is not found.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_top_posts_of_hashtag
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_top_posts_of_hashtag(driver, "shanghai", True)
        {
          "top_posts": [
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
                "text": "I know what she’s gonna say before she even has the chance 😂#shanghai",
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
    return CollectTopPostsOfHashtag(driver, hashtag).collect()
