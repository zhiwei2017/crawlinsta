import pytest
from crawlinsta.utils import (
    filter_requests, search_request, get_json_data, get_media_type,
    get_user_data, find_brackets
)
from crawlinsta.constants import JsonResponseContentType, INSTAGRAM_DOMAIN, API_VERSION
from seleniumwire.request import Request, Response
from unittest import mock


@mock.patch("crawlinsta.utils.logger", autospec=True)
def test_filter_requests_empty_requests(mocked_logger):
    result = filter_requests([])
    assert result == []
    mocked_logger.error.assert_called_once_with("No requests to filter.")


def test_filter_requests_success():
    request1 = Request(method="GET", url="http://dummy.com", headers=[])
    response1 = Response(status_code=200, reason="ok", headers=[('Content-Type',
                                                                 "application/xform; charset=utf-8")])
    request2 = Request(method="GET", url="http://dummy.com", headers=[])
    request2.response = response1

    response2 = Response(status_code=200, reason="ok", headers=[('Content-Type',
                                                                 "application/json; charset=utf-8")])
    request3 = Request(method="GET", url="http://dummy.com", headers=[])
    request3.response = response2
    requests = [request1, request2, request3]

    result = filter_requests(requests)

    assert len(result) == 1
    assert result[0] == request3


@mock.patch("crawlinsta.utils.logger", autospec=True)
def test_search_request_empty_requests(mocked_logger):
    result = search_request([], request_url="http://dummy.com")
    assert result is None
    mocked_logger.error.assert_called_once_with("No requests to search.")


@mock.patch("crawlinsta.utils.logger", autospec=True)
def test_search_request_not_found_fail(mocked_logger):
    result = search_request([Request(method="GET", url="http://dummy.com", headers=[])],
                   request_url="http://dummy.com")
    assert result is None
    mocked_logger.error.assert_called_once_with("No response with content-type [application/json; charset=utf-8] to the url 'http://dummy.com' found.")


def test_search_request_success():
    def check_request_header(request, header):
        return header in request.headers
    request1 = Request(method="GET", url="http://dummy.com", headers=[])

    request2 = Request(method="GET", url="http://dummy.com/2/", headers=[])

    response1 = Response(status_code=200, reason="ok", headers=[('Content-Type',
                                                                 "application/xform; charset=utf-8")])
    request3 = Request(method="GET", url="http://dummy.com/2/", headers=[])
    request3.response = response1

    response2 = Response(status_code=200, reason="ok", headers=[('Content-Type',
                                                                 "application/json; charset=utf-8")])
    request4 = Request(method="GET", url="http://dummy.com/2/", headers=[])
    request4.response = response2

    response3 = Response(status_code=200, reason="ok", headers=[])
    request5 = Request(method="GET", url="http://dummy.com/2/", headers=[])
    request5.response = response3

    response4 = Response(status_code=200, reason="ok", headers=[('Content-Type',
                                                                 "application/json; charset=utf-8")])
    request6 = Request(method="GET", url="http://dummy.com/2/", headers=[('Content-Type',
                                                                 "application/json; charset=utf-8")])
    request6.response = response4

    requests = [request1, request2, request3, request4, request5, request6]

    result = search_request(requests, "http://dummy.com/2/", JsonResponseContentType.application_json, check_request_header, "Content-Type")

    assert result == 5


def test_get_json_data():
    response = Response(status_code=200, reason="ok",
                        headers=[('Content-Type', "application/json; charset=utf-8"),
                                 ('Content-Encoding', "identity")],
                        body=b'{"key": "value"}')
    result = get_json_data(response)
    assert result == {"key": "value"}


def test_get_media_type_fail():
    with pytest.raises(ValueError, match="Invalid media_type"):
        get_media_type(3, "feed")

    with pytest.raises(ValueError, match="Invalid product_type"):
        get_media_type(2, "dummy")


def test_get_media_type_success():
    result = get_media_type(1, "image")
    assert result == "Photo"

    result = get_media_type(2, "feed")
    assert result == "Video"

    result = get_media_type(2, "igtv")
    assert result == "IGTV"

    result = get_media_type(2, "clips")
    assert result == "Reel"

    result = get_media_type(8, "album")
    assert result == "Album"


def test_get_user_data():
    url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username=1234"
    request1 = Request(method="GET", url=f"{url}/2/", headers=[])

    request2 = Request(method="GET", url=url, headers=[])

    response3 = Response(status_code=200, reason="ok", headers=[('Content-Type',
                                                                 "application/xform; charset=utf-8")])
    request3 = Request(method="GET", url=url, headers=[])
    request3.response = response3

    response4 = Response(status_code=200, reason="ok", headers=[('Content-Type',
                                                                 "application/json; charset=utf-8")],
                         body=b'{"data": {"user": "dummy"}}')
    request4 = Request(method="GET", url=url, headers=[])
    request4.response = response4

    response5 = Response(status_code=200, reason="ok", headers=[])
    request5 = Request(method="GET", url=url, headers=[])
    request5.response = response5

    requests = [request1, request2, request3, request4, request5]

    result = get_user_data(requests, "1234")

    assert result == "dummy"


def test_find_brackets():
    result = find_brackets("{{{{}}}}")
    assert result == [(3, 4), (2, 5), (1, 6), (0, 7)]

    result = find_brackets("{{{{}}}}}{}")
    assert result == [(3, 4), (2, 5), (1, 6), (0, 7)]
