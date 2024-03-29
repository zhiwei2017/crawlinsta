import logging
import random
import time
from pydantic import Json
from urllib.parse import quote, urlencode
from seleniumwire.request import Request
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union, List, Dict, Any, Tuple
from ..schemas import Posts, Users, UserProfile, Post
from ..utils import search_request, get_json_data, filter_requests, get_user_data
from ..data_extraction import extract_post, extract_id
from ..constants import JsonResponseContentType

logger = logging.getLogger("crawlinsta")


class UserIDRequiredCollect:
    """Base class for collecting data that requires user id.

    Attributes:
        driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
        username (str): The username of the user.
        user_id (Optional[int]): The user id.
        user_data (Optional[Dict[str, Any]]): The user data dictionary."""
    def __init__(self, driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str) -> None:
        """Initialize UserIDRequiredCollect.

        Args:
            driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
            username (str): The username of the user.
        """
        self.driver = driver
        self.username = username
        self.user_id = None
        self.user_data = None

    def get_user_id(self) -> bool:
        """Get user id.

        Returns:
            bool: True if the user has a private account, False otherwise.

        Raises:
            ValueError: If the user is not found.
        """
        json_requests = filter_requests(self.driver.requests,
                                        JsonResponseContentType.application_json)

        if not json_requests:
            raise ValueError(f"User '{self.username}' not found.")

        self.user_data = get_user_data(json_requests, self.username)
        self.user_id = extract_id(self.user_data)
        return self.user_data["is_private"]


class CollectPostsBase(UserIDRequiredCollect):
    """Base class for collecting posts.

    Attributes:
        driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
        username (str): The username of the user.
        n (int): The number of posts to collect.
        target_url (str): The target URL to search for.
        collect_type (str): The type of data to collect.
        json_data_key (str): The key to extract the json data from.
        json_data_list (List[Dict[str, Any]]): The list of json data.
        remaining (int): The remaining number of posts to collect.
        json_requests (List[Dict[str, Any]]): The list of json requests.
        access_keys (Tuple[str]): The keys to access the post data.
    """
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 n: int,
                 url: str,
                 target_url: str,
                 collect_type: str,
                 json_data_key: str,
                 access_keys: Tuple[str] = ("node", )) -> None:
        """Initialize CollectPostsBase.

        Args:
            driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
            username (str): The username of the user.
            n (int): The number of posts to collect.
            target_url (str): The target URL to search for.
            collect_type (str): The type of data to collect.
            json_data_key (str): The key to extract the json data from.
            access_keys (Tuple[str]): The keys to access the post data.
        """
        if n <= 0:
            raise ValueError(f"The number of {collect_type} to collect "
                             f"must be a positive integer.")
        super().__init__(driver, username)
        self.n = n
        self.target_url = target_url
        self.url = url
        self.collect_type = collect_type
        self.json_data_key = json_data_key
        self.json_data_list = []
        self.remaining = n
        self.json_requests = []
        self.access_keys = access_keys

    def check_request_data(self, request: Request, after: str = "") -> bool:
        """Check request data.

        Args:
            request (Request): The request to check.
            after (str): The after cursor.

        Returns:
            bool: True if the request data is valid, False otherwise.
        """
        raise NotImplementedError

    def get_posts_data(self, after: str = "") -> bool:
        """Get posts data.

        Args:
            after (str): The after cursor in request body.

        Returns:
            bool: True if the posts data is found, False otherwise.
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

    def loading_action(self) -> None:
        """Loading action."""
        footer = self.driver.find_element(By.XPATH, "//footer")
        self.driver.execute_script("return arguments[0].scrollIntoView(true);", footer)
        time.sleep(random.SystemRandom().randint(4, 6))

        self.json_requests += filter_requests(self.driver.requests,
                                              JsonResponseContentType.text_javascript)
        del self.driver.requests

    def create_post_list(self) -> List[Post]:
        """Create post list.

        Returns:
            List[Dict[str, Any]]: The list of posts.
        """
        posts = []
        for result in self.json_data_list:
            for item in result['edges']:
                for k in self.access_keys:
                    item = item.get(k)
                item_dict = item
                post = extract_post(item_dict)
                posts.append(post)
        return posts

    def collect(self) -> Json:
        """Collect posts.

        Returns:
            Json: The collected posts in json format.

        Raises:
            ValueError: If the user is not found.
        """
        self.driver.get(self.url)
        time.sleep(random.SystemRandom().randint(4, 6))

        is_private_account = self.get_user_id()

        if is_private_account:
            logger.warning(f"User '{self.username}' has a private account.")
            return Posts(posts=[], count=0).model_dump(mode="json")

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


class CollectUsersBase(UserIDRequiredCollect):
    """Base class for collecting posts.

    Attributes:
        driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
        username (str): The username of the user.
        n (int): The number of users to collect.
        target_url_format (str): The target URL format to search for.
        collect_type (str): The type of data to collect.
        json_data_list (List[Dict[str, Any]]): The list of json data.
        remaining (int): The remaining number of users to collect.
        json_requests (List[Dict[str, Any]]): The list of json requests.
        initial_load_data_btn_xpath (str): The xpath of the initial load data button.
    """

    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 n: int,
                 url: str,
                 target_url_format: str,
                 collect_type: str,
                 initial_load_data_btn_xpath: str) -> None:
        """Initialize CollectPostsBase.

        Args:
            driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
            username (str): The username of the user.
            n (int): The number of users to collect.
            target_url_format (str): The target URL format to search for.
            collect_type (str): The type of data to collect.
            initial_load_data_btn_xpath (str): The xpath of the initial load data button.
        """
        if n <= 0:
            raise ValueError(f"The number of {collect_type} to collect "
                             f"must be a positive integer.")
        super().__init__(driver, username)
        self.n = n
        self.url = url
        self.target_url_format = target_url_format
        self.collect_type = collect_type
        self.json_data_list = []
        self.remaining = n
        self.json_requests = []
        self.initial_load_data_btn_xpath = initial_load_data_btn_xpath

    def initial_load_data(self) -> None:
        """Initial load data."""
        followers_btn = self.driver.find_element(By.XPATH, self.initial_load_data_btn_xpath)
        followers_btn.click()
        time.sleep(random.SystemRandom().randint(4, 6))
        self.json_requests += filter_requests(self.driver.requests)
        del self.driver.requests

    def get_request_query_dict(self) -> Dict[str, Any]:
        """Get request query dict."""
        raise NotImplementedError

    def get_target_url(self) -> str:
        """Get target URL.

        Returns:
            str: The target URL.
        """
        query_dict = self.get_request_query_dict()
        query_str = urlencode(query_dict, quote_via=quote)
        target_url = self.target_url_format.format(user_id=self.user_id,
                                                   query_str=query_str)
        return target_url

    def get_users_data(self) -> bool:
        """Get posts data.

        Returns:
            bool: True if the posts data is found, False otherwise.
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

    def loading_action(self) -> None:
        """Loading action."""
        followers_bottom = self.driver.find_element(By.XPATH, "//div[@class='_aano']//div[@role='progressbar']")
        self.driver.execute_script("return arguments[0].scrollIntoView(true);", followers_bottom)
        time.sleep(random.SystemRandom().randint(4, 6))
        self.json_requests += filter_requests(self.driver.requests)
        del self.driver.requests

    def create_users_list(self, key: str = "users") -> List[UserProfile]:
        """Create a list of users from the given json data list.

        Args:
            key (str): The key to extract from the json data. Default is "users".

        Returns:
            List[UserProfile]: The list of users.
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

    def collect(self) -> Json:
        """Collect users.

        Returns:
            Json: The collected users in json format.
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
