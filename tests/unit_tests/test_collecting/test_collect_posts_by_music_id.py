import json
import pytest
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting import INSTAGRAM_DOMAIN, API_VERSION, collect_posts_by_music_id


class MockedDriver:
    def __init__(self):
        self.requests = []
        self.music_id = None

    def implicitly_wait(self, seconds):
        pass

    def get(self, url):
        self.music_id = url.split("/")[-2]

        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/clips/music/"
        with open("tests/resources/posts_by_music_id/music1.json", "r") as file:
            data = json.load(file)
        request = mock.Mock()
        request.url = url
        request.body = urlencode(dict(audio_cluster_id=self.music_id),
                                 quote_via=quote).encode()
        request.response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]

    def find_element(self, by, value):
        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/clips/music/"
        request = mock.Mock()
        request.url = url
        data_file = "tests/resources/posts_by_music_id/music2.json"
        max_id = "Grb-yYqzpqONu1uUrLfb5-CBvlvW98aSzq_261vY2J6Dovf64VuY-af7kuyV4lvWz7KLsNvl0Fua8ZLane6_5Fuo35rDm7SG9Fvql5LT2YGyu1vq9pnCoKDbvlvu28Lq4oT47VsmgMKUlsBjFBY0AikIGAAaCDoGGQwA"

        request.body = urlencode(dict(audio_cluster_id=self.music_id, max_id=max_id),
                                 quote_via=quote).encode()

        with open(data_file, "r") as file:
            data = json.load(file)
        request.response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]
        return mock.Mock()

    def execute(self, *args, **kwargs):
        pass


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_collect_posts_by_music_id(mocked_sleep):
    result = collect_posts_by_music_id(MockedDriver(), "1053780911670375", 20)
    with open("tests/resources/posts_by_music_id/result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


@pytest.mark.parametrize("n", [0, -1])
def test_collect_posts_by_music_id_fail(n):
    with pytest.raises(ValueError) as exc:
        collect_posts_by_music_id(MockedDriver(), "1053780911670375", n)
    assert str(exc.value) == "The number of posts to collect must be a positive integer."
