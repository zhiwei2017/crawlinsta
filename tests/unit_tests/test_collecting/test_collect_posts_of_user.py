import json
import pytest
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting import INSTAGRAM_DOMAIN, collect_posts_of_user
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def __init__(self):
        self.username = None
        self.call_find_element_number = 0
        super().__init__()

    def get(self, url):
        self.username = url.split("/")[-2]
        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        with open("tests/resources/posts/graphql1.json", "r") as file:
            data = json.load(file)
        request = mock.Mock()
        request.url = url
        request.body = urlencode(dict(av="17841461911219001", doc_id="7354141574647290", variables=json.dumps({"username": self.username}, separators=(',', ':'))),
                                 quote_via=quote).encode()
        request.response = mock.Mock(headers={"Content-Type": "text/javascript; charset=utf-8",
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]

    def find_element(self, by, value):
        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        if not self.call_find_element_number:
            data_file = "tests/resources/posts/graphql2.json"
            after = "3305036909188660917_50269116275"
        else:
            data_file = "tests/resources/posts/graphql3.json"
            after = "3294160102348327242_50269116275"
        with open(data_file, "r") as file:
            data = json.load(file)

        response = mock.Mock(headers={"Content-Type": "text/javascript; charset=utf-8",
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())

        request1 = mock.Mock(url=url, response=response)
        request1.body = urlencode(dict(av="17841461911219001", doc_id="7784658434954494",
                                       variables=json.dumps({"username": self.username, "after": after}, separators=(',', ':'))),
                                       quote_via=quote).encode()

        request2 = mock.Mock(url=url, response=response)
        request2.body = urlencode(dict(av="178414619", doc_id="7784658434954494",
                                       variables=json.dumps({"username": self.username, "after": after},
                                                            separators=(',', ':'))),
                                  quote_via=quote).encode()

        request3 = mock.Mock(url=url, response=response)
        request3.body = urlencode(dict(av="17841461911219001", doc_id="7784658434954494"),
                                  quote_via=quote).encode()

        request4 = mock.Mock(url=url, response=response)
        request4.body = urlencode(dict(av="17841461911219001", doc_id="7784658434954494",
                                       variables=json.dumps({"username": "dummy", "after": after},
                                                            separators=(',', ':'))),
                                  quote_via=quote).encode()

        request5 = mock.Mock(url=url, response=response)
        request5.body = urlencode(dict(av="17841461911219001", doc_id="7784658434954494",
                                       variables=json.dumps({"username": self.username, "after": "dummy"},
                                                            separators=(',', ':'))),
                                  quote_via=quote).encode()

        self.requests = [request2, request3, request4, request5, request1]
        self.call_find_element_number += 1
        return mock.Mock()


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_collect_posts_of_user(mocked_sleep):
    result = collect_posts_of_user(MockedDriver(), "anasaiaofficial", 30)
    with open("tests/resources/posts/result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


@pytest.mark.parametrize("n", [0, -1])
def test_collect_posts_of_user_fail(n):
    with pytest.raises(ValueError) as exc_info:
        collect_posts_of_user(MockedDriver(), "anasaiaofficial", n)
    assert str(exc_info.value) == "The number of posts to collect must be a positive integer."
