import logging
import random
import re
import time
from pydantic import Json
from urllib.parse import quote, urlencode
from seleniumwire.request import Request
from selenium.webdriver.common.by import By
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union, List, Dict, Any, Sequence
from ..schemas import Posts, Users, UserProfile
from ..utils import search_request, get_json_data, filter_requests
from ..data_extraction import extract_post, extract_id
from ..constants import JsonResponseContentType, INSTAGRAM_DOMAIN, API_VERSION

logger = logging.getLogger("crawlinsta")


class CollectBase:
    """Base class for collecting data.

    Attributes:
        driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
        url (str): The URL to load.
    """
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 url: str) -> None:
        """Initialize CollectBase.

        Args:
            driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
            url (str): The URL to load.
        """
        self.driver = driver
        self.url = url

    def load_webpage(self) -> None:
        """Load webpage."""
        self.driver.get(self.url)
        time.sleep(random.SystemRandom().randint(4, 6))

    def fetch_data(self) -> None:
        """Fetching data."""
        raise NotImplementedError

    def continue_fetching(self) -> bool:
        """Continue fetching data.

        Returns:
            bool: True if continue fetching data, False otherwise.
        """
        return False

    def fetch_more_data(self) -> None:
        """Fetching more data."""
        pass

    def extract_data(self) -> bool:
        """Extract data.

        Returns:
            bool: True if the data is found, False otherwise.
        """
        return True

    def generate_result(self, empty_result=False) -> Json:
        """Generate response.

        Returns:
            Json: The generated response in json format.
        """
        return {}

    def collect(self) -> Json:
        """Collect data.

        Returns:
            Json: The collected data in json format.
        """
        raise NotImplementedError


class UserIDRequiredCollect(CollectBase):
    """Base class for collecting data that requires user id.

    Attributes:
        driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
        username (str): The username of the user.
        user_id (Optional[int]): The user id.
        user_data (Optional[Dict[str, Any]]): The user data dictionary.
        url (str): The URL to load.
    """
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 url: str) -> None:
        """Initialize UserIDRequiredCollect.

        Args:
            driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
            username (str): The username of the user.
            url (str): The URL to load.
        """
        super().__init__(driver, url)
        self.username = username
        self.user_id: Union[str, None] = None
        self.user_data: Union[Dict[str, Any], None] = None

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
        target_url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={self.username}"
        idx = search_request(json_requests, target_url, JsonResponseContentType.application_json)
        if idx is None:
            raise ValueError(f"User '{self.username}' not found.")
        request = json_requests.pop(idx)  # type: ignore
        json_data = get_json_data(request.response)
        self.user_data = json_data["data"]['user']
        self.user_id = extract_id(json_data["data"]['user'])  # type: ignore
        return self.user_data["is_private"]  # type: ignore


class CollectPostsBase(UserIDRequiredCollect):
    """Base class for collecting posts.

    Attributes:
        driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
        username (str): The username of the user.
        url (str): The URL to load.
        n (int): The number of posts to collect.
        target_url (str): The target URL to search for.
        collect_type (str): The type of data to collect.
        json_data_key (str): The key to extract the json data from.
        json_data_list (List[Dict[str, Any]]): The list of json data.
        remaining (int): The remaining number of posts to collect.
        json_requests (List[Dict[str, Any]]): The list of json requests.
        access_keys (Sequence[str]): The keys to access the post data.
    """
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 n: int,
                 url: str,
                 target_url: str,
                 response_content_type: str,
                 collect_type: str,
                 json_data_key: str,
                 access_keys: Sequence[str] = ("node", )) -> None:
        """Initialize CollectPostsBase.

        Args:
            driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
            username (str): The username of the user.
            n (int): The number of posts to collect.
            url (str): The URL to load.
            target_url (str): The target URL to search for.
            collect_type (str): The type of data to collect.
            json_data_key (str): The key to extract the json data from.
            access_keys (Sequence[str]): The keys to access the post data.
        """
        if n <= 0:
            raise ValueError(f"The number of {collect_type} to collect "
                             f"must be a positive integer.")
        super().__init__(driver, username, url)
        self.n = n
        self.target_url = target_url
        self.response_content_type = response_content_type
        self.collect_type = collect_type
        self.json_data_key = json_data_key
        self.json_data_list: List[Dict[str, Any]] = []
        self.remaining = n
        self.json_requests: List[Request] = []
        self.access_keys = access_keys
        self.no_data_found = False

    def check_request_data(self, request: Request, after: str = "") -> bool:
        """Check request data.

        Args:
            request (Request): The request to check.
            after (str): The after cursor.

        Returns:
            bool: True if the request data is valid, False otherwise.
        """
        raise NotImplementedError

    def fetch_data(self) -> None:
        """Fetching data.

        Raises:
            ValueError: If the user is not found.
        """

        self.json_requests += filter_requests(self.driver.requests,
                                              self.response_content_type)
        del self.driver.requests

        if not self.json_requests:
            raise ValueError(f"User '{self.username}' not found.")

    def extract_data(self) -> bool:
        """Get posts data.

        Returns:
            bool: True if the posts data is found, False otherwise.
        """
        after = self.json_data_list[-1]['page_info']["end_cursor"] if self.json_data_list else ""
        idx = search_request(self.json_requests, self.target_url,
                             self.response_content_type,
                             self.check_request_data, after)
        if idx is None:
            return False

        request = self.json_requests.pop(idx)
        json_data = get_json_data(request.response)["data"][self.json_data_key]
        self.json_data_list.append(json_data)
        self.remaining -= len(json_data["edges"])
        return True

    def continue_fetching(self) -> bool:
        """Continue fetching data.

        Returns:
            bool: True if continue fetching data, False otherwise.
        """
        return self.json_data_list[-1]['page_info']["has_next_page"] and self.remaining > 0

    def fetch_more_data(self) -> None:
        """Loading action."""
        footer = self.driver.find_element(By.XPATH, "//footer")
        self.driver.execute_script("return arguments[0].scrollIntoView(true);", footer)
        time.sleep(random.SystemRandom().randint(4, 6))

        self.json_requests += filter_requests(self.driver.requests,
                                              self.response_content_type)
        del self.driver.requests

    def generate_result(self, empty_result: bool = False) -> Json:
        """Create post list.

        Args:
            empty_result (bool): True if the result is empty, False otherwise.

        Returns:
            List[Dict[str, Any]]: The list of posts.
        """
        if empty_result:
            return Posts(posts=[], count=0).model_dump(mode="json")
        posts = []
        for result in self.json_data_list:
            for item in result['edges']:
                for k in self.access_keys:
                    item = item.get(k)
                item_dict = item
                post = extract_post(item_dict)
                posts.append(post)
        posts = posts[:self.n]
        return Posts(posts=posts, count=len(posts)).model_dump(mode="json")

    def collect(self) -> Json:
        """Collect posts.

        Returns:
            Json: The collected posts in json format.

        Raises:
            ValueError: If the user is not found.
        """
        self.load_webpage()

        is_private_account = self.get_user_id()

        if is_private_account:
            logger.warning(f"User '{self.username}' has a private account.")
            return self.generate_result(empty_result=True)

        self.fetch_data()

        # get first 12 documents
        status = self.extract_data()
        if not status:
            self.no_data_found = True
            logger.warning(f"No {self.collect_type} found for user '{self.username}'.")
            return self.generate_result(empty_result=True)  # type: ignore

        while self.continue_fetching():
            self.fetch_more_data()
            status = self.extract_data()
            if not status:
                break

        return self.generate_result(empty_result=False)


class CollectUsersBase(UserIDRequiredCollect):
    """Base class for collecting posts.

    Attributes:
        driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
        username (str): The username of the user.
        n (int): The number of users to collect.
        url (str): The URL to load.
        target_url_format (str): The target URL format to search for.
        collect_type (str): The type of data to collect.
        json_data_list (List[Dict[str, Any]]): The list of json data.
        remaining (int): The remaining number of users to collect.
        json_requests (List[Dict[str, Any]]): The list of json requests.
        fetch_data_btn_xpath (str): The xpath of the initial load data button.
    """

    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 username: str,
                 n: int,
                 url: str,
                 target_url_format: str,
                 collect_type: str,
                 fetch_data_btn_xpath: str) -> None:
        """Initialize CollectPostsBase.

        Args:
            driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
            username (str): The username of the user.
            n (int): The number of users to collect.
            url (str): The URL to load.
            target_url_format (str): The target URL format to search for.
            collect_type (str): The type of data to collect.
            fetch_data_btn_xpath (str): The xpath of the initial load data button.

        Raises:
            ValueError: If the number of users to collect is not a positive integer.
        """
        if n <= 0:
            raise ValueError(f"The number of {collect_type} to collect "
                             f"must be a positive integer.")
        super().__init__(driver, username, url)
        self.n = n
        self.target_url_format = target_url_format
        self.collect_type = collect_type
        self.json_data_list: List[Dict[str, Any]] = []
        self.remaining = n
        self.json_requests: List[Request] = []
        self.fetch_data_btn_xpath = fetch_data_btn_xpath

    def fetch_data(self) -> None:
        """Initial load data."""
        followers_btn = self.driver.find_element(By.XPATH, self.fetch_data_btn_xpath)
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

    def extract_data(self) -> bool:
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

    def continue_fetching(self) -> bool:
        """Continue fetching data.

        Returns:
            bool: True if continue fetching data, False otherwise.
        """
        return 'next_max_id' in self.json_data_list[-1] and self.remaining > 0

    def fetch_more_data(self) -> None:
        """Loading action."""
        followers_bottom = self.driver.find_element(By.XPATH, "//div[@class='_aano']//div[@role='progressbar']")
        self.driver.execute_script("return arguments[0].scrollIntoView(true);", followers_bottom)
        time.sleep(random.SystemRandom().randint(4, 6))
        self.json_requests += filter_requests(self.driver.requests)
        del self.driver.requests

    def generate_result(self, empty_result: bool = False) -> Json:
        """Create a list of users from the given json data list.

        Args:
            empty_result (bool): True if the result is empty, False otherwise.

        Returns:
            List[UserProfile]: The list of users.
        """
        if empty_result:
            return Users(users=[], count=0).model_dump(mode="json")
        users = []
        for json_data in self.json_data_list:
            for user_info in json_data["users"]:
                user = UserProfile(id=extract_id(user_info),
                                   username=user_info.get("username", ""),
                                   fullname=user_info.get("full_name", ""),
                                   profile_pic_url=user_info.get("profile_pic_url", ""),
                                   is_private=user_info.get("is_private"),
                                   is_verified=user_info.get("is_verified"))
                users.append(user)
        users = users[:self.n]
        return Users(users=users, count=len(users)).model_dump(mode="json")

    def collect(self) -> Json:
        """Collect users.

        Returns:
            Json: The collected users in json format.
        """
        self.load_webpage()

        is_private_account = self.get_user_id()

        if is_private_account:
            logger.warning(f"User '{self.username}' has a private account.")
            return self.generate_result(empty_result=True)

        self.fetch_data()

        # get 50 followers
        status = self.extract_data()
        if not status:
            logger.warning(f"No {self.collect_type} found for user '{self.username}'.")
            return self.generate_result(empty_result=True)

        while self.continue_fetching():
            self.fetch_more_data()
            status = self.extract_data()
            if not status:
                break

        return self.generate_result(empty_result=False)


class CollectPostInfoBase(CollectBase):
    """Base class for collecting post information.

    Attributes:
        driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
        post_code (str): The post code.
        n (int): The number of posts to collect.
        collect_type (str): The type of data to collect.
        url (str): The URL to load.
        json_data_list (List[Dict[str, Any]]): The list of json data.
        json_requests (List[Dict[str, Any]]): The list of json requests.
        remaining (int): The remaining number of posts to collect.
        post_id (Optional[str]): The post id.
    """
    def __init__(self,
                 driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                 post_code: str,
                 n: int,
                 collect_type: str,
                 url: str) -> None:
        """Initialize CollectPostInfoBase.

        Args:
            driver (Union[Chrome, Edge, Firefox, Safari, Remote]): The selenium web driver.
            post_code (str): The post code.
            n (int): The number of posts to collect.
            collect_type (str): The type of data to collect.
            url (str): The URL to load.

        Raises:
            ValueError: If the number of posts to collect is not a positive integer.
        """
        if n <= 0:
            raise ValueError(f"The number of {collect_type} to collect "
                             f"must be a positive integer.")
        super().__init__(driver, url)
        self.n = n
        self.post_code = post_code
        self.collect_type = collect_type
        self.json_data_list: List[Dict[str, Any]] = []
        self.remaining = n
        self.json_requests: List[Request] = []
        self.post_id = None

    def get_post_id(self) -> None:
        """Get the post id."""
        meta_tag_xpath = "//meta[@property='al:ios:url']"
        meta_tag = self.driver.find_element(By.XPATH, meta_tag_xpath)
        post_ids = re.findall("\d+", meta_tag.get_attribute("content"))  # noqa
        if not post_ids:
            return
        self.post_id = post_ids[0]
