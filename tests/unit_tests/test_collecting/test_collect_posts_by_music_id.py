import json
import pytest
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting.posts_by_music_id import collect_posts_by_music_id
from crawlinsta.constants import INSTAGRAM_DOMAIN, API_VERSION, JsonResponseContentType
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def __init__(self, data_files, max_id):
        self.music_id = None
        self.data_files = data_files
        self.max_id = max_id
        super().__init__()

    def get(self, url):
        self.music_id = url.split("/")[-2]

        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/clips/music/"
        body = urlencode(dict(audio_cluster_id=self.music_id), quote_via=quote).encode()
        with open(self.data_files[0], "r") as file:
            data = json.load(file)
        response = mock.Mock(headers={"Content-Type": JsonResponseContentType.application_json,
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())
        request = mock.Mock(url=url, body=body, response=response)
        self.requests = [request]

    def execute_script(self, value):
        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/clips/music/"

        body = urlencode(dict(audio_cluster_id=self.music_id, max_id=self.max_id),
                         quote_via=quote).encode()
        with open(self.data_files[1], "r") as file:
            data = json.load(file)
        response = mock.Mock(headers={"Content-Type": JsonResponseContentType.application_json,
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())

        request = mock.Mock(url=url, body=body, response=response)

        body1 = urlencode(dict(audio_cluster_id="music_id", max_id=self.max_id),
                          quote_via=quote).encode()
        request1 = mock.Mock(url=url, body=body1, response=response)

        request2 = mock.Mock(url=url, body=mock.MagicMock(), response=response)
        self.requests = [request2, request1, request]
        return mock.Mock()


@pytest.mark.parametrize("data_files, max_id, result_file, music_id",
                         [(["tests/resources/posts_by_music_id/music1.json", "tests/resources/posts_by_music_id/music2.json"],
                           "Grb-yYqzpqONu1uUrLfb5-CBvlvW98aSzq_261vY2J6Dovf64VuY-af7kuyV4lvWz7KLsNvl0Fua8ZLane6_5Fuo35rDm7SG9Fvql5LT2YGyu1vq9pnCoKDbvlvu28Lq4oT47VsmgMKUlsBjFBY0AikIGAAaCDoGGQwA",
                           "tests/resources/posts_by_music_id/music_result.json",
                           "1053780911670375"),
                          (["tests/resources/posts_by_music_id/audio1.json", "tests/resources/posts_by_music_id/audio2.json"],
                           "GsauteCL34_Dm1yGhce0nbnTjVzKjr2L-MOnk1zUgpmq7cy9lVzWl7K66LOEllzYtqbD-MXgmlyavdXzsc2LmVykwunLgt6TmFyu2NXjmbWhmFy0zI_z9aS0jFy6_bSr1u7Li1y88cDbh4HEhlwm4pLD1cdjFBg0AikIGAAaCDoGGQwA",
                           "tests/resources/posts_by_music_id/audio_result.json",
                           "955300842838255")])
@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_posts_by_music_id(mocked_sleep, data_files, max_id, result_file, music_id):
    result = collect_posts_by_music_id(MockedDriver(data_files, max_id), music_id, 20)
    with open(result_file, "r") as file:
        expected = json.load(file)
    assert result == expected


@pytest.mark.parametrize("n", [0, -1])
def test_collect_posts_by_music_id_fail(n):
    with pytest.raises(ValueError) as exc:
        collect_posts_by_music_id(MockedDriver(["tests/resources/posts_by_music_id/music1.json", "tests/resources/posts_by_music_id/music2.json"],
                                               "Grb-yYqzpqONu1uUrLfb5-CBvlvW98aSzq_261vY2J6Dovf64VuY-af7kuyV4lvWz7KLsNvl0Fua8ZLane6_5Fuo35rDm7SG9Fvql5LT2YGyu1vq9pnCoKDbvlvu28Lq4oT47VsmgMKUlsBjFBY0AikIGAAaCDoGGQwA"), "1053780911670375", n)
    assert str(exc.value) == "The number of posts to collect must be a positive integer."


@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
def test_collect_posts_by_music_id_fail_no_request(mocked_sleep):
    with pytest.raises(ValueError) as exc:
        collect_posts_by_music_id(BaseMockedDriver(), "1053780911670375", 20)
    assert str(exc.value) == "Music id '1053780911670375' not found."



@pytest.mark.parametrize("data_files, max_id, result_file, music_id",
                         [(["tests/resources/posts_by_music_id/music1.json", "tests/resources/posts_by_music_id/music2.json"],
                           "Grb-yYqzpqONu1uUrLfb5-CBvlvW98aSzq_261vY2J6Dovf64VuY-af7kuyV4lvWz7KLsNvl0Fua8ZLane6_5Fuo35rDm7SG9Fvql5LT2YGyu1vq9pnCoKDbvlvu28Lq4oT47VsmgMKUlsBjFBY0AikIGAAaCDoGGQwA",
                           "tests/resources/posts_by_music_id/music_result.json",
                           "1053780911670375")])
@mock.patch("crawlinsta.collecting.base.time.sleep", return_value=None)
@mock.patch("crawlinsta.collecting.posts_by_music_id.search_request", return_value=None)
@mock.patch("crawlinsta.collecting.posts_by_music_id.logger")
def test_collect_posts_by_music_id_no_data(mocked_logger, mocked_search_requests, mocked_sleep, data_files, max_id, result_file, music_id):
    result = collect_posts_by_music_id(MockedDriver(data_files, max_id), music_id, 20)
    assert result == {'count': 0,
                      'music': {'artist': None,
                                'clips_count': 0,
                                'duration_in_ms': None,
                                'id': '1053780911670375',
                                'is_trending_in_clips': False,
                                'photos_count': 0,
                                'title': 'Original audio',
                                'url': None},
                      'posts': []}
    mocked_logger.warning.assert_called_once_with("No data found for music id '1053780911670375'.")
