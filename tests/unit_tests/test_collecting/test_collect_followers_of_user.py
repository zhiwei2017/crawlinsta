import json
import pytest
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting.followers_of_user import collect_followers_of_user
from crawlinsta.constants import INSTAGRAM_DOMAIN, API_VERSION, JsonResponseContentType
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def __init__(self):
        self.user_id = None
        self.call_find_element_number = 0
        super().__init__()

    def get(self, url):
        self.user_id = "1798450984"
        username = url.split("/")[-2]

        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        with open("tests/resources/followers/web_profile_info.json", "r") as file:
            data = json.load(file)
        request = mock.Mock()
        request.url = url
        request.body = urlencode(dict(av="17841461911219001",
                                      variables=json.dumps({"render_surface": "PROFILE"}, separators=(',', ':'))),
                                 quote_via=quote).encode()
        request.response = mock.Mock(headers={"Content-Type": JsonResponseContentType.text_javascript,
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())

        self.requests = [request]

    def find_element(self, by, value):
        query_dict = dict(count=12)
        if self.call_find_element_number:
            query_dict["max_id"] = 12 * self.call_find_element_number
        query_dict["search_surface"] = "follow_list_page"
        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{self.user_id}/followers/?{urlencode(query_dict, quote_via=quote)}"
        request = mock.Mock()
        request.url = url

        with open(f"tests/resources/followers/followers{self.call_find_element_number + 1}.json", "r") as file:
            data = json.load(file)
        request.response = mock.Mock(headers={"Content-Type": JsonResponseContentType.application_json,
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]
        self.call_find_element_number += 1
        return mock.Mock()


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_followers_of_user(mocked_sleep):
    result = collect_followers_of_user(MockedDriver(), "marie_2_0", 30)
    with open("tests/resources/followers/result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


@pytest.mark.parametrize("n", [0, -1])
def test_collect_followers_of_user_fail(n):
    with pytest.raises(ValueError) as exc_info:
        collect_followers_of_user(MockedDriver(), "anasaiaofficial", n)
    assert str(exc_info.value) == "The number of followers to collect must be a positive integer."


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_followers_of_user_no_request(mocked_sleep):
    with pytest.raises(ValueError) as exc_info:
        collect_followers_of_user(BaseMockedDriver(), "anasaiaofficial")
    assert str(exc_info.value) == "User 'anasaiaofficial' not found."


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
@mock.patch("crawlinsta.collecting.base.CollectUsersBase.extract_data", return_value=False)
@mock.patch("crawlinsta.collecting.base.logger")
def test_collect_followers_of_user_no_followers(mocked_logger, mocked_extract_data, mocked_sleep):
    result = collect_followers_of_user(MockedDriver(), "anasaiaofficial", 30)
    assert result == {"users": [], "count": 0}
    mocked_logger.warning.assert_called_once_with("No followers found for user 'anasaiaofficial'.")


class MockedDriverPrivate(MockedDriver):
    def get(self, url):
        self.user_id = "1798450984"
        username = url.split("/")[-2]

        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        with open("tests/resources/followers/web_profile_info.json", "r") as file:
            data = json.load(file)
        data["data"]["user"]["is_private"] = True
        request = mock.Mock()
        request.url = url
        request.body = urlencode(dict(av="17841461911219001",
                                      variables=json.dumps({"render_surface": "PROFILE"}, separators=(',', ':'))),
                                 quote_via=quote).encode()
        request.response = mock.Mock(headers={"Content-Type": JsonResponseContentType.text_javascript,
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())

        self.requests = [request]


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_followers_of_user_private(mocked_sleep):
    result = collect_followers_of_user(MockedDriverPrivate(), "anasaiaofficial", 30)
    assert result == {"users": [], "count": 0}
