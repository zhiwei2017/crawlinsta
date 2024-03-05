import pytest
from crawlinsta.utils import filter_requests, search_request, get_json_data, get_media_type
from seleniumwire.request import Request, Response


def test_filter_requests_fail():
    with pytest.raises(ValueError, match="No requests to filter."):
        filter_requests([])


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


def test_search_request_empty_requests_fail():
    with pytest.raises(ValueError, match="No requests to search."):
        search_request([], request_url="http://dummy.com")


def test_search_request_not_found_fail():
    with pytest.raises(ValueError, match="No json response to the url 'http://dummy.com' found."):
        search_request([Request(method="GET", url="http://dummy.com", headers=[])],
                       request_url="http://dummy.com")


def test_search_request_success():
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

    requests = [request1, request2, request3, request4]

    result = search_request(requests, request_url="http://dummy.com/2/")

    assert result == 3


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
