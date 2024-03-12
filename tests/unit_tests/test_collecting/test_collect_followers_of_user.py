import json
import pytest
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting import INSTAGRAM_DOMAIN, API_VERSION, collect_followers_of_user


class MockedDriver:
    def __init__(self):
        self.requests = []
        self.user_id = None
        self.call_find_element_number = 0

    def implicitly_wait(self, seconds):
        pass

    def get(self, url):
        self.user_id = "1798450984"
        username = url.split("/")[-2]

        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={username}"
        with open("tests/resources/followers/web_profile_info.json", "r") as file:
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
        query_dict["search_surface"] = "follow_list_page"
        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{self.user_id}/followers/?{urlencode(query_dict, quote_via=quote)}"
        request = mock.Mock()
        request.url = url

        with open(f"tests/resources/followers/followers{self.call_find_element_number + 1}.json", "r") as file:
            data = json.load(file)
        request.response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]
        self.call_find_element_number += 1
        return mock.Mock()

    def execute(self, *args, **kwargs):
        pass


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
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