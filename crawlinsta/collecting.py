import json
import logging
import random
import re
import time
from urllib.parse import quote, urlencode, parse_qs
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from .schemas import (
    UserBasicInfo, UserProfile, UserInfo, Users, Liker, Likers, Comment,
    Comments, Posts, MusicPosts, HashtagBasicInfo,
    HashtagBasicInfos, Hashtag, SearchingResultHashtag, SearchingResultUser,
    LocationBasicInfo, Place, SearchingResultPlace, SearchingResult,
    FriendshipStatus, Music
)
from .utils import search_request, get_json_data, filter_requests, get_user_data, find_brackets
from .decorators import driver_implicit_wait
from .data_extraction import extract_post, extract_id, extract_music_info, extract_sound_info
from .constants import (
    INSTAGRAM_DOMAIN, GRAPHQL_QUERY_PATH, API_VERSION, FOLLOWING_DOC_ID,
    JsonResponseContentType
)

__all__ = [
    "collect_user_info",
    "collect_posts_of_user",
    "collect_reels_of_user",
    "collect_tagged_posts_of_user",
    "get_friendship_status",
    "collect_followers_of_user",
    "collect_followings_of_user",
    "collect_following_hashtags_of_user",
    "collect_likers_of_post",
    "collect_comments_of_post",
    "search_with_keyword",
    "collect_top_posts_of_hashtag",
    "collect_posts_by_music_id",
    "download_media"
]

logger = logging.getLogger("crawlinsta")


@driver_implicit_wait(10)
def collect_user_info(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                      username: str) -> Json:
    """Collect user information through `username`, including `user_id`, `username`,
    `profile_pic_url`, `biography`, `post_count`, `follower_count`, `following_count`.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.

    Returns:
        Json: user information in json format.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_user_info
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_user_info(driver, "nasa")
        {
          "id": "528817151",
          "username": "nasa",
          "fullname": "NASA",
          "biography": "Exploring the universe and our home planet.",
          "follower_count": 97956738,
          "following_count": 77,
          "following_tag_count": 10,
          "is_private": false,
          "is_verified": true,
          "profile_pic_url": "https://dummy.pic.com",
          "post_count": 4116,
          "usertags_count": 0
        }
    """
    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.randint(4, 6))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    user_data = get_user_data(json_requests, username)
    user_id = extract_id(user_data)

    following_btn_xpath = f"//a[@href='/{username}/following/'][@role='link']"
    following_btn = driver.find_element(By.XPATH, following_btn_xpath)
    following_btn.click()

    time.sleep(random.randint(3, 5))

    hashtag_btn = driver.find_element(By.XPATH, "//span[text()='Hashtags']")
    hashtag_btn.click()
    time.sleep(random.randint(4, 6))

    json_requests += filter_requests(driver.requests)
    del driver.requests

    variables = dict(id=user_id)
    query_dict = dict(doc_id=FOLLOWING_DOC_ID, variables=json.dumps(variables, separators=(',', ':')))
    target_url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?{urlencode(query_dict, quote_via=quote)}"
    idx = search_request(json_requests, target_url)
    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)
    following_hashtags_number = json_data["data"]['user']['edge_following_hashtag']['count']

    result = UserInfo(id=user_id,
                      username=user_data["username"],
                      fullname=user_data["full_name"],
                      profile_pic_url=user_data["profile_pic_url"],
                      is_private=user_data["is_private"],
                      is_verified=user_data["is_verified"],
                      follower_count=user_data["edge_followed_by"]["count"],
                      following_count=user_data["edge_follow"]["count"],
                      following_tag_count=following_hashtags_number,
                      post_count=user_data["edge_owner_to_timeline_media"]["count"],
                      biography=user_data["biography"])
    return result.model_dump(mode="json")


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
    time.sleep(random.randint(4, 6))

    json_requests = filter_requests(driver.requests, JsonResponseContentType.text_javascript)
    del driver.requests
    # get first 12 documents
    target_url = f"{INSTAGRAM_DOMAIN}/api/graphql"
    idx = search_request(json_requests, target_url,
                         JsonResponseContentType.text_javascript,
                         check_request_data, username)
    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]
    results.append(json_data)
    remaining -= len(json_data["edges"])

    while results[-1]['page_info']["has_next_page"] and remaining > 0:
        footer = driver.find_element(By.XPATH, "//footer")
        driver.execute_script("return arguments[0].scrollIntoView(true);", footer)

        time.sleep(random.randint(4, 6))
        json_requests += filter_requests(driver.requests, JsonResponseContentType.text_javascript)
        del driver.requests

        idx = search_request(json_requests, target_url, JsonResponseContentType.text_javascript,
                             check_request_data, username, after=results[-1]['page_info']["end_cursor"])
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


@driver_implicit_wait(10)
def collect_reels_of_user(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                          username: str,
                          n: int = 100) -> Json:
    """Collect n reels of the given user. If n is set to 0, collect all reels.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of reels, which should be collected. By default,
         it's 100. If it's set to 0, collect all posts.

    Returns:
        Json: all visible reels user information of the given user in json format.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_reels_of_user
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_reels_of_user(driver, "dummy_instagram_username", 100)
        {
          "reels": [
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
    def check_request_data(request, user_id, after=""):
        request_data = parse_qs(request.body.decode())
        variables = json.loads(request_data.get("variables", ["{}"])[0])
        if request_data.get("av", [''])[0] != "17841461911219001":
            return False
        elif not variables:
            return False
        elif variables.get("data", dict()).get("target_user_id", "") != user_id:
            return False
        elif variables.get("after", "") != after:
            return False
        return True

    if n <= 0:
        raise ValueError("The number of reels to collect must be a positive integer.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/reels/')
    time.sleep(random.randint(4, 6))

    # get user id
    json_requests = filter_requests(driver.requests)
    user_data = get_user_data(json_requests, username)
    user_id = extract_id(user_data)

    json_requests = filter_requests(driver.requests, JsonResponseContentType.text_javascript)
    del driver.requests

    # get first 12 documents
    target_url = f"{INSTAGRAM_DOMAIN}/api/graphql"
    idx = search_request(json_requests, target_url, JsonResponseContentType.text_javascript,
                         check_request_data, user_id)
    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)["data"]["xdt_api__v1__clips__user__connection_v2"]
    results.append(json_data)
    remaining -= len(json_data["edges"])

    while results[-1]['page_info']["has_next_page"] and remaining > 0:
        footer = driver.find_element(By.XPATH, "//footer")
        driver.execute_script("return arguments[0].scrollIntoView(true);", footer)

        time.sleep(random.randint(4, 6))
        json_requests += filter_requests(driver.requests, JsonResponseContentType.text_javascript)
        del driver.requests

        idx = search_request(json_requests, target_url, JsonResponseContentType.text_javascript,
                             check_request_data, user_id, results[-1]['page_info']["end_cursor"])
        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)["data"]["xdt_api__v1__clips__user__connection_v2"]
        results.append(json_data)
        remaining -= len(json_data["edges"])

    posts = []
    for result in results:
        for item in result['edges']:
            post = extract_post(item['node']["media"])
            posts.append(post)
    posts = posts[:n]
    return Posts(posts=posts, count=len(posts)).model_dump(mode="json")


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
    def check_request_data(request, user_id, after=""):
        request_data = parse_qs(request.body.decode())
        variables = json.loads(request_data.get("variables", ["{}"])[0])
        if request_data.get("av", [''])[0] != "17841461911219001":
            return False
        elif not variables:
            return False
        elif variables.get("user_id", "") != user_id:
            return False
        elif variables.get("after", "") != after:
            return False
        return True

    if n <= 0:
        raise ValueError("The number of tagged posts to collect must be a positive integer.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/tagged/')
    time.sleep(random.randint(4, 6))

    # get user id
    json_requests = filter_requests(driver.requests)
    user_data = get_user_data(json_requests, username)
    user_id = extract_id(user_data)

    json_requests = filter_requests(driver.requests, JsonResponseContentType.text_javascript)
    del driver.requests

    # get first 12 documents
    target_url = f"{INSTAGRAM_DOMAIN}/api/graphql"
    idx = search_request(json_requests, target_url, JsonResponseContentType.text_javascript,
                         check_request_data, user_id)
    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)["data"]["xdt_api__v1__usertags__user_id__feed_connection"]
    results.append(json_data)
    remaining -= len(json_data["edges"])

    while results[-1]['page_info']["has_next_page"] and remaining > 0:
        footer = driver.find_element(By.XPATH, "//footer")
        driver.execute_script("return arguments[0].scrollIntoView(true);", footer)

        time.sleep(random.randint(4, 6))
        json_requests += filter_requests(driver.requests, JsonResponseContentType.text_javascript)
        del driver.requests

        idx = search_request(json_requests, target_url, JsonResponseContentType.text_javascript,
                             check_request_data, user_id, results[-1]['page_info']["end_cursor"])
        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)["data"]["xdt_api__v1__usertags__user_id__feed_connection"]
        results.append(json_data)
        remaining -= len(json_data["edges"])

    posts = []
    for result in results:
        for item in result['edges']:
            post = extract_post(item['node'])
            posts.append(post)
    posts = posts[:n]
    return Posts(posts=posts, count=len(posts)).model_dump(mode="json")


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
          "followed_by": true,
          "blocking": null,
          "muting": null,
          "is_private": false,
          "incoming_request": null,
          "outgoing_request": null,
          "is_blocking_reel": null,
          "is_muting_reel": null,
          "is_bestie": null,
          "is_restricted": null,
          "is_feed_favorite": null,
          "subscribed": null,
          "is_eligible_to_subscribe": null
        }
    """
    following, followed_by = False, False
    for username in [username1, username2]:
        driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
        time.sleep(random.randint(4, 6))

        json_requests = filter_requests(driver.requests)
        del driver.requests

        # get user data
        user_data = get_user_data(json_requests, username)
        user_id = extract_id(user_data)

        following_btn = driver.find_element(By.XPATH, f"//a[@href='/{username}/following/'][@role='link']")
        following_btn.click()
        time.sleep(random.randint(4, 6))
        del driver.requests

        searching_username = username2 if username == username1 else username1

        search_input_box = driver.find_element(By.XPATH,
                                               '//input[@aria-label="Search input"][@placeholder="Search"][@type="text"]')
        search_input_box.send_keys(searching_username)
        time.sleep(random.randint(6, 8))

        json_requests = filter_requests(driver.requests)
        del driver.requests

        # get first 12 followings
        query_dict = dict(query=searching_username)
        target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_id}/following/?{urlencode(query_dict, quote_via=quote)}"
        idx = search_request(json_requests, target_url)
        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)

        for user_info in json_data["users"]:
            if user_info["username"] not in {username1, username2}:
                continue
            elif user_info["username"] == username1:
                following = True
            else:
                followed_by = True
            break

    return FriendshipStatus(following=following, followed_by=followed_by).model_dump(mode="json")


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
    if n <= 0:
        raise ValueError("The number of followers to collect must be a positive integer.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.randint(4, 6))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    # get user data
    user_data = get_user_data(json_requests, username)
    user_id = extract_id(user_data)

    followers_btn = driver.find_element(By.XPATH, f"//a[@href='/{username}/followers/'][@role='link']")
    followers_btn.click()
    time.sleep(random.randint(4, 6))

    json_requests += filter_requests(driver.requests)
    del driver.requests

    # get 50 followers
    query_dict = dict(count=12, search_surface="follow_list_page")
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_id}/followers/?{urlencode(query_dict, quote_via=quote)}"
    idx = search_request(json_requests, target_url)
    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)
    results.append(json_data)
    remaining -= len(json_data["users"])

    while 'next_max_id' in results[-1] and remaining > 0:
        followers_bottom = driver.find_element(By.XPATH, "//div[@class='_aano']//div[@role='progressbar']")
        driver.execute_script("return arguments[0].scrollIntoView(true);", followers_bottom)

        time.sleep(random.randint(4, 6))

        json_requests += filter_requests(driver.requests)
        del driver.requests

        query_dict = dict(count=12, max_id=results[-1]['next_max_id'], search_surface="follow_list_page")
        target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_id}/followers/?{urlencode(query_dict, quote_via=quote)}"
        idx = search_request(json_requests, target_url)
        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)
        results.append(json_data)
        remaining -= len(json_data["users"])

    users = []
    for json_data in results:
        for user_info in json_data["users"]:
            user = UserProfile(id=user_info["pk"],
                               username=user_info["username"],
                               fullname=user_info["full_name"],
                               profile_pic_url=user_info["profile_pic_url"],
                               is_private=user_info["is_private"],
                               is_verified=user_info["is_verified"])
            users.append(user)
    users = users[:n]
    return Users(users=users, count=len(users)).model_dump(mode="json")


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
    if n <= 0:
        raise ValueError("The number of following users to collect must be a positive integer.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.randint(4, 6))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    # get user data
    user_data = get_user_data(json_requests, username)
    user_id = extract_id(user_data)

    following_btn = driver.find_element(By.XPATH, f"//a[@href='/{username}/following/'][@role='link']")
    following_btn.click()
    time.sleep(random.randint(4, 6))

    json_requests += filter_requests(driver.requests)
    del driver.requests

    # get first 12 followings
    query_dict = dict(count=12)
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_id}/following/?{urlencode(query_dict, quote_via=quote)}"
    idx = search_request(json_requests, target_url)
    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)
    results.append(json_data)
    remaining -= len(json_data["users"])

    while 'next_max_id' in results[-1] and remaining > 0:
        following_bottom = driver.find_element(By.XPATH, "//div[@class='_aano']//div[@role='progressbar']")
        driver.execute_script("return arguments[0].scrollIntoView(true);", following_bottom)

        time.sleep(random.randint(4, 6))

        json_requests += filter_requests(driver.requests)
        del driver.requests

        query_dict = dict(count=12, max_id=results[-1]['next_max_id'])
        target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_id}/following/?{urlencode(query_dict, quote_via=quote)}"
        idx = search_request(json_requests, target_url)
        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)
        results.append(json_data)
        remaining -= len(json_data["users"])

    users = []
    for json_data in results:
        for user_info in json_data["users"]:
            user = UserProfile(id=user_info["pk"],
                               username=user_info["username"],
                               fullname=user_info["full_name"],
                               profile_pic_url=user_info["profile_pic_url"],
                               is_private=user_info["is_private"],
                               is_verified=user_info["is_verified"])
            users.append(user)
    users = users[:n]
    return Users(users=users, count=len(users)).model_dump(mode="json")


@driver_implicit_wait(10)
def collect_following_hashtags_of_user(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                                       username: str,
                                       n: int = 100) -> Json:
    """Collect n followings hashtags of the given user.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of followings, which should be collected.
         By default, it's 100. If it's set to 0, collect all followings.

    Returns:
        Json: all visible followings hashtags' information of the given user in
        json format.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_following_hashtags_of_user
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_following_hashtags_of_user(driver, "instagram_username", 100)
        {
          "hashtags": [
            {
              "id": "528817151",
              "name": "asiangames",
              "post_count": 1000000,
              "profile_pic_url": "https://dummy.pic.com",
            },
            ...
            ],
          "count": 100
        }
    """
    if n <= 0:
        raise ValueError("The number of following hashtags to collect must be a positive integer.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.randint(4, 6))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    user_data = get_user_data(json_requests, username)
    user_id = extract_id(user_data)

    following_btn_xpath = f"//a[@href='/{username}/following/'][@role='link']"
    following_btn = driver.find_element(By.XPATH, following_btn_xpath)
    following_btn.click()

    time.sleep(random.randint(3, 5))

    hashtag_btn = driver.find_element(By.XPATH, "//span[text()='Hashtags']")
    hashtag_btn.click()
    time.sleep(random.randint(4, 6))

    json_requests += filter_requests(driver.requests)
    del driver.requests

    # get first 12 followings
    variables = dict(id=user_id)
    query_dict = dict(doc_id=FOLLOWING_DOC_ID, variables=json.dumps(variables, separators=(',', ':')))
    target_url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?{urlencode(query_dict, quote_via=quote)}"
    idx = search_request(json_requests, target_url)
    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)
    results.append(json_data)
    remaining -= len(json_data["data"]['user']['edge_following_hashtag']['edges'])

    hashtags = []
    for json_data in results:
        for item in json_data["data"]['user']['edge_following_hashtag']['edges']:
            hashtag = HashtagBasicInfo(id=extract_id(item["node"]),
                                       name=item["node"]["name"],
                                       post_count=item["node"]["media_count"],
                                       profile_pic_url=item["node"]["profile_pic_url"])
            hashtags.append(hashtag)
    hashtags = hashtags[:n]
    return HashtagBasicInfos(hashtags=hashtags, count=len(hashtags)).model_dump(mode="json")


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
          "likers": [
            {
              "id": "528817151",
              "username": "nasa",
              "fullname": "NASA",
              "is_private": false,
              "is_verified": true,
              "profile_pic_url": "https://dummy.pic.com",
              "friendship_status": {
                "following": false,
                "followed_by": true,
                "blocking": null,
                "muting": null,
                "is_private": false,
                "incoming_request": null,
                "outgoing_request": null,
                "is_blocking_reel": null,
                "is_muting_reel": null,
                "is_bestie": null,
                "is_restricted": null,
                "is_feed_favorite": null,
                "subscribed": null,
                "is_eligible_to_subscribe": null
              }
            },
            ...
            ],
          "count": 100
        }
    """
    if n <= 0:
        raise ValueError("The number of likers to collect must be a positive integer.")

    results = []

    driver.get(f"{INSTAGRAM_DOMAIN}/p/{post_code}/")
    time.sleep(random.randint(4, 6))
    del driver.requests

    # get the media id for later requests filtering
    meta_tag_xpath = "//meta[@property='al:ios:url']"
    meta_tag = driver.find_element(By.XPATH, meta_tag_xpath)
    post_id = re.findall("\d+", meta_tag.get_attribute("content"))
    if not post_id:
        return Likers(likers=[], count=0).model_dump(mode="json")
    post_id = post_id[0]

    likes_btn_xpath = f"//a[@href='/p/{post_code}/liked_by/'][@role='link']"
    likes_btn = driver.find_element(By.XPATH, likes_btn_xpath)
    likes_btn.click()
    time.sleep(random.randint(3, 5))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    # get 50 likers
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/media/{post_id}/likers/"
    idx = search_request(json_requests, target_url)
    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)
    results.append(json_data)

    likers = []
    for json_data in results:
        for liker_info in json_data["users"]:
            friendship_status = FriendshipStatus(following=liker_info["friendship_status"]["following"],
                                                 followed_by=liker_info["friendship_status"]["followed_by"],
                                                 blocking=liker_info["friendship_status"]["blocking"],
                                                 muting=liker_info["friendship_status"]["muting"],
                                                 is_private=liker_info["friendship_status"]["is_private"],
                                                 incoming_request=liker_info["friendship_status"]["incoming_request"],
                                                 outgoing_request=liker_info["friendship_status"]["outgoing_request"],
                                                 is_blocking_reel=liker_info["friendship_status"]["is_blocking_reel"],
                                                 is_muting_reel=liker_info["friendship_status"]["is_muting_reel"],
                                                 is_bestie=liker_info["friendship_status"]["is_bestie"],
                                                 is_restricted=liker_info["friendship_status"]["is_restricted"],
                                                 is_feed_favorite=liker_info["friendship_status"]["is_feed_favorite"],
                                                 subscribed=liker_info["friendship_status"]["subscribed"],
                                                 is_eligible_to_subscribe=liker_info["friendship_status"][
                                                     "is_eligible_to_subscribe"])
            liker = Liker(id=liker_info["pk"],
                          username=liker_info["username"],
                          fullname=liker_info["full_name"],
                          profile_pic_url=liker_info["profile_pic_url"],
                          is_private=liker_info["is_private"],
                          is_verified=liker_info["is_verified"],
                          friendship_status=friendship_status)
            likers.append(liker)
    likers = likers[:n]
    return Likers(likers=likers, count=len(likers)).model_dump(mode="json")


@driver_implicit_wait(10)
def collect_comments_of_post(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                             post_code: str,
                             n: int = 100) -> Json:
    """Collect n comments of a given post.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        post_code (str): code of the post, whose comments will be collected.
        n (int): maximum number of comments, which should be collected. By default,
         it's 100. If it's set to 0, collect all comments.

    Returns:
        Json: all comments of the given post in json format.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import collect_comments_of_post
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> collect_comments_of_post(driver, "WGDBS3D", 100)
        {
          "comments": [
            {
              "id": "18278957755095859",
              "user": {
                "id": "6293392719",
                "username": "dummy_user"
              },
              "post_id": "3275298868401088037",
              "created_at_utc": 1704669275,
              "status": null,
              "share_enabled": null,
              "is_ranked_comment": null,
              "text": "Fantastic Job",
              "has_translation": false,
              "is_liked_by_post_owner": null,
              "comment_like_count": 0
            },
            ...
            ],
          "count": 100
        }
    """
    def check_request_data(request, post_id):
        request_data = parse_qs(request.body.decode())
        variables = json.loads(request_data.get("variables", ["{}"])[0])
        if request_data.get("av", [''])[0] != "17841461911219001":
            return False
        elif not variables:
            return False
        elif variables.get("media_id", "") != post_id:
            return False
        return True

    def find_cached_data():
        scripts = driver.find_elements(By.XPATH, '//script[@type="application/json"]')
        script_data = None
        for script in scripts:
            if "xdt_api__v1__media__media_id__comments__connection" not in script.get_attribute("innerHTML"):
                continue
            script_data = script
            break

        if not script_data:
            return []

        data_str = script_data.get_attribute("innerHTML")
        start_idx = data_str.find("xdt_api__v1__media__media_id__comments__connection") + len("xdt_api__v1__media__media_id__comments__connection")
        data_str = data_str[start_idx:]
        start, stop = find_brackets(data_str)[-1]
        json_data = json.loads(data_str[start:stop+1])
        return json_data

    if n <= 0:
        raise ValueError("The number of comments to collect must be a positive integer.")

    results = []
    remaining = n

    driver.get(f"{INSTAGRAM_DOMAIN}/p/{post_code}/")
    time.sleep(random.randint(4, 6))

    # get the media id for later requests filtering
    meta_tag_xpath = "//meta[@property='al:ios:url']"
    meta_tag = driver.find_element(By.XPATH, meta_tag_xpath)
    post_id = re.findall("\d+", meta_tag.get_attribute("content"))
    if not post_id:
        return Comments(comments=[], count=0).model_dump(mode="json")
    post_id = post_id[0]

    json_requests = []
    target_url = f"{INSTAGRAM_DOMAIN}/api/graphql"
    cached_data = find_cached_data()

    if cached_data:
        results.append(cached_data)
        remaining -= len(cached_data["edges"])
    else:
        json_requests = filter_requests(driver.requests, JsonResponseContentType.text_javascript)
        del driver.requests

        idx = search_request(json_requests, target_url, JsonResponseContentType.text_javascript, check_request_data, post_id)
        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)["data"]["xdt_api__v1__media__media_id__comments__connection"]
        results.append(json_data)
        remaining -= len(json_data["edges"])

    while results[-1]["page_info"]['has_next_page'] and remaining > 0:
        comment_lists = driver.find_elements(By.XPATH, '//div[@class="x78zum5 xdt5ytf x1iyjqo2"]/div[@class="x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 x5pf9jr xo71vjh x1uhb9sk x1plvlek xryxfnj x1c4vz4f x2lah0s xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh x1nhvcw1"]')
        driver.execute_script("return arguments[0].scrollIntoView(true);", comment_lists[-1])

        time.sleep(random.randint(4, 6))
        json_requests += filter_requests(driver.requests, JsonResponseContentType.text_javascript)
        del driver.requests

        idx = search_request(json_requests, target_url, JsonResponseContentType.text_javascript,
                             check_request_data, post_id)
        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)["data"]["xdt_api__v1__media__media_id__comments__connection"]
        results.append(json_data)
        remaining -= len(json_data["edges"])

    comments = []
    for json_data in results:
        for item in json_data["edges"]:
            comment_dict = item["node"]
            default_created_at_timestamp = comment_dict.get("created_at", 0)
            comment = Comment(id=extract_id(comment_dict),
                              user=UserBasicInfo(id=extract_id(comment_dict["user"]),
                                                 username=comment_dict["user"]["username"]),
                              post_id=post_id,
                              created_at_utc=comment_dict.get("created_at_utc", default_created_at_timestamp),
                              status=comment_dict.get("status"),
                              share_enabled=comment_dict.get("share_enabled"),
                              is_ranked_comment=comment_dict.get("is_ranked_comment"),
                              text=comment_dict["text"],
                              has_translation=comment_dict.get("has_translation", False),
                              is_liked_by_posst_owner=comment_dict.get("has_liked_comment", False),
                              comment_like_count=comment_dict.get("comment_like_count", 0))
            comments.append(comment)

    return Comments(comments=comments, count=len(comments)).model_dump(mode="json")


@driver_implicit_wait(10)
def search_with_keyword(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                        keyword: str,
                        pers: bool) -> Json:
    """Search hashtags or users with given keyword.

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        keyword (str): keyword for searching.
        pers (bool): indicating whether results should be personalized or not.

    Returns:
        Json: found users/hashtags.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import search_with_keyword
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> search_with_keyword(driver, "shanghai", True)
        {
          "hashtags": [
            {
              "position": 1,
              "hashtag": {
                "id": "17841563224118980",
                "name": "shanghai",
                "post_count": 11302316,
                "profile_pic_url": ""
              }
            }
          ],
          "users": [
            {
              "position": 0,
              "user": {
                "id": "7594441262",
                "username": "shanghai.explore",
                "fullname": "Shanghai 🇨🇳 Travel | Hotels | Food | Tips",
                "profile_pic_url": "https://scontent.cdninstagram.com/v/t51.2885-19/409741157_243678455262812_2168807265478461941_n.jpg?stp=dst-jpg_s150x150&_nc_ht=scontent.cdninstagram.com&_nc_cat=108&_nc_ohc=S3SAe59tdbUAX9SLkyd&edm=APs17CUBAAAA&ccb=7-5&oh=00_AfALvv52ytTyye_PDEjKCmWAUetHX8BXCGsS7rnFThzNTQ&oe=65ECAABE&_nc_sid=10d13b",
                "is_private": null,
                "is_verified": true
              }
            }
          ],
          "places": [
            {
              "position": 2,
              "place": {
                "location": {
                  "id": "106324046073002",
                  "name": "Shanghai, China"
                },
                "subtitle": "",
                "title": "Shanghai, China"
              }
            }
          ],
          "personalised": true
        }
    """

    def check_request_data(request, keyword, pers):
        request_data = parse_qs(request.body.decode())
        variables = json.loads(request_data.get("variables", ["{}"])[0])
        if not variables:
            return False
        elif pers and variables.get("data", dict(query=""))["query"] != keyword:
            return False
        elif not pers and variables.get("query") != keyword:
            return False
        return True

    driver.get(f'{INSTAGRAM_DOMAIN}')
    time.sleep(random.randint(4, 6))

    search_btn = driver.find_element(By.XPATH, '//a[@href="#"][@role="link"]')
    search_btn.click()
    time.sleep(random.randint(4, 6))

    del driver.requests

    search_input_box = driver.find_element(By.XPATH, '//input[@aria-label="Search input"][@placeholder="Search"][@type="text"]')
    search_input_box.send_keys(keyword)
    time.sleep(random.randint(6, 8))

    if not pers:
        del driver.requests
        not_pers_btn = driver.find_element(By.XPATH, '//div[@aria-label="Not personalised"][@role="button"][@tabindex="0"]//span[text()="Not personalised"]')
        not_pers_btn.click()
        time.sleep(random.randint(6, 8))

    json_requests = filter_requests(driver.requests, response_content_type=JsonResponseContentType.text_javascript)
    del driver.requests

    target_url = f"{INSTAGRAM_DOMAIN}/api/graphql"
    idx = search_request(json_requests, target_url, JsonResponseContentType.text_javascript,
                         check_request_data, keyword, pers)
    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)
    data_key = "xdt_api__v1__fbsearch__topsearch_connection" if pers else "xdt_api__v1__fbsearch__non_profiled_serp"
    json_data = json_data["data"][data_key]

    hashtags = []
    places = []
    if pers:
        for hashtag_info in json_data.get("hashtags", []):
            hashtag = SearchingResultHashtag(position=hashtag_info["position"],
                                             hashtag=HashtagBasicInfo(id=extract_id(hashtag_info["hashtag"]),
                                                                      name=hashtag_info["hashtag"]["name"],
                                                                      post_count=hashtag_info["hashtag"]["media_count"]))
            hashtags.append(hashtag)

        for place_info in json_data.get("places", []):
            place = SearchingResultPlace(position=place_info["position"],
                                         place=Place(
                                             location=LocationBasicInfo(id=place_info["place"]["location"]["pk"],
                                                                        name=place_info["place"]["location"]["name"]),
                                             subtitle=place_info["place"]["subtitle"],
                                             title=place_info["place"]["title"]))
            places.append(place)

    users = []
    for i, user_info in enumerate(json_data.get("users", [])):
        if pers:
            position = user_info["position"]
            user_info_dict = user_info["user"]
        else:
            position = i
            user_info_dict = user_info

        user = SearchingResultUser(position=position,
                                   user=UserProfile(id=extract_id(user_info_dict),
                                                    username=user_info_dict["username"],
                                                    fullname=user_info_dict["full_name"],
                                                    profile_pic_url=user_info_dict["profile_pic_url"],
                                                    is_verified=user_info_dict["is_verified"]))
        users.append(user)

    searching_result = SearchingResult(hashtags=hashtags,
                                       users=users,
                                       places=places,
                                       personalised=pers)
    return searching_result.model_dump(mode="json")


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
    time.sleep(random.randint(4, 6))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    target_url = f'{INSTAGRAM_DOMAIN}/{API_VERSION}/tags/web_info/?tag_name={hashtag}'
    idx = search_request(json_requests, target_url)
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
    time.sleep(random.randint(4, 6))

    json_requests = filter_requests(driver.requests)
    del driver.requests
    # get first 12 documents
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/clips/music/"
    idx = search_request(json_requests, target_url, JsonResponseContentType.application_json,
                         check_request_data, music_id)
    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)
    results.append(json_data)
    remaining -= len(json_data["items"])

    while results[-1]["paging_info"]['more_available'] and remaining > 0:
        footer = driver.find_element(By.XPATH, "//footer")
        driver.execute_script("return arguments[0].scrollIntoView(true);", footer)

        time.sleep(random.randint(4, 6))
        json_requests += filter_requests(driver.requests)
        del driver.requests

        idx = search_request(json_requests, target_url, JsonResponseContentType.application_json,
                             check_request_data, music_id, results[-1]["paging_info"]['max_id'])
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


@driver_implicit_wait(10)
def download_media(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                   media_url: str,
                   file_name: str) -> None:
    """Download the image/video based on the given media_url, and store it to
    the given path.

    Normally, the media_url is valid for 1 week (max. 3 weeks).

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        media_url (str): url of the media for downloading.
        file_name (str): path for storing the downloaded media.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import download_media
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> download_media(driver, "https://scontent-muc2-1.xx.fbcdn.net/v/t39.12897-6/419784899_922911948795613_3855576336552877996_n.m4a", "tmp")
    """
    driver.get(media_url)
    time.sleep(random.randint(4, 6))

    idx = search_request(driver.requests, media_url, response_content_type=None)
    request = driver.requests.pop(idx)
    file_extension = request.response.headers["Content-Type"].split("/")[1]
    with open(f"{file_name}.{file_extension}", "wb") as f:
        f.write(request.response.body)
        f.close()
