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
    def check_request_data(request, music_id, max_id=""):
        request_data = parse_qs(request.body.decode())
        if request_data.get("max_id", [""])[0] != max_id:
            return False
        elif request_data.get("audio_cluster_id", [""])[0] != music_id:
            return False
        return True

    if n <= 0:
        raise ValueError("The number of posts to collect must be a positive integer.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/reels/audio/{music_id}/')
    time.sleep(random.SystemRandom().randint(4, 6))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    if not json_requests:
        raise ValueError(f"Music id '{music_id}' not found.")

    # get first 12 documents
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/clips/music/"
    idx = search_request(json_requests, target_url, JsonResponseContentType.application_json,
                         check_request_data, music_id)
    if idx is None:
        logger.warning(f"No data found for music id '{music_id}'.")
        return MusicPosts(posts=[], music=Music(id=music_id), count=0).model_dump(mode="json")  # type: ignore

    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)
    results.append(json_data)
    remaining -= len(json_data["items"])

    while results[-1]["paging_info"]['more_available'] and remaining > 0:
        footer = driver.find_element(By.XPATH, "//footer")
        driver.execute_script("return arguments[0].scrollIntoView(true);", footer)

        time.sleep(random.SystemRandom().randint(4, 6))
        json_requests += filter_requests(driver.requests)
        del driver.requests

        idx = search_request(json_requests, target_url, JsonResponseContentType.application_json,
                             check_request_data, music_id, results[-1]["paging_info"]['max_id'])
        if idx is None:
            break
        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)
        results.append(json_data)
        remaining -= len(json_data["items"])

    posts = []
    for result in results:
        for item in result['items']:
            post = extract_post(item["media"])
            posts.append(post)

    metadata = results[0]["metadata"]
    media_count = results[0]["media_count"]
    if metadata.get("music_info"):
        music_basic = extract_music_info(metadata["music_info"])
    else:
        music_basic = extract_sound_info(metadata["original_sound_info"])
    music = Music(**music_basic.model_dump(),
                  clips_count=media_count["clips_count"],
                  photos_count=media_count["photos_count"])
    posts = posts[:n]
    return MusicPosts(posts=posts, music=music, count=len(posts)).model_dump(mode="json")
