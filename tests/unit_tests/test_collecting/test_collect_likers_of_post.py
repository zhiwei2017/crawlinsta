import json
import pytest
from unittest import mock
from crawlinsta.collecting.collect_likers_of_post import collect_likers_of_post
from crawlinsta.constants import INSTAGRAM_DOMAIN, API_VERSION, JsonResponseContentType
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def __init__(self, post_id="3283079976352304185",
                 data_file="tests/resources/likers/likers.json"):
        self.call_find_element_number = 0
        self.post_id = post_id
        self.data_file = data_file
        super().__init__()

    def find_element(self, by, value):
        mocked_element = mock.Mock()
        if not self.call_find_element_number:
            mocked_element.get_attribute = mock.Mock(return_value=self.post_id)
        else:
            url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/media/{self.post_id}/likers/"
            with open(self.data_file, "r") as file:
                data = json.load(file)
            response = mock.Mock(headers={"Content-Type": JsonResponseContentType.application_json,
                                          'Content-Encoding': 'identity'},
                                 body=json.dumps(data).encode())
            request = mock.Mock(url=url, response=response)
            self.requests = [request]
        self.call_find_element_number += 1
        return mocked_element


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_likers_of_post_success(mocked_sleep):
    result = collect_likers_of_post(MockedDriver(), "C2P19gPrUw5", 100)
    with open("tests/resources/likers/result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


class MockedDriverFail(BaseMockedDriver):
    def find_element(self, by, value):
        mocked_element = mock.Mock(get_attribute=mock.Mock(return_value=""))
        return mocked_element


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_likers_of_post_fail(mocked_sleep):
    result = collect_likers_of_post(MockedDriverFail(), "C2P19gPrUw5", 100)
    assert result == {"users": [], "count": 0}


@pytest.mark.parametrize("n", [0, -1])
def test_collect_likers_of_post_fail_on_wrong_n(n):
    with pytest.raises(ValueError) as exc:
        collect_likers_of_post(MockedDriver(), "C2P19gPrUw5", n)
    assert str(exc.value) == "The number of likers to collect must be a positive integer."


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
@mock.patch("crawlinsta.collecting.collect_likers_of_post.search_request", return_value=None)
@mock.patch("crawlinsta.collecting.collect_likers_of_post.logger")
def test_collect_likers_of_post_no_likers(mocked_logger, mocked_search_request, mocked_sleep):
    result = collect_likers_of_post(MockedDriver(), "C2P19gPrUw5", 30)
    assert result == {"users": [], "count": 0}
    mocked_logger.warning.assert_called_once_with("No likers found for post 'C2P19gPrUw5'.")
