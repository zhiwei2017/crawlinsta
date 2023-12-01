import random
import time
from urllib.parse import parse_qs
from pydantic import Json
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from .schemas import (
    UserBasicInfo, UserInfo, Users, Likers, Comments, Usertag, Location,
    Caption, Post, Posts, HashtagBasicInfo, HashtagBasicInfos, Hashtag,
    SearchingResult, FriendshipStatus
)
from .utils import filter_request, get_json_data, get_media_type
from .decorators import driver_implicit_wait

INSTAGRAM_DOMAIN = "https://www.instagram.com"
GRAPHQL_QUERY_PATH = "graphql/query"
API_VERSION = "api/v1"
FOLLOWING_DOC_ID = "17901966028246171"


@driver_implicit_wait(10)
def collect_user_info(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                      username: str) -> Json:
    """Collect user information through username, including user_id, username,
    profile_pic_url, biography, post_count, follower_count, following_count.

    Strategy: click the username, get to the main page of the user, the user
    information is returned in the response body.

    Alternatively, put the mouse over the user's name in home page, the user
    information will show in a popup. A request triggered by the mouseover was
    sent to the path `/api/v1/users/<user_id>/info/` or
    `/api/v1/users/web_profile_info/?username=<user_name>`

    Args:
        driver (:obj:`selenium.webdriver.remote.webdriver.WebDriver`): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.

    Returns:
        Json: user information in json format.

    Examples:
        >>> from crawlinsta import webdriver
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> from crawlinsta.login import login
        >>> login(driver, "your_username", "your_password")
        >>> collect_user_info(driver, "instagram_username")
    """
    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.randint(4, 6))
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={username}"
    request = filter_request(driver.requests, target_url)
    if not request:
        raise ValueError(f"No json response to the url '{target_url}' found.")
    json_data = get_json_data(request.response)
    user_data = json_data["data"]['user']
    del driver.requests

    following_btn_xpath = f"//a[@href='/{username}/following/'][@role='link']"
    following_btn = driver.find_element(By.XPATH, following_btn_xpath)
    following_btn.click()

    time.sleep(random.randint(3, 5))

    hashtag_btn = driver.find_element(By.XPATH, "//span[text()='Hashtags']")
    hashtag_btn.click()
    time.sleep(random.randint(4, 6))

    target_url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?doc_id={FOLLOWING_DOC_ID}&variables=%7B%22id%22%3A%22{user_data['id']}%22%7D"
    request = filter_request(driver.requests, target_url)
    if not request:
        raise ValueError(f"No json response to the url '{target_url}' found.")
    json_data = get_json_data(request.response)
    following_hashtags_number = json_data["data"]['user']['edge_following_hashtag']['count']
    del driver.requests

    result = UserInfo(id=user_data["id"],
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
    """Collect n posts of the given user.

    Strategy: click the username, get to the main page of the user, a few posts
    are displayed in the user's main page. The request was sent to the path
    `/api/v1/feed/user/<user_name>/username/?count=6` to get the posts and a
    next_max_id for loading other posts. To load the other posts, move the mouse
    to the bottom of the page, it will trigger another request sent to
    `/api/v1/feed/user/<user_id>/?count=12&max_id=<next_max_id>`
    to have more posts.

    Args:
        driver (:obj:`selenium.webdriver.remote.webdriver.WebDriver`): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of posts, which should be collected. By default,
         it's 100. If it's set to 0, collect all posts.

    Returns:
        Json: all visible post of the given user in json format.

    Examples:
        >>> from crawlinsta import webdriver
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> from crawlinsta.login import login
        >>> login(driver, "your_username", "your_password")
        >>> collect_posts_of_user(driver, "instagram_username")
    """
    if n < 0:
        raise ValueError("Parameter 'n' must be bigger than or equal to 0.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.randint(4, 6))

    # get first 12 documents
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/feed/user/{username}/username/?count=12"
    request = filter_request(driver.requests, target_url)
    if not request:
        raise ValueError(f"No json response to the url '{target_url}' found.")
    json_data = get_json_data(request.response)
    results.append(json_data)
    remaining -= 12
    del driver.requests

    while results[-1]['more_available']:
        if n > 0 >= remaining:
            break
        footer = driver.find_element(By.XPATH, "//footer")
        ActionChains(driver).scroll_to_element(footer).perform()

        time.sleep(random.randint(4, 6))
        target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/feed/user/{results[-1]['user']['pk']}/?count=12&max_id={results[-1]['next_max_id']}"
        request = filter_request(driver.requests, target_url)
        if not request:
            raise ValueError(f"No json response to the url '{target_url}' found.")
        json_data = get_json_data(request.response)
        results.append(json_data)
        remaining -= 12
        del driver.requests

    posts = []
    for result in results:
        for item in result['items']:
            usertags = []
            for usertag_info in item.get("usertags", {"in": []})["in"]:
                tagged_user = UserBasicInfo(id=usertag_info["user"]["pk"],
                                            username=usertag_info["user"]["username"],
                                            fullname=usertag_info["user"]["full_name"],
                                            profile_pic_url=usertag_info["user"]["profile_pic_url"],
                                            is_private=usertag_info["user"]["is_private"],
                                            is_verified=usertag_info["user"]["is_verified"])
                usertag = Usertag(user=tagged_user,
                                  position=usertag_info["position"],
                                  start_time_in_video_in_sec=usertag_info["start_time_in_video_in_sec"],
                                  duration_in_video_in_sec=usertag_info["duration_in_video_in_sec"])
                usertags.append(usertag)
            location = item.get("location", None)
            if location:
                location = Location(id=location["pk"],
                                    short_name=location["short_name"],
                                    name=location["name"],
                                    city=location.get("city", ""),
                                    lng=location.get("lng", 0),
                                    lat=location.get("lat", 0),
                                    address=location.get("address", ""))
            caption = Caption(id=item["caption"]["pk"],
                              text=item["caption"]["text"],
                              created_at_utc=item["caption"]["created_at_utc"])

            user = UserBasicInfo(id=item["user"]["id"],
                                 username=item["user"]["username"],
                                 fullname=item["user"]["full_name"],
                                 profile_pic_url=item["user"]["profile_pic_url"],
                                 is_private=item["user"]["is_private"],
                                 is_verified=item["user"]["is_verified"])

            post = Post(id=item['pk'],
                        code=item['code'],
                        user=user,
                        taken_at=item['taken_at'],
                        has_shared_to_fb=bool(item['has_shared_to_fb']),
                        usertags=usertags,
                        media_type=get_media_type(item['media_type'], item['product_type']),
                        caption=caption,
                        accessibility_caption=item.get("accessibility_caption", caption.text),
                        location=location,
                        original_width=item['original_width'],
                        original_height=item['original_height'],
                        url=item["image_versions2"]['candidates'][0]["url"],
                        like_count=item['like_count'],
                        comment_count=item['comment_count'])
            posts.append(post)
    return Posts(posts=posts[:n]).model_dump(mode="json")


@driver_implicit_wait(10)
def collect_reels_of_user(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                          username: str,
                          n: int = 100) -> Json:
    """Collect n reels of the given user.

    Strategy: click the username, get to the main page of the user, a few posts
    are displayed in the user's main page. Click the button reels to see all the
    reels from the user.The request was sent to the path
    `/api/v1/feed/user/<user_name>/username/?count=6` to get the posts/reels and a
    next_max_id for loading other posts/reels. To load the other posts/reels,
    move the mouse to the bottom of the page, it will trigger another request sent to
    `/api/v1/feed/user/<user_id>/?count=12&max_id=<next_max_id>`
    to have more posts/reels.

    Args:
        driver (:obj:`selenium.webdriver.remote.webdriver.WebDriver`): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of reels, which should be collected. By default,
         it's 100. If it's set to 0, collect all posts.

    Returns:
        Json: all visible reels user information of the given user in json format.

    Examples:
        >>> from crawlinsta import webdriver
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> from crawlinsta.login import login
        >>> login(driver, "your_username", "your_password")
        >>> collect_reels_of_user(driver, "instagram_username")
    """
    if n < 0:
        raise ValueError("Parameter 'n' must be bigger than or equal to 0.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.randint(4, 6))

    reels_btn = driver.find_element(By.XPATH, f"//a[@href='/{username}/reels/'][@role='tab']")
    reels_btn.click()
    time.sleep(random.randint(4, 6))

    # get first 12 documents
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/clips/user/"
    request = filter_request(driver.requests, target_url)
    if not request:
        raise ValueError(f"No json response to the url '{target_url}' found.")
    json_data = get_json_data(request.response)
    results.append(json_data)
    page_size = int(parse_qs(request.body.decode('utf-8'))["page_size"][0])
    remaining -= page_size
    del driver.requests

    while results[-1]['paging_info']['more_available']:
        if n > 0 >= remaining:
            break

        footer = driver.find_element(By.XPATH, "//footer")
        ActionChains(driver).scroll_to_element(footer).perform()

        time.sleep(random.randint(4, 6))
        request = filter_request(driver.requests, target_url)
        if not request:
            raise ValueError(f"No json response to the url '{target_url}' found.")
        json_data = get_json_data(request.response)
        results.append(json_data)
        page_size = int(parse_qs(request.body.decode('utf-8'))["page_size"][0])
        remaining -= page_size
        del driver.requests

    posts = []
    for result in results:
        for item in result['items']:
            item = item['media']
            usertags = []
            for usertag_info in item.get("usertags", {"in": []})["in"]:
                tagged_user = UserBasicInfo(id=usertag_info["user"]["pk"],
                                            username=usertag_info["user"]["username"],
                                            fullname=usertag_info["user"]["full_name"],
                                            profile_pic_url=usertag_info["user"]["profile_pic_url"],
                                            is_private=usertag_info["user"]["is_private"],
                                            is_verified=usertag_info["user"]["is_verified"])
                usertag = Usertag(user=tagged_user,
                                  position=usertag_info["position"],
                                  start_time_in_video_in_sec=usertag_info["start_time_in_video_in_sec"],
                                  duration_in_video_in_sec=usertag_info["duration_in_video_in_sec"])
                usertags.append(usertag)
            location = item.get("location", None)
            if location:
                location = Location(id=location["pk"],
                                    short_name=location["short_name"],
                                    name=location["name"],
                                    city=location.get("city", ""),
                                    lng=location.get("lng", 0),
                                    lat=location.get("lat", 0),
                                    address=location.get("address", ""))
            caption = item.get("caption", None)
            default_accessibility_caption = ""
            if caption:
                caption = Caption(id=item["caption"]["pk"],
                                  text=item["caption"]["text"],
                                  created_at_utc=item["caption"]["created_at_utc"])
                default_accessibility_caption = caption.text

            user = UserBasicInfo(id=item["user"]["id"],
                                 username=item["user"]["username"],
                                 fullname=item["user"]["full_name"],
                                 profile_pic_url=item["user"]["profile_pic_url"],
                                 is_private=item["user"]["is_private"],
                                 is_verified=item["user"]["is_verified"])

            post = Post(id=item['pk'],
                        code=item['code'],
                        user=user,
                        taken_at=item['taken_at'],
                        has_shared_to_fb=bool(item['has_shared_to_fb']),
                        usertags=usertags,
                        media_type=get_media_type(item['media_type'], item['product_type']),
                        caption=caption,
                        accessibility_caption=item.get("accessibility_caption", default_accessibility_caption),
                        location=location,
                        original_width=item['original_width'],
                        original_height=item['original_height'],
                        url=item["image_versions2"]['candidates'][0]["url"],
                        like_count=item['like_count'],
                        comment_count=item['comment_count'])
            posts.append(post)
    return Posts(posts=posts[:n]).model_dump(mode="json")


def collect_user_tagged_posts(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                              username: str,
                              n: int = 100) -> Json:
    """Collect n posts in which user was tagged.

    Strategy: click the username, get to the main page of the user, a few posts
    are displayed in the user's main page. Click the button tagged to see all the
    posts in which the user was tagged.The request was sent to the path
    `/<user_name>/tagged/` to get the tagged posts/reels and a next_max_id for
    loading other posts/reels. To load the other posts/reels, move the mouse to
    the bottom of the page, it will trigger another request sent to the path
    /graphql/query/?doc_id=<tagged_user_id>&variables=<next_max_id>

    Args:
        username (str): name of the user.
        n (int): maximum number of tagged posts, which should be collected. By
         default, it's 100. If it's set to 0, collect all posts.

    Returns:
        Json: all visible tagged posts in json format.
    """
    return Posts().model_dump(mode="json")


def get_friendship_status(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                          username1: str,
                          username2: str) -> Json:
    """Get the relationship between any two users.

    Strategy: the only way to do it is to check if user_A is contained in
    user_B's followings or followers.

    Args:
        username1 (str): username of the person A.
        username2 (str): username of the person B.

    Returns:
        Json: friendship indication between person A and person B.
    """
    return FriendshipStatus().model_dump(mode="json")


@driver_implicit_wait(10)
def collect_followers(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                      username: str,
                      n: int = 100) -> Json:
    """Collect n followers of the given user. Anyone besides the account owner
    can get maximal 50 followers.

    Strategy: click the username, get to the main page of the user, then click
    followers, a list of followers of the user shows in a popup. A request
    triggered by the clicking was sent to the path
    `/api/v1/friendships/<user_id>/followers/?count=12&search_surface=follow_list_page`.

    Args:
        driver (:obj:`selenium.webdriver.remote.webdriver.WebDriver`): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of followers, which should be collected. By default,
         it's 100. If it's set to 0, collect all followers.

    Returns:
        Json: all visible followers' user information of the given user in json format.

    Examples:
        >>> from crawlinsta import webdriver
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> from crawlinsta.login import login
        >>> login(driver, "your_username", "your_password")
        >>> collect_followers(driver, "instagram_username")
    """
    if n < 0:
        raise ValueError("Parameter 'n' must be bigger than or equal to 0.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.randint(4, 6))

    # get user data
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={username}"
    request = filter_request(driver.requests, target_url)
    if not request:
        raise ValueError(f"No json response to the url '{target_url}' found.")
    json_data = get_json_data(request.response)
    user_data = json_data["data"]['user']
    del driver.requests

    followers_btn = driver.find_element(By.XPATH, f"//a[@href='/{username}/followers/'][@role='link']")
    followers_btn.click()
    time.sleep(random.randint(4, 6))

    # get 50 followers
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_data['id']}/followers/?count=12&search_surface=follow_list_page"
    request = filter_request(driver.requests, target_url)
    if not request:
        raise ValueError(f"No json response to the url '{target_url}' found.")
    json_data = get_json_data(request.response)
    results.append(json_data)
    remaining -= 12
    del driver.requests

    while 'next_max_id' in results[-1]:
        if n > 0 >= remaining:
            break

        followers_bottom = driver.find_element(By.XPATH, "//div[@class='_aano']/div[@class='_aanq']")
        ActionChains(driver).scroll_to_element(followers_bottom).perform()

        time.sleep(random.randint(4, 6))
        target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_data['id']}/following/?count=12&max_id={results[-1]['next_max_id']}"
        request = filter_request(driver.requests, target_url)
        if not request:
            raise ValueError(f"No json response to the url '{target_url}' found.")
        json_data = get_json_data(request.response)
        results.append(json_data)
        remaining -= 12
        del driver.requests

    users = []
    for user_info in json_data["users"][:n]:
        user = UserBasicInfo(id=user_info["pk"],
                             username=user_info["username"],
                             fullname=user_info["full_name"],
                             profile_pic_url=user_info["profile_pic_url"],
                             is_private=user_info["is_private"],
                             is_verified=user_info["is_verified"])
        users.append(user)
    return Users(users=users[:n]).model_dump(mode="json")


@driver_implicit_wait(10)
def collect_followings(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                       username: str,
                       n: int = 100) -> Json:
    """Collect n followings of the given user.

    Strategy: click the username, get to the main page of the user, then click following, a list of
    following of the user shows in a popup. A request triggered by the clicking was sent to the path
    `/api/v1/friendships/373735170/following/?count=12`.

    Args:
        driver (:obj:`selenium.webdriver.remote.webdriver.WebDriver`): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of followings, which should be collected. By default,
         it's 100. If it's set to 0, collect all followings.

    Returns:
        Json: all visible followings' user information of the given user in json format.

    Examples:
        >>> from crawlinsta import webdriver
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> from crawlinsta.login import login
        >>> login(driver, "your_username", "your_password")
        >>> collect_followings(driver, "instagram_username")
    """
    if n < 0:
        raise ValueError("Parameter 'n' must be bigger than or equal to 0.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.randint(4, 6))

    # get user data
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={username}"
    request = filter_request(driver.requests, target_url)
    if not request:
        raise ValueError(f"No json response to the url '{target_url}' found.")
    json_data = get_json_data(request.response)
    user_data = json_data["data"]['user']
    del driver.requests

    following_btn = driver.find_element(By.XPATH, f"//a[@href='/{username}/following/'][@role='link']")
    following_btn.click()
    time.sleep(random.randint(4, 6))

    # get first 12 followings
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_data['id']}/following/?count=12"
    request = filter_request(driver.requests, target_url)
    if not request:
        raise ValueError(f"No json response to the url '{target_url}' found.")
    json_data = get_json_data(request.response)
    results.append(json_data)
    remaining -= 12
    del driver.requests

    while 'next_max_id' in results[-1]:
        if n > 0 >= remaining:
            break

        following_bottom = driver.find_element(By.XPATH, "//div[@class='_aano']/div[@class='_aanq']")
        ActionChains(driver).scroll_to_element(following_bottom).perform()

        time.sleep(random.randint(4, 6))
        target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_data['id']}/following/?count=12&max_id={results[-1]['next_max_id']}"
        request = filter_request(driver.requests, target_url)
        if not request:
            raise ValueError(f"No json response to the url '{target_url}' found.")
        json_data = get_json_data(request.response)
        results.append(json_data)
        remaining -= 12
        del driver.requests

    users = []
    for json_data in results:
        for user_info in json_data["users"]:
            user = UserBasicInfo(id=user_info["pk"],
                                 username=user_info["username"],
                                 fullname=user_info["full_name"],
                                 profile_pic_url=user_info["profile_pic_url"],
                                 is_private=user_info["is_private"],
                                 is_verified=user_info["is_verified"])
            users.append(user)
    return Users(users=users[:n]).model_dump(mode="json")


@driver_implicit_wait(10)
def collect_following_hashtags(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                               username: str,
                               n: int = 100) -> Json:
    """Collect n followings hashtags of the given user.

    Strategy: click the username, get to the main page of the user, then click
    following and click hashtags, a list of following hashtags of the user shows
    in a popup. A request triggered by the clicking was sent to the path
    `/api/v1/friendships/373735170/following/?count=12`.

    Args:
        driver (:obj:`selenium.webdriver.remote.webdriver.WebDriver`): selenium
         driver for controlling the browser to perform certain actions.
        username (str): name of the user.
        n (int): maximum number of followings, which should be collected.
         By default, it's 100. If it's set to 0, collect all followings.

    Returns:
        Json: all visible followings hashtags' information of the given user in
        json format.

    Examples:
        >>> from crawlinsta import webdriver
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> from crawlinsta.login import login
        >>> login(driver, "your_username", "your_password")
        >>> collect_following_hashtags(driver, "instagram_username")
    """
    if n < 0:
        raise ValueError("Parameter 'n' must be bigger than or equal to 0.")

    results = []
    remaining = n

    driver.get(f'{INSTAGRAM_DOMAIN}/{username}/')
    time.sleep(random.randint(4, 6))
    target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={username}"
    request = filter_request(driver.requests, target_url)
    if not request:
        raise ValueError(f"No json response to the url '{target_url}' found.")
    json_data = get_json_data(request.response)
    user_data = json_data["data"]['user']
    del driver.requests

    following_btn_xpath = f"//a[@href='/{username}/following/'][@role='link']"
    following_btn = driver.find_element(By.XPATH, following_btn_xpath)
    following_btn.click()

    time.sleep(random.randint(3, 5))

    hashtag_btn = driver.find_element(By.XPATH, "//span[text()='Hashtags']")
    hashtag_btn.click()
    time.sleep(random.randint(4, 6))

    # get first 12 followings
    target_url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?doc_id={FOLLOWING_DOC_ID}&variables=%7B%22id%22%3A%22{user_data['id']}%22%7D"
    request = filter_request(driver.requests, target_url)
    if not request:
        raise ValueError(f"No json response to the url '{target_url}' found.")
    json_data = get_json_data(request.response)
    results.append(json_data)
    remaining -= len(json_data["data"]['user']['edge_following_hashtag']['edges'])
    del driver.requests

    # while remaining > 0 and not results[-1]['extensions']['is_final']:
    #     following_bottom = driver.find_element(By.XPATH, "//div[@class='_aabq']")
    #     driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", following_bottom)
    #
    #     time.sleep(random.randint(4, 6))
    #     target_url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?doc_id={FOLLOWING_DOC_ID}&variables=%7B%22id%22%3A%22{user_data['id']}%22%7D"
    #     request = filter_request(driver.requests, target_url)
    #     if not request:
    #         raise ValueError(f"No json response to the url '{target_url}' found.")
    #     json_data = get_json_data(request.response)
    #     results.append(json_data)
    #     remaining -= 12
    #     del driver.requests

    hashtags = []
    for json_data in results:
        for item in json_data["data"]['user']['edge_following_hashtag']['edges']:
            hashtag = HashtagBasicInfo(id=item["node"]["id"],
                                       name=item["node"]["name"],
                                       post_count=item["node"]["media_count"],
                                       profile_pic_url=item["node"]["profile_pic_url"])
            hashtags.append(hashtag)
    return HashtagBasicInfos(hashtags=hashtags).model_dump(mode="json")


def collect_likers_of_post(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                           post_id: str,
                           n: int = 100) -> Json:
    """Collect the users, who likes a given post.

    Strategy: click the likes (a button with link `/p/<post_code>/liked_by/`), a
    list of likers shows in a popup.
    A request triggered by the clicking was sent to the path `/api/v1/post/<post_id>/likers/`

    Args:
        post_id (str): id of the post for collecting.
        n (int): maximum number of likers, which should be collected. By default,
         it's 100. If it's set to 0, collect all likers.

    Returns:
        Json: all likers' user information of the given post in json format.
    """
    return Likers().model_dump(mode="json")


def collect_comments(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                     post_id: str,
                     n: int = 100) -> Json:
    """Collect n comments of a given post.

    Strategy: click the post (a button with link `/p/<post_code>/`), a list of
    comments shows in a popup. A request triggered by the clicking was sent to the path
    `/api/v1/post/<post_id>/comments/?can_support_threading=true&permalink_enabled=false`
    The comments are paginated, to load more comments, have to use the mouse to click
    a button to load more comments.

    Args:
        post_id (str): id of the post, whose comments will be collected.
        n (int): maximum number of comments, which should be collected. By default,
         it's 100. If it's set to 0, collect all comments.

    Returns:
        Json: all comments of the given post in json format.
    """
    return Comments().model_dump(mode="json")


def search_with_keyword(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                        keyword: str,
                        pers: bool) -> Json:
    """Search hashtags or users with given keyword.

    Args:
        keyword (str): keyword for searching.
        pers (bool): indicating whether results should be personalized or not.

    Returns:
        Json: found users/hashtags.
    """
    return SearchingResult().model_dump(mode="json")


def collect_hashtag_top_posts(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                              hashtag: str) -> Json:
    """Collect top posts of a given hashtag.

    Strategy: click the search button from the left navigation bar, and input the hashtag in
    the searchbar, and select the desired hashtag from searching results. This action will
    trigger a request sent to the path `/api/v1/tags/web_info/?tag_name=<tag name>`, as result
    the top posts are showed.

    Args:
        hashtag (str): hashtag.

    Returns:
        Json: Hashtag information in a json format.
    """
    return Hashtag().model_dump(mode="json")


def collect_posts_by_music_id(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                              music_id: str) -> Json:
    """Search for all posts containing the given music_id.

    Strategy: the only way to collect the posts using the same music, is to first find
    a post with this music, then click the link "original audio" to get all the posts
    using this music.

    The request was sent to the path /reels/audio/<music_id>/.

    Args:
        music_id (str): id of the music.

    Returns:
        Json: a list of posts containing the music.
    """
    return Posts().model_dump(mode="json")


def download_media(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                   media_url: str,
                   path: str) -> None:
    """Download the image/video based on the given media_url, and store it to
    the given path.

    Args:
        media_url (str): url of the media for downloading.
        path (str): path for storing the downloaded media..
    """
    pass
