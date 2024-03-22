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

logger = logging.getLogger("crawlinsta")


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
    driver.get(f'{INSTAGRAM_DOMAIN}/explore/tags/{hashtag}')
    time.sleep(random.SystemRandom().randint(4, 6))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    if not json_requests:
        raise ValueError(f"Hashtag '{hashtag}' not found.")

    target_url = f'{INSTAGRAM_DOMAIN}/{API_VERSION}/tags/web_info/?tag_name={hashtag}'
    idx = search_request(json_requests, target_url)
    if idx is None:
        logger.warning(f"No data found for hashtag '{hashtag}'.")
        return Hashtag(id=None, name=hashtag).model_dump(mode="json")  # type: ignore
    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)

    posts = []
    for section in json_data["data"]["top"]["sections"]:
        if section["layout_type"] == "one_by_two_left":
            items = section["layout_content"].get("fill_items", [])
            items += section["layout_content"].get("one_by_two_item", dict()).get("clips", dict()).get("items", [])

        else:
            items = section["layout_content"].get("medias", [])
        for item in items:
            post = extract_post(item["media"])
            posts.append(post)

    tag = Hashtag(id=extract_id(json_data["data"]),
                  name=json_data["data"]["name"],
                  post_count=json_data["data"]["media_count"],
                  profile_pic_url=json_data["data"]["profile_pic_url"],
                  is_trending=json_data["data"]["is_trending"],
                  related_tags=json_data["data"]["related_tags"],
                  subtitle=json_data["data"]["subtitle"],
                  posts=posts)
    return tag.model_dump(mode="json")
