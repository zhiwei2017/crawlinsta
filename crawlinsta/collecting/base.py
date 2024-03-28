import logging
import random
import time
from urllib.parse import quote, urlencode
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union, List, Dict, Any
from ..schemas import Posts, Users, UserProfile
from ..utils import search_request, get_json_data, filter_requests, get_user_data
from ..data_extraction import extract_post, extract_id
from ..constants import JsonResponseContentType

logger = logging.getLogger("crawlinsta")


class CollectPostsBase:
    """Base class for collecting posts."""
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 n: int,
                 url,
                 target_url: str,
                 collect_type: str,
                 json_data_key: str,
                 primary_key="node",
                 secondary_key=None):
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
        self.username = username
        if n <= 0:
            raise ValueError(f"The number of {collect_type} to collect "
                             f"must be a positive integer.")
        self.n = n
        self.target_url = target_url
        self.url = url
        self.collect_type = collect_type
        self.json_data_key = json_data_key
        self.json_data_list = []
        self.remaining = n
        self.json_requests = []
        self.primary_key = primary_key
        self.secondary_key = secondary_key

    def get_user_id(self):
        """Get user ID."""
        pass

    def check_request_data(self, request, after=""):
        """Check request data."""
        pass

    def get_posts_data(self, after=""):
        """Get posts data.

        Args:
            json_requests ():
            after ():

        Returns:

        """
        idx = search_request(self.json_requests, self.target_url,
                             JsonResponseContentType.text_javascript,
                             self.check_request_data, after)
        if idx is None:
            return False

        request = self.json_requests.pop(idx)
        json_data = get_json_data(request.response)["data"][self.json_data_key]
        self.json_data_list.append(json_data)
        self.remaining -= len(json_data["edges"])
        return True

    def loading_action(self):
        """Loading action."""
        footer = self.driver.find_element(By.XPATH, "//footer")
        self.driver.execute_script("return arguments[0].scrollIntoView(true);", footer)
        time.sleep(random.SystemRandom().randint(4, 6))

        self.json_requests += filter_requests(self.driver.requests,
                                              JsonResponseContentType.text_javascript)
        del self.driver.requests

    def create_post_list(self):
        """Create post list.

        Args:
            primary_key ():
            secondary_key ():

        Returns:

        """
        posts = []
        for result in self.json_data_list:
            for item in result['edges']:
                item_dict = item[self.primary_key] if not self.secondary_key \
                    else item[self.primary_key][self.secondary_key]
                post = extract_post(item_dict)
                posts.append(post)
        return posts

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

        self.get_user_id()

        self.json_requests += filter_requests(self.driver.requests,
                                              JsonResponseContentType.text_javascript)
        del self.driver.requests

        if not self.json_requests:
            raise ValueError(f"User '{self.username}' not found.")

        # get first 12 documents
        status = self.get_posts_data()
        if not status:
            logger.warning(f"No {self.collect_type} found for user '{self.username}'.")
            return Posts(posts=[], count=0).model_dump(mode="json")  # type: ignore

        while self.json_data_list[-1]['page_info']["has_next_page"] and self.remaining > 0:
            self.loading_action()
            status = self.get_posts_data(after=self.json_data_list[-1]['page_info']["end_cursor"])
            if not status:
                break

        posts = self.create_post_list()[:self.n]
        return Posts(posts=posts, count=len(posts)).model_dump(mode="json")


class CollectUsersBase:
    """Base class for collecting posts."""

    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 n: int,
                 url: str,
                 target_url_format: str,
                 collect_type: str,
                 initial_load_data_btn_xpath: str):
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
        self.username = username
        if n <= 0:
            raise ValueError(f"The number of {collect_type} to collect "
                             f"must be a positive integer.")
        self.n = n
        self.url = url
        self.target_url_format = target_url_format
        self.collect_type = collect_type
        self.json_data_list = []
        self.remaining = n
        self.user_id = None
        self.json_requests = []
        self.initial_load_data_btn_xpath = initial_load_data_btn_xpath

    def get_user_id(self):
        json_requests = filter_requests(self.driver.requests,
                                        JsonResponseContentType.application_json)

        if not json_requests:
            raise ValueError(f"User '{self.username}' not found.")

        user_data = get_user_data(json_requests, self.username)
        self.user_id = extract_id(user_data)
        return user_data["is_private"]

    def initial_load_data(self):
        """Initial load data."""
        followers_btn = self.driver.find_element(By.XPATH, self.initial_load_data_btn_xpath)
        followers_btn.click()
        time.sleep(random.SystemRandom().randint(4, 6))
        self.json_requests += filter_requests(self.driver.requests)
        del self.driver.requests

    def get_request_query_dict(self) -> Dict[str, Any]:
        """Get request query dict."""
        pass

    def get_target_url(self):
        """Get target URL."""
        query_dict = self.get_request_query_dict()
        query_str = urlencode(query_dict, quote_via=quote)
        target_url = self.target_url_format.format(user_id=self.user_id,
                                                   query_str=query_str)
        return target_url

    def get_users_data(self):
        """Get posts data.

        Args:
            json_requests ():
            after ():

        Returns:

        """
        target_url = self.get_target_url()
        idx = search_request(self.json_requests, target_url,
                             JsonResponseContentType.application_json)

        if idx is None:
            return False

        request = self.json_requests.pop(idx)
        json_data = get_json_data(request.response)
        self.json_data_list.append(json_data)
        self.remaining -= len(json_data["users"])
        return True

    def loading_action(self):
        """Loading action."""
        followers_bottom = self.driver.find_element(By.XPATH, "//div[@class='_aano']//div[@role='progressbar']")
        self.driver.execute_script("return arguments[0].scrollIntoView(true);", followers_bottom)
        time.sleep(random.SystemRandom().randint(4, 6))
        self.json_requests += filter_requests(self.driver.requests)
        del self.driver.requests

    def create_users_list(self, key: str = "users"):
        """Create a list of users from the given json data list.

        Args:
            json_data_list (List[Dict[str, Any]]): The list of json data.
            key (str): The key to extract from the json data. Default is "users".

        Returns:
            List[UserProfile]: The list of users.

        Examples:
            >>> create_users_list([{"user": {"pk": 123, "username": "username", "full_name": "fullname",
            ... "profile_pic_url": "https://example.com", "is_private": False, "is_verified": True}}], "user")
            [UserProfile(id=123, username="username", fullname="fullname", profile_pic_url="https://example.com",
            is_private=False, is_verified=True)]
        """
        users = []
        for json_data in self.json_data_list:
            for user_info in json_data[key]:
                user = UserProfile(id=extract_id(user_info),
                                   username=user_info.get("username", ""),
                                   fullname=user_info.get("full_name", ""),
                                   profile_pic_url=user_info.get("profile_pic_url", ""),
                                   is_private=user_info.get("is_private"),
                                   is_verified=user_info.get("is_verified"))
                users.append(user)
        return users

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

        is_private_account = self.get_user_id()

        if is_private_account:
            logger.warning(f"User '{self.username}' has a private account.")
            return Users(users=[], count=0).model_dump(mode="json")

        self.initial_load_data()

        # get 50 followers
        status = self.get_users_data()
        if not status:
            logger.warning(f"No {self.collect_type} found for user '{self.username}'.")
            return Users(users=[], count=0).model_dump(mode="json")

        while 'next_max_id' in self.json_data_list[-1] and self.remaining > 0:
            self.loading_action()
            status = self.get_users_data()
            if not status:
                break

        users = self.create_users_list("users")[:self.n]
        return Users(users=users, count=len(users)).model_dump(mode="json")
