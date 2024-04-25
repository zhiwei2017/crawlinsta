import json
import logging
import random
import time
from urllib.parse import parse_qs
from pydantic import Json
from selenium.webdriver.common.by import By
from seleniumwire.request import Request
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union, List, Dict, Any
from ..schemas import (
    UserProfile, HashtagBasicInfo, SearchingResultHashtag, SearchingResultUser,
    LocationBasicInfo, Place, SearchingResultPlace, SearchingResult
)
from ..utils import search_request, get_json_data, filter_requests
from ..decorators import driver_implicit_wait
from ..data_extraction import extract_id
from ..constants import INSTAGRAM_DOMAIN, JsonResponseContentType
from .base import CollectBase

logger = logging.getLogger("crawlinsta")


class SearchWithKeyword(CollectBase):
    """Search with keyword.

    Attributes:
        driver (Union[Chrome, Edge, Firefox, Safari, Remote]): selenium
         driver for controlling the browser to perform certain actions.
        keyword (str): keyword for searching.
        pers (bool): indicating whether results should be personalized or not.
        data_key (str): key for extracting data from json data.
        json_requests (List[Request]): list of requests.
        json_data (dict): json data.
    """
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 keyword: str,
                 pers: bool) -> None:
        """Initialize SearchWithKeyword class.

        Args:
            driver (Union[Chrome, Edge, Firefox, Safari, Remote]): selenium
             driver for controlling the browser to perform certain actions.
            keyword (str): keyword for searching.
            pers (bool): indicating whether results should be personalized or not.
        """
        super().__init__(driver, INSTAGRAM_DOMAIN)
        self.keyword = keyword
        self.pers = pers
        self.data_key = "xdt_api__v1__fbsearch__"
        if pers:
            self.data_key += "topsearch_connection"
        else:
            self.data_key += "non_profiled_serp"
        self.json_requests: List[Request] = []
        self.json_data: Union[Dict[str, Any], None] = None

    def check_request_data(self, request: Request) -> bool:
        """Check request data.

        Args:
            request (Request): request object.

        Returns:
            bool: True if request data is valid, False otherwise.
        """
        request_data = parse_qs(request.body.decode())
        variables = json.loads(request_data.get("variables", ["{}"])[0])
        if not variables:
            return False
        elif self.pers and variables.get("data", dict(query=""))["query"] != self.keyword:
            return False
        elif not self.pers and variables.get("query") != self.keyword:
            return False
        return True

    def extract_data(self) -> bool:
        """Extract data from json data and store it in json_data attribute.

        Returns:
            bool: True if data is extracted successfully, False otherwise.
        """
        target_url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        idx = search_request(self.json_requests, target_url,
                             JsonResponseContentType.text_javascript,
                             self.check_request_data)

        if idx is None:
            return False

        request = self.json_requests.pop(idx)
        json_data = get_json_data(request.response)
        self.json_data = json_data["data"][self.data_key]
        return True

    def fetch_data(self) -> None:
        """Loading action."""
        search_btn = self.driver.find_element(By.XPATH, '//a[@href="#"][@role="link"]')
        search_btn.click()
        time.sleep(random.SystemRandom().randint(4, 6))

        del self.driver.requests

        search_input_box = self.driver.find_element(
            By.XPATH, '//input[@aria-label="Search input"][@placeholder="Search"][@type="text"]')
        search_input_box.send_keys(self.keyword)
        time.sleep(random.SystemRandom().randint(6, 8))

        if not self.pers:
            del self.driver.requests
            not_pers_btn = self.driver.find_element(
                By.XPATH,
                '//div[@aria-label="Not personalised" '
                'or @aria-label="Not personalized" '
                'or @aria-label="Nicht personalisiert"]'
                '[@role="button"][@tabindex="0"]'
                '//span[text()="Not personalised" '
                'or text()="Not personalized" '
                'or text()="Nicht personalisiert"]')
            not_pers_btn.click()
            time.sleep(random.SystemRandom().randint(6, 8))

        self.json_requests = filter_requests(self.driver.requests, JsonResponseContentType.text_javascript)
        del self.driver.requests

    def generate_result(self, empty_result: bool = False) -> Json:
        """Generate result.

        Args:
            empty_result (bool): indicating whether result is empty or not.

        Returns:
            Json: searching result.
        """
        if empty_result:
            return SearchingResult(hashtags=[],
                                   users=[],
                                   places=[],
                                   personalised=self.pers).model_dump(mode="json")
        hashtags = []
        places = []
        if self.pers:
            for hashtag_dict in self.json_data.get("hashtags", []):  # type: ignore
                hashtag_info_dict = hashtag_dict["hashtag"]
                hashtag_basic_info = HashtagBasicInfo(id=extract_id(hashtag_info_dict),
                                                      name=hashtag_info_dict["name"],
                                                      post_count=hashtag_info_dict["media_count"],
                                                      profile_pic_url=hashtag_info_dict.get("profile_pic_url", ""))
                hashtag = SearchingResultHashtag(position=hashtag_dict["position"],
                                                 hashtag=hashtag_basic_info)
                hashtags.append(hashtag)

            for place_info in self.json_data.get("places", []):  # type: ignore
                place = SearchingResultPlace(position=place_info["position"],
                                             place=Place(
                                                 location=LocationBasicInfo(
                                                     id=extract_id(place_info["place"]["location"]),
                                                     name=place_info["place"]["location"]["name"]),
                                                 subtitle=place_info["place"]["subtitle"],
                                                 title=place_info["place"]["title"]))
                places.append(place)

        users = []
        for i, user_info in enumerate(self.json_data.get("users", [])):  # type: ignore
            if self.pers:
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
                                           personalised=self.pers)
        return searching_result.model_dump(mode="json")

    def collect(self) -> Json:
        """Collect data from the webpage.

        Returns:
            Json: searching result.
        """
        self.load_webpage()

        self.fetch_data()
        status = self.extract_data()
        if not status:
            logger.warning(f"No search results found for keyword '{self.keyword}'.")
            return self.generate_result(empty_result=True)
        return self.generate_result(empty_result=False)


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
    return SearchWithKeyword(driver, keyword, pers).collect()
