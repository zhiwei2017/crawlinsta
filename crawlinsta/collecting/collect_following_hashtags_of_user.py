import json
import logging
import random
import time
from urllib.parse import quote, urlencode
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import HashtagBasicInfo, HashtagBasicInfos
from ..utils import search_request, get_json_data, filter_requests, get_user_data
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_id
from ..constants import INSTAGRAM_DOMAIN, GRAPHQL_QUERY_PATH, FOLLOWING_DOC_ID

logger = logging.getLogger("crawlinsta")


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

    Raises:
        ValueError: if the number of following hashtags to collect is not a positive integer.
        ValueError: if the user with the given username is not found.

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
    time.sleep(random.SystemRandom().randint(4, 6))

    json_requests = filter_requests(driver.requests)
    del driver.requests

    if not json_requests:
        raise ValueError(f"User '{username}' not found.")

    user_data = get_user_data(json_requests, username)
    user_id = extract_id(user_data)

    if user_data["is_private"]:
        logger.warning(f"User '{username}' has a private account.")
        return HashtagBasicInfos(hashtags=[], count=0).model_dump(mode="json")

    following_btn_xpath = f"//a[@href='/{username}/following/'][@role='link']"
    following_btn = driver.find_element(By.XPATH, following_btn_xpath)
    following_btn.click()
    time.sleep(random.SystemRandom().randint(3, 5))

    hashtag_btn = driver.find_element(By.XPATH, "//span[text()='Hashtags']")
    hashtag_btn.click()
    time.sleep(random.SystemRandom().randint(4, 6))

    json_requests += filter_requests(driver.requests)
    del driver.requests

    # get first 12 followings
    variables = dict(id=user_id)
    query_dict = dict(doc_id=FOLLOWING_DOC_ID, variables=json.dumps(variables, separators=(',', ':')))
    target_url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?{urlencode(query_dict, quote_via=quote)}"
    idx = search_request(json_requests, target_url)

    if idx is None:
        logger.warning(f"No following hashtags found for user '{username}'.")
        return HashtagBasicInfos(hashtags=[], count=0).model_dump(mode="json")

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

