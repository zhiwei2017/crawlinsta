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


class CollectCommentOfPost:
    """Base class for collecting posts."""
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 post_code: str,
                 n: int,
                 url,
                 target_url,
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
        self.post_code = post_code
        if n <= 0:
            raise ValueError(f"The number of {collect_type} to collect "
                             f"must be a positive integer.")
        self.n = n
        self.url = url
        self.target_url = target_url
        self.collect_type = collect_type
        self.json_data_list = []
        self.json_requests = []
        self.remaining = n
        self.post_id = None

    def get_post_id(self):
        meta_tag_xpath = "//meta[@property='al:ios:url']"
        meta_tag = self.driver.find_element(By.XPATH, meta_tag_xpath)
        post_ids = re.findall("\d+", meta_tag.get_attribute("content"))  # noqa
        if not post_ids:
            return
        self.post_id = post_ids[0]

    def check_request_data(self, request):
        request_data = parse_qs(request.body.decode())
        variables = json.loads(request_data.get("variables", ["{}"])[0])
        if request_data.get("av", [''])[0] != "17841461911219001":
            return False
        elif not variables:
            return False
        elif variables.get("media_id", "") != self.post_id:
            return False
        return True

    def find_cached_data(self):
        scripts = self.driver.find_elements(By.XPATH, '//script[@type="application/json"]')
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

    def get_posts_data(self):
        """Get posts data.

        Args:
            json_requests ():
            after ():

        Returns:

        """
        idx = search_request(self.json_requests,
                             self.target_url,
                             JsonResponseContentType.application_json,
                             self.check_request_data)
        if idx is None:
            return False

        request = self.json_requests.pop(idx)
        json_data = get_json_data(request.response)["data"]["xdt_api__v1__media__media_id__comments__connection"]
        self.json_data_list.append(json_data)
        self.remaining -= len(json_data["edges"])
        return True

    def loading_action(self):
        """Loading action."""
        xpath = '//div[@class="x78zum5 xdt5ytf x1iyjqo2"]/div[@class="x9f619 xjbqb8w x78zum5 x168nmei x13lgxp2 ' \
                'x5pf9jr xo71vjh x1uhb9sk x1plvlek xryxfnj x1c4vz4f x2lah0s xdt5ytf xqjyukv x1qjc9v5 x1oa3qoh ' \
                'x1nhvcw1"]'
        comment_lists = self.driver.find_elements(By.XPATH, xpath)
        self.driver.execute_script("return arguments[0].scrollIntoView(true);", comment_lists[-1])

        time.sleep(random.SystemRandom().randint(4, 6))
        self.json_requests += filter_requests(self.driver.requests,
                                              JsonResponseContentType.application_json)
        del self.driver.requests

    def create_comment_list(self):
        """Create post list.

        Args:
            primary_key ():
            secondary_key ():

        Returns:

        """
        comments = []
        for json_data in self.json_data_list:
            for item in json_data["edges"]:
                comment_dict = item["node"]
                default_created_at_timestamp = comment_dict.get("created_at", 0)
                comment = Comment(id=extract_id(comment_dict),
                                  user=UserBasicInfo(id=extract_id(comment_dict["user"]),
                                                     username=comment_dict["user"]["username"]),
                                  post_id=self.post_id,
                                  created_at_utc=comment_dict.get("created_at_utc", default_created_at_timestamp),
                                  status=comment_dict.get("status"),
                                  share_enabled=comment_dict.get("share_enabled"),
                                  is_ranked_comment=comment_dict.get("is_ranked_comment"),
                                  text=comment_dict["text"],
                                  has_translation=comment_dict.get("has_translation", False),
                                  is_liked_by_post_owner=comment_dict.get("has_liked_comment", False),
                                  comment_like_count=comment_dict.get("comment_like_count", 0))
                comments.append(comment)
        return comments

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

        # get the media id for later requests filtering
        self.get_post_id()
        if not self.post_id:
            logger.warning(f"No post id found for post '{self.post_code}'.")
            return Comments(comments=[], count=0).model_dump(mode="json")

        cached_data = self.find_cached_data()

        if cached_data:
            self.json_data_list.append(cached_data)
            self.remaining -= len(cached_data["edges"])
        else:
            self.json_requests = filter_requests(self.driver.requests,
                                                 JsonResponseContentType.application_json)
            del self.driver.requests

            status = self.get_posts_data()
            if not status:
                logger.warning(f"No comments found for post '{self.post_code}'.")
                return Comments(comments=[], count=0).model_dump(mode="json")

        while self.json_data_list[-1]["page_info"]['has_next_page'] and self.remaining > 0:
            self.loading_action()

            status = self.get_posts_data()
            if not status:
                break

        comments = self.create_comment_list()
        comments = comments[:self.n]
        return Comments(comments=comments, count=len(comments)).model_dump(mode="json")


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
    return CollectCommentOfPost(driver, post_code, n,
                                f"{INSTAGRAM_DOMAIN}/p/{post_code}/",
                                f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}",
                                "comments").collect()
