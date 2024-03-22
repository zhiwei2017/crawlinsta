import json
import logging
import random
import time
from urllib.parse import parse_qs
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import Posts
from ..utils import search_request, get_json_data, filter_requests
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_post
from ..constants import INSTAGRAM_DOMAIN, JsonResponseContentType

logger = logging.getLogger("crawlinsta")


@driver_implicit_wait(10)
def collect_posts_of_user(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                          username: str,
                          n: int = 100) -> Json:
    """Collect n posts of the given user. If n is set to 0, collect all posts.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of posts, which should be collected. By default,
         it's 100. If it's set to 0, collect all posts.

    Returns:
        Json: all visible post of the given user in json format.

    Raises:
        ValueError: if the number of posts to collect is not a positive integer.
        ValueError: if the user with the given username is not found.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_posts_of_user
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_posts_of_user(driver, "dummy_instagram_username", 100)
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
              "media_type": "Photo",
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
    def check_request_data(request, username, after=""):
        request_data = parse_qs(request.body.decode())
        variables = json.loads(request_data.get("variables", ["{}"])[0])
        if request_data.get("av", [''])[0] != "17841461911219001":
            return False
        elif not variables:
            return False
        elif variables.get("username", "") != username:
            return False
        elif variables.get("after", "") != after:
            return False
        return True

    if n <= 0:
        raise ValueError("The number of posts to collect must be a positive integer.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.SystemRandom().randint(4, 6))

    json_requests = filter_requests(driver.requests, JsonResponseContentType.text_javascript)
    del driver.requests

    if not json_requests:
        raise ValueError(f"User '{username}' not found.")

    # get first 12 documents
    target_url = f"{INSTAGRAM_DOMAIN}/api/graphql"
    idx = search_request(json_requests, target_url,
                         JsonResponseContentType.text_javascript,
                         check_request_data, username)
    if idx is None:
        logger.warning(f"No posts found for user '{username}'.")
        return Posts(posts=[], count=0).model_dump(mode="json")  # type: ignore

    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]
    results.append(json_data)
    remaining -= len(json_data["edges"])

    while results[-1]['page_info']["has_next_page"] and remaining > 0:
        footer = driver.find_element(By.XPATH, "//footer")
        driver.execute_script("return arguments[0].scrollIntoView(true);", footer)

        time.sleep(random.SystemRandom().randint(4, 6))
        json_requests += filter_requests(driver.requests, JsonResponseContentType.text_javascript)
        del driver.requests

        idx = search_request(json_requests, target_url, JsonResponseContentType.text_javascript,
                             check_request_data, username, after=results[-1]['page_info']["end_cursor"])
        if idx is None:
            break
        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]
        results.append(json_data)
        remaining -= len(json_data["edges"])

    posts = []
    for result in results:
        for item in result['edges']:
            post = extract_post(item["node"])
            posts.append(post)
    posts = posts[:n]
    return Posts(posts=posts, count=len(posts)).model_dump(mode="json")
