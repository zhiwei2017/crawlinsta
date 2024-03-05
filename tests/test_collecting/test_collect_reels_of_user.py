import json
import pytest
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting import INSTAGRAM_DOMAIN, API_VERSION, collect_reels_of_user


class MockedDriver:
    def __init__(self):
        self.requests = []
        self.user_id = None

    def implicitly_wait(self, seconds):
        pass

    def get(self, url):
        self.user_id = "50269116275"
        username = url.split("/")[-3]

        url1 = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={username}"
        with open("tests/resources/reels/web_profile_info.json", "r") as file:
            data1 = json.load(file)
        request1 = mock.Mock()
        request1.url = url1
        request1.response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                               'Content-Encoding': 'identity'},
                                      body=json.dumps(data1).encode())

        url2 = f"{INSTAGRAM_DOMAIN}/api/graphql"
        with open("tests/resources/reels/graphql1.json", "r") as file:
            data2 = json.load(file)
        request2 = mock.Mock()
        request2.url = url2
        request2.body = urlencode(dict(av="17841461911219001", doc_id="7191572580905225", variables=json.dumps({"data": {"target_user_id": self.user_id}}, separators=(',', ':'))),
                                  quote_via=quote).encode()
        request2.response = mock.Mock(headers={"Content-Type": "text/javascript; charset=utf-8",
                                               'Content-Encoding': 'identity'},
                                      body=json.dumps(data2).encode())
        self.requests = [request1, request2]

    def find_element(self, by, value):
        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        request = mock.Mock()
        request.url = url
        data_file = "tests/resources/reels/graphql2.json"
        after = "QVFCU1EwZjBPaDVQQ0U1ZHNvYnByell3YkJMYkJRLUdUR3FlazVXbGlXRnlVOHhFcTRsWGtuZU1nTjZYRXZzM2FCM042MFNmT2hRcDQ2a0lIU25KT1J0cA=="

        request.body = urlencode(dict(av="17841461911219001", doc_id="7631884496822310",
                                      variables=json.dumps({"data": {"target_user_id": self.user_id}, "after": after}, separators=(',', ':'))),
                                 quote_via=quote).encode()

        with open(data_file, "r") as file:
            data = json.load(file)
        request.response = mock.Mock(headers={"Content-Type": "text/javascript; charset=utf-8",
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]
        return mock.Mock()

    def execute(self, *args, **kwargs):
        pass


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_collect_reels_of_user(mocked_sleep):
    result = collect_reels_of_user(MockedDriver(), "anasaiaofficial", 20)
    with open("tests/resources/reels/result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


def test_collect_reels_of_user_fail():
    with pytest.raises(ValueError) as exc_info:
        collect_reels_of_user(MockedDriver(), "anasaiaofficial", -1)
    assert str(exc_info.value) == "The number of reels to collect must be a positive integer."
