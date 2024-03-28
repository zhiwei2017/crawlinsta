import logging
import random
import time
from urllib.parse import parse_qs
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import MusicPosts, Music
from ..utils import search_request, get_json_data, filter_requests
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_post, extract_music_info, extract_sound_info
from ..constants import INSTAGRAM_DOMAIN, API_VERSION, JsonResponseContentType

logger = logging.getLogger("crawlinsta")


class CollectPostsByMusicId:
    """Base class for collecting posts."""
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 music_id: str,
                 n: int,
                 url,
                 target_url: str,
                 collect_type: str):
        """Initialize CollectPostsBase.

        Args:
            driver ():
            username ():
            n ():
            target_url ():
            collect_type ():
            json_data_key ():
        """
        self.driver = driver
        self.music_id = music_id
        if n <= 0:
            raise ValueError(f"The number of {collect_type} to collect "
                             f"must be a positive integer.")
        self.n = n
        self.url = url
        self.target_url = target_url
        self.collect_type = collect_type
        self.json_data_list = []
        self.remaining = n
        self.json_requests = []

    def check_request_data(self, request, max_id=""):
        request_data = parse_qs(request.body.decode())
        if request_data.get("max_id", [""])[0] != max_id:
            return False
        elif request_data.get("audio_cluster_id", [""])[0] != self.music_id:
            return False
        return True

    def get_posts_data(self, max_id=""):
        """Get posts data.

        Args:
            json_requests ():
            after ():

        Returns:

        """
        idx = search_request(self.json_requests, self.target_url,
                             JsonResponseContentType.application_json,
                             self.check_request_data, max_id)
        if idx is None:
            return False

        request = self.json_requests.pop(idx)
        json_data = get_json_data(request.response)
        self.json_data_list.append(json_data)
        self.remaining -= len(json_data["items"])
        return True

    def loading_action(self):
        """Loading action."""
        footer = self.driver.find_element(By.XPATH, "//footer")
        self.driver.execute_script("return arguments[0].scrollIntoView(true);", footer)
        time.sleep(random.SystemRandom().randint(4, 6))

        self.json_requests += filter_requests(self.driver.requests,
                                              JsonResponseContentType.application_json)
        del self.driver.requests

    def create_post_list(self):
        """Create post list.

        Args:
            primary_key ():
            secondary_key ():

        Returns:

        """
        posts = []
        for result in self.json_data_list:
            for item in result['items']:
                item_dict = item["media"]
                post = extract_post(item_dict)
                posts.append(post)
        return posts

    def get_music_info(self, metadata, media_count):
        if metadata.get("music_info"):
            music_basic = extract_music_info(metadata["music_info"])
        else:
            music_basic = extract_sound_info(metadata["original_sound_info"])
        music = Music(**music_basic.model_dump(),
                      clips_count=media_count["clips_count"],
                      photos_count=media_count["photos_count"])
        return music

    def collect(self):
        """Collect posts.

        Args:
            url ():
            primary_key ():
            secondary_key ():

        Returns:

        """
        self.driver.get(self.url)
        time.sleep(random.SystemRandom().randint(4, 6))

        self.json_requests += filter_requests(self.driver.requests,
                                              JsonResponseContentType.application_json)
        del self.driver.requests

        if not self.json_requests:
            raise ValueError(f"Music id '{self.music_id}' not found.")

        # get first 12 documents
        status = self.get_posts_data()
        if not status:
            logger.warning(f"No data found for music id '{self.music_id}'.")
            return MusicPosts(posts=[], music=Music(id=self.music_id), count=0).model_dump(mode="json")  # type: ignore

        while self.json_data_list[-1]['paging_info']["more_available"] and self.remaining > 0:
            self.loading_action()
            status = self.get_posts_data(max_id=self.json_data_list[-1]["paging_info"]['max_id'])
            if not status:
                break

        posts = self.create_post_list()[:self.n]
        music = self.get_music_info(self.json_data_list[0]["metadata"],
                                    self.json_data_list[0]["media_count"])
        return MusicPosts(posts=posts, music=music, count=len(posts)).model_dump(mode="json")


@driver_implicit_wait(10)
def collect_posts_by_music_id(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                              music_id: str,
                              n: int = 100) -> Json:
    """Collect n posts containing the given music_id. If n is set to 0, collect all posts.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        music_id (str): id of the music.
        n (int): maximum number of posts, which should be collected. By default, it's 100.
         If it's set to 0, collect all posts.

    Returns:
        Json: a list of posts containing the music.

    Raises:
        ValueError: if the number of posts to collect is not a positive integer.
        ValueError: if the music id is not found.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_posts_by_music_id
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_posts_by_music_id(driver, "2614441095386924", 100)
        {
          "posts": [
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
    return CollectPostsByMusicId(driver, music_id, n, f'{INSTAGRAM_DOMAIN}/reels/audio/{music_id}/',
                                 f"{INSTAGRAM_DOMAIN}/{API_VERSION}/clips/music/", "posts").collect()
