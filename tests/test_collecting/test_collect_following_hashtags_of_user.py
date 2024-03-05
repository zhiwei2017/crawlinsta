import json
import pytest
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting import INSTAGRAM_DOMAIN, API_VERSION, FOLLOWING_DOC_ID, GRAPHQL_QUERY_PATH, collect_following_hashtags_of_user


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
        with open("tests/resources/followings/web_profile_info.json", "r") as file:
            data = json.load(file)
        request = mock.Mock()
        request.url = url
        request.response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())

        self.requests = [request]

    def find_element(self, by, value):
        if self.call_find_element_number:
            variables = dict(id=self.user_id)
            query_dict = dict(doc_id=FOLLOWING_DOC_ID, variables=json.dumps(variables, separators=(',', ':')))
            url = f"{INSTAGRAM_DOMAIN}/{GRAPHQL_QUERY_PATH}/?{urlencode(query_dict, quote_via=quote)}"
            request = mock.Mock()
            request.url = url

            with open(f"tests/resources/following_hashtags/hashtags.json", "r") as file:
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
def test_collect_following_hashtags_of_user(mocked_sleep):
    result = collect_following_hashtags_of_user(MockedDriver(), "angibieneck", 200)
    with open("tests/resources/following_hashtags/result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


@pytest.mark.parametrize("n", [0, -1])
def test_collect_following_hashtags_of_user_fail(n):
    with pytest.raises(ValueError) as exc_info:
        collect_following_hashtags_of_user(MockedDriver(), "angibieneck", n)
    assert str(exc_info.value) == "The number of following hashtags to collect must be a positive integer."
