import json
import pytest
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting import INSTAGRAM_DOMAIN, API_VERSION, collect_followings_of_user
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def __init__(self):
        self.user_id = None
        self.call_find_element_number = 0
        super().__init__()

    def get(self, url):
        self.user_id = "1798450984"
        username = url.split("/")[-2]

        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={username}"
        with open("tests/resources/followings/web_profile_info.json", "r") as file:
            data = json.load(file)
        request = mock.Mock()
        request.url = url
        request.response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())

        self.requests = [request]

    def find_element(self, by, value):
        query_dict = dict(count=12)
        if self.call_find_element_number:
            query_dict["max_id"] = 12 * self.call_find_element_number
        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{self.user_id}/following/?{urlencode(query_dict, quote_via=quote)}"
        request = mock.Mock()
        request.url = url

        with open(f"tests/resources/followings/following{self.call_find_element_number + 1}.json", "r") as file:
            data = json.load(file)
        request.response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]
        self.call_find_element_number += 1
        return mock.Mock()


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_collect_followings_of_user(mocked_sleep):
    result = collect_followings_of_user(MockedDriver(), "marie_2_0", 30)
    with open("tests/resources/followings/result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


@pytest.mark.parametrize("n", [0, -1])
def test_collect_followings_of_user_fail(n):
    with pytest.raises(ValueError) as exc_info:
        collect_followings_of_user(MockedDriver(), "marie_2_0", n)
    assert str(exc_info.value) == "The number of following users to collect must be a positive integer."
