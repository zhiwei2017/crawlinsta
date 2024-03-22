import json
import logging
import random
import time
from urllib.parse import parse_qs
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..schemas import (
    UserProfile, HashtagBasicInfo, SearchingResultHashtag, SearchingResultUser,
    LocationBasicInfo, Place, SearchingResultPlace, SearchingResult
)
from ..utils import search_request, get_json_data, filter_requests
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_id
from ..constants import INSTAGRAM_DOMAIN, JsonResponseContentType

logger = logging.getLogger("crawlinsta")


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
                "profile_pic_url": "https://scontent.cdninstagram.com/v13b",
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
    time.sleep(random.SystemRandom().randint(4, 6))

    search_btn = driver.find_element(By.XPATH, '//a[@href="#"][@role="link"]')
    search_btn.click()
    time.sleep(random.SystemRandom().randint(4, 6))

    del driver.requests

    search_input_box = driver.find_element(
        By.XPATH, '//input[@aria-label="Search input"][@placeholder="Search"][@type="text"]')
    search_input_box.send_keys(keyword)
    time.sleep(random.SystemRandom().randint(6, 8))

    if not pers:
        del driver.requests
        not_pers_btn = driver.find_element(
            By.XPATH,
            '//div[@aria-label="Not personalised"][@role="button"][@tabindex="0"]//span[text()="Not personalised"]')
        not_pers_btn.click()
        time.sleep(random.SystemRandom().randint(6, 8))

    json_requests = filter_requests(driver.requests, response_content_type=JsonResponseContentType.text_javascript)
    del driver.requests

    target_url = f"{INSTAGRAM_DOMAIN}/api/graphql"
    idx = search_request(json_requests, target_url, JsonResponseContentType.text_javascript,
                         check_request_data, keyword, pers)

    if idx is None:
        logger.warning(f"No search results found for keyword '{keyword}'.")
        return SearchingResult(hashtags=[], users=[], places=[], personalised=pers).model_dump(mode="json")

    request = json_requests.pop(idx)
    json_data = get_json_data(request.response)
    data_key = "xdt_api__v1__fbsearch__topsearch_connection" if pers else "xdt_api__v1__fbsearch__non_profiled_serp"
    json_data = json_data["data"][data_key]

    hashtags = []
    places = []
    if pers:
        for hashtag_dict in json_data.get("hashtags", []):
            hashtag_info_dict = hashtag_dict["hashtag"]
            hashtag_basic_info = HashtagBasicInfo(id=extract_id(hashtag_info_dict),
                                                  name=hashtag_info_dict["name"],
                                                  post_count=hashtag_info_dict["media_count"],
                                                  profile_pic_url=hashtag_info_dict.get("profile_pic_url", ""))
            hashtag = SearchingResultHashtag(position=hashtag_dict["position"],
                                             hashtag=hashtag_basic_info)
            hashtags.append(hashtag)

        for place_info in json_data.get("places", []):
            place = SearchingResultPlace(position=place_info["position"],
                                         place=Place(
                                             location=LocationBasicInfo(id=extract_id(place_info["place"]["location"]),
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
                                                    is_verified=user_info_dict.get("is_verified"),
                                                    is_private=user_info_dict.get("is_private")))
        users.append(user)

    searching_result = SearchingResult(hashtags=hashtags,
                                       users=users,
                                       places=places,
                                       personalised=pers)
    return searching_result.model_dump(mode="json")
