import json
import pytest
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting.collect_tagged_posts_of_user import collect_tagged_posts_of_user
from crawlinsta.constants import INSTAGRAM_DOMAIN, API_VERSION, JsonResponseContentType
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def __init__(self):
        self.user_id = None
        super().__init__()

    def get(self, url):
        self.user_id = "12804596"
        username = url.split("/")[-3]

        url1 = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={username}"
        with open("tests/resources/tagged_posts/web_profile_info.json", "r") as file:
            data1 = json.load(file)
        request1 = mock.Mock()
        request1.url = url1
        request1.response = mock.Mock(headers={"Content-Type": JsonResponseContentType.application_json,
                                               'Content-Encoding': 'identity'},
                                      body=json.dumps(data1).encode())

        url2 = f"{INSTAGRAM_DOMAIN}/api/graphql"
        with open("tests/resources/tagged_posts/graphql1.json", "r") as file:
            data2 = json.load(file)
        request2 = mock.Mock()
        request2.url = url2
        request2.body = urlencode(dict(av="17841461911219001", doc_id="7289408964443685", variables=json.dumps({"user_id": self.user_id}, separators=(',', ':'))),
                                  quote_via=quote).encode()
        request2.response = mock.Mock(headers={"Content-Type": JsonResponseContentType.text_javascript,
                                               'Content-Encoding': 'identity'},
                                      body=json.dumps(data2).encode())
        self.requests = [request1, request2]

    def find_element(self, by, value):
        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        data_file = "tests/resources/tagged_posts/graphql2.json"
        after = "1660590271798502213"
        with open(data_file, "r") as file:
            data = json.load(file)
        response = mock.Mock(headers={"Content-Type": JsonResponseContentType.text_javascript,
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())

        request1 = mock.Mock(url=url, response=response)
        request1.body = urlencode(dict(av="17841461911", doc_id="6933349160067627",
                                       variables=json.dumps({"user_id": self.user_id, "after": after},
                                                            separators=(',', ':'))),
                                  quote_via=quote).encode()

        request2 = mock.Mock(url=url, response=response)
        request2.body = urlencode(dict(av="17841461911219001", doc_id="6933349160067627"),
                                  quote_via=quote).encode()

        request3 = mock.Mock(url=url, response=response)
        request3.body = urlencode(dict(av="17841461911219001", doc_id="6933349160067627",
                                       variables=json.dumps({"user_id": "dummy", "after": after},
                                                            separators=(',', ':'))),
                                  quote_via=quote).encode()

        request4 = mock.Mock(url=url, response=response)
        request4.body = urlencode(dict(av="17841461911219001", doc_id="6933349160067627",
                                       variables=json.dumps({"user_id": self.user_id, "after": "after"},
                                                            separators=(',', ':'))),
                                  quote_via=quote).encode()

        request = mock.Mock(url=url, response=response)
        request.body = urlencode(dict(av="17841461911219001", doc_id="6933349160067627",
                                      variables=json.dumps({"user_id": self.user_id, "after": after}, separators=(',', ':'))),
                                 quote_via=quote).encode()

        self.requests = [request1, request2, request3, request4, request]
        return mock.Mock()


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_tagged_posts_of_user(mocked_sleep):
    result = collect_tagged_posts_of_user(MockedDriver(), "onesmileymonkey", 20)
    with open("tests/resources/tagged_posts/result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


def test_collect_tagged_posts_of_user_fail():
    with pytest.raises(ValueError) as exc_info:
        collect_tagged_posts_of_user(MockedDriver(), "anasaiaofficial", -1)
    assert str(exc_info.value) == "The number of tagged posts to collect must be a positive integer."


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_tagged_posts_of_user_no_request(mocked_sleep):
    with pytest.raises(ValueError) as exc_info:
        collect_tagged_posts_of_user(BaseMockedDriver(), "anasaiaofficial")
    assert str(exc_info.value) == "User 'anasaiaofficial' not found."


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
@mock.patch("crawlinsta.collecting.base.CollectPostsBase.extract_data", return_value=False)
@mock.patch("crawlinsta.collecting.base.logger")
def test_collect_tagged_posts_of_user_no_posts(mocked_logger, mocked_extract_data, mocked_sleep):
    result = collect_tagged_posts_of_user(MockedDriver(), "anasaiaofficial", 30)
    assert result == {"posts": [], "count": 0}
    mocked_logger.warning.assert_called_once_with("No tagged posts found for user 'anasaiaofficial'.")
