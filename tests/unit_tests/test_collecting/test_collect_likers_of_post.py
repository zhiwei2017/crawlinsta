import json
import pytest
from unittest import mock
from crawlinsta.collecting import INSTAGRAM_DOMAIN, API_VERSION, collect_likers_of_post


class MockedDriver:
    def __init__(self, post_id="3283079976352304185",
                 data_file="tests/resources/likers/likers.json"):
        self.requests = []
        self.call_find_element_number = 0
        self.post_id = post_id
        self.data_file = data_file

    def implicitly_wait(self, seconds):
        pass

    def get(self, url):
        pass

    def find_element(self, by, value):
        mocked_element = mock.Mock()
        if not self.call_find_element_number:
            mocked_element.get_attribute = mock.Mock(return_value=self.post_id)
        else:
            url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/media/{self.post_id}/likers/"
            with open(self.data_file, "r") as file:
                data = json.load(file)
            response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                          'Content-Encoding': 'identity'},
                                 body=json.dumps(data).encode())
            request = mock.Mock(url=url, response=response)
            self.requests = [request]
        self.call_find_element_number += 1
        return mocked_element

    def execute(self, *args, **kwargs):
        pass


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_collect_likers_of_post_success(mocked_sleep):
    result = collect_likers_of_post(MockedDriver(), "C2P19gPrUw5", 100)
    with open("tests/resources/likers/result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


class MockedDriverFail:
    def __init__(self):
        self.requests = []

    def implicitly_wait(self, seconds):
        pass

    def get(self, url):
        pass

    def find_element(self, by, value):
        mocked_element = mock.Mock(get_attribute=mock.Mock(return_value=""))
        return mocked_element

    def execute(self, *args, **kwargs):
        pass


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_collect_likers_of_post_fail(mocked_sleep):
    result = collect_likers_of_post(MockedDriverFail(), "C2P19gPrUw5", 100)
    assert result == {"likers": [], "count": 0}


@pytest.mark.parametrize("n", [0, -1])
def test_collect_likers_of_post_fail_on_wrong_n(n):
    with pytest.raises(ValueError) as exc:
        collect_likers_of_post(MockedDriver(), "C2P19gPrUw5", n)
    assert str(exc.value) == "The number of likers to collect must be a positive integer."
