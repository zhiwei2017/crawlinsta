import json
import pytest
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting.user_info import collect_user_info
from crawlinsta.constants import (
    INSTAGRAM_DOMAIN, API_VERSION, GRAPHQL_QUERY_PATH, JsonResponseContentType
)
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def get(self, url):
        username = url.split("/")[-2]
        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        with open("tests/resources/user_info/web_profile_info.json", "r") as file:
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
        url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?doc_id=17901966028246171&variables=%7B%22id%22%3A%22528817151%22%7D"
        with open("tests/resources/user_info/query.json", "r") as file:
            data = json.load(file)
        request = mock.Mock()
        request.url = url
        request.response = mock.Mock(headers={"Content-Type": JsonResponseContentType.application_json,
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]
        return mock.Mock()


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_user_info(mocked_sleep):
    result = collect_user_info(MockedDriver(), "nasa")
    assert result == {
        'id': '528817151',
        "username": "nasa",
        "fullname": "NASA",
        "biography": "🚀 🌎  Exploring the universe and our home planet. Verification: nasa.gov/socialmedia",
        'follower_count': 97956738,
        'following_count': 77,
        'following_tag_count': 10,
        "is_private": False,
        "is_verified": True,
        "profile_pic_url": 'https://scontent-muc2-1.cdninstagram.com/v/t51.2885-19/29090066_159271188110124_1152068159029641216_n.jpg?stp=dst-jpg_s150x150&_nc_ht=scontent-muc2-1.cdninstagram.com&_nc_cat=1&_nc_ohc=QR8vCKU7rFgAX-lnMuu&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfC3ixsrquc_5TCJtVEtyC3hGx2rL8bLgprss4AV7rw1Mg&oe=65E1C329&_nc_sid=8b3546',
        'post_count': 4116,
    }


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_user_info_fail(mocked_sleep):
    with pytest.raises(ValueError, match="User 'nasa' not found.") as exc:
        collect_user_info(BaseMockedDriver(), "nasa")


class MockedDriverPrivate(BaseMockedDriver):
    def get(self, url):
        username = url.split("/")[-2]
        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        with open("tests/resources/user_info/web_profile_info.json", "r") as file:
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

    def find_element(self, by, value):
        url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?doc_id=17901966028246171&variables=%7B%22id%22%3A%22528817151%22%7D"
        with open("tests/resources/user_info/query.json", "r") as file:
            data = json.load(file)
        request = mock.Mock()
        request.url = url
        request.response = mock.Mock(headers={"Content-Type": JsonResponseContentType.application_json,
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]
        return mock.Mock()


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_user_info_private(mocked_sleep):
    result = collect_user_info(MockedDriverPrivate(), "nasa")
    assert result == {
        'id': '528817151',
        "username": "nasa",
        "fullname": "NASA",
        "biography": "🚀 🌎  Exploring the universe and our home planet. Verification: nasa.gov/socialmedia",
        'follower_count': 97956738,
        'following_count': 77,
        'following_tag_count': 0,
        "is_private": True,
        "is_verified": True,
        "profile_pic_url": 'https://scontent-muc2-1.cdninstagram.com/v/t51.2885-19/29090066_159271188110124_1152068159029641216_n.jpg?stp=dst-jpg_s150x150&_nc_ht=scontent-muc2-1.cdninstagram.com&_nc_cat=1&_nc_ohc=QR8vCKU7rFgAX-lnMuu&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfC3ixsrquc_5TCJtVEtyC3hGx2rL8bLgprss4AV7rw1Mg&oe=65E1C329&_nc_sid=8b3546',
        'post_count': 4116,
    }


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
@mock.patch("crawlinsta.collecting.user_info.logger")
@mock.patch("crawlinsta.collecting.user_info.search_request", return_value=None)
def test_collect_user_info_private_1(mocked_search_request, mocked_logger, mocked_sleep):
    result = collect_user_info(MockedDriver(), "nasa")
    assert result == {
        'id': '528817151',
        "username": "nasa",
        "fullname": "NASA",
        "biography": "🚀 🌎  Exploring the universe and our home planet. Verification: nasa.gov/socialmedia",
        'follower_count': 97956738,
        'following_count': 77,
        'following_tag_count': 0,
        "is_private": False,
        "is_verified": True,
        "profile_pic_url": 'https://scontent-muc2-1.cdninstagram.com/v/t51.2885-19/29090066_159271188110124_1152068159029641216_n.jpg?stp=dst-jpg_s150x150&_nc_ht=scontent-muc2-1.cdninstagram.com&_nc_cat=1&_nc_ohc=QR8vCKU7rFgAX-lnMuu&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfC3ixsrquc_5TCJtVEtyC3hGx2rL8bLgprss4AV7rw1Mg&oe=65E1C329&_nc_sid=8b3546',
        'post_count': 4116,
    }
    mocked_logger.warning.assert_called_once_with("Following hashtags number not found for user 'nasa'.")
