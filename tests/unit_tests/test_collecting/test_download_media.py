import os
import pytest
import shutil
import tempfile
from unittest import mock
from crawlinsta.collecting import download_media
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def get(self, url):
        request = mock.Mock(url=url)
        with open("tests/resources/download_media/image.jpg", "rb") as file:
            request.response = mock.Mock(headers={"Content-Type": "image/jpeg"},
                                         body=file.read())
        self.requests = [request]


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_download_media(mocked_sleep):
    driver = MockedDriver()
    tmp_dir = tempfile.mkdtemp()
    tmp_filename = os.path.join(tmp_dir, "image")
    download_media(driver, "https://dummy.image.com", tmp_filename)
    with open("tests/resources/download_media/image.jpg", "rb") as file1:
        with open(f"{tmp_filename}.jpeg", "rb") as file2:
            assert file1.read() == file2.read()
    shutil.rmtree(tmp_dir)


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
@mock.patch("crawlinsta.collecting.search_request", return_value=None)
def test_download_media_fail(mocked_search_request, mocked_sleep):
    driver = MockedDriver()
    with pytest.raises(ValueError) as exc:
        download_media(driver, "https://dummy.image.com", "dummy_filename")
    assert str(exc.value) == "Media url 'https://dummy.image.com' not found."
