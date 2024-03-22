import json
import logging
import random
import re
import time
from urllib.parse import parse_qs
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import UserBasicInfo, Comment, Comments
from ..utils import search_request, get_json_data, filter_requests, find_brackets
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_id
from ..constants import INSTAGRAM_DOMAIN, GRAPHQL_QUERY_PATH, JsonResponseContentType

logger = logging.getLogger("crawlinsta")


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

    Raises:
        ValueError: if the number of comments to collect is not a positive integer.

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
        start_idx = data_str.find("xdt_api__v1__media__media_id__comments__connection")
        offset = len("xdt_api__v1__media__media_id__comments__connection")
        start_idx += offset
        data_str = data_str[start_idx:]
        start, stop = find_brackets(data_str)[-1]
        json_data = json.loads(data_str[start:stop + 1])
        return json_data

    if n <= 0:
        raise ValueError("The number of comments to collect must be a positive integer.")

    results = []
    remaining = n

    driver.get(f"{INSTAGRAM_DOMAIN}/p/{post_code}/")
    time.sleep(random.SystemRandom().randint(4, 6))

    # get the media id for later requests filtering
    meta_tag_xpath = "//meta[@property='al:ios:url']"
    meta_tag = driver.find_element(By.XPATH, meta_tag_xpath)
    post_ids = re.findall("\d+", meta_tag.get_attribute("content"))  # noqa
    if not post_ids:
        logger.warning(f"No post id found for post '{post_code}'.")
        return Comments(comments=[], count=0).model_dump(mode="json")
    post_id = post_ids[0]

    json_requests = []
    target_url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}"
    cached_data = find_cached_data()

    if cached_data:
        results.append(cached_data)
        remaining -= len(cached_data["edges"])
    else:
        json_requests = filter_requests(driver.requests, JsonResponseContentType.application_json)
        del driver.requests

        idx = search_request(json_requests,
                             target_url,
                             JsonResponseContentType.application_json,
                             check_request_data,
                             post_id)
        if idx is None:
            logger.warning(f"No comments found for post '{post_code}'.")
            return Comments(comments=[], count=0).model_dump(mode="json")

        request = json_requests.pop(idx)
        json_data = get_json_data(request.response)["data"]["xdt_api__v1__media__media_id__comments__connection"]
        results.append(json_data)
        remaining -= len(json_data["edges"])

    while results[-1]["page_info"]['has_next_page'] and remaining > 0:
        xpath = '//div[@class="x78zum5 xdt5ytf x1iyjqo2"]/div[@class="x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 ' \
                'x5pf9jr xo71vjh x1uhb9sk x1plvlek xryxfnj x1c4vz4f x2lah0s xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh ' \
                'x1nhvcw1"]'
        comment_lists = driver.find_elements(By.XPATH, xpath)
        driver.execute_script("return arguments[0].scrollIntoView(true);", comment_lists[-1])

        time.sleep(random.SystemRandom().randint(4, 6))
        json_requests += filter_requests(driver.requests,
                                         JsonResponseContentType.application_json)
        del driver.requests

        idx = search_request(json_requests,
                             target_url,
                             JsonResponseContentType.application_json,
                             check_request_data,
                             post_id)
        if idx is None:
            break
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
                              is_liked_by_post_owner=comment_dict.get("has_liked_comment", False),
                              comment_like_count=comment_dict.get("comment_like_count", 0))
            comments.append(comment)
    comments = comments[:n]
    return Comments(comments=comments, count=len(comments)).model_dump(mode="json")
