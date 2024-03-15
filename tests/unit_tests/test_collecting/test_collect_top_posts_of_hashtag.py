import json
from unittest import mock
from crawlinsta.collecting import INSTAGRAM_DOMAIN, API_VERSION, collect_top_posts_of_hashtag
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def __init__(self, response_content_type="application/json; charset=utf-8",
                 data_file="tests/resources/top_posts_of_hashtag/top_posts_of_hashtag.json"):
        self.response_content_type = response_content_type
        self.data_file = data_file
        super().__init__()

    def get(self, url):
        hashtag = url.split("/")[-1]
        url = f'{INSTAGRAM_DOMAIN}/{API_VERSION}/tags/web_info/?tag_name={hashtag}'
        with open(self.data_file, "r") as file:
            data = json.load(file)
        response = mock.Mock(headers={"Content-Type": self.response_content_type,
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())
        request = mock.Mock(url=url, response=response)
        self.requests = [request]


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_collect_top_posts_of_hashtag(mocked_sleep):
    result = collect_top_posts_of_hashtag(MockedDriver(), "asiangames2023")
    with open("tests/resources/top_posts_of_hashtag/result.json", "r") as file:
        expected = json.load(file)
    assert result == expected
