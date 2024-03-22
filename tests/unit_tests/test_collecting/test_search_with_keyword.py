import json
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting.search_with_keyword import search_with_keyword
from crawlinsta.constants import INSTAGRAM_DOMAIN, JsonResponseContentType
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def __init__(self, keyword):
        self.call_find_element_number = 0
        self.keyword = keyword
        super().__init__()

    def find_element(self, by, value):
        if not self.call_find_element_number:
            self.call_find_element_number += 1
            return mock.Mock()
        url = f"{INSTAGRAM_DOMAIN}/api/graphql"

        if self.call_find_element_number == 1:
            body = urlencode(dict(variables=json.dumps({"data": {"query": self.keyword}}, separators=(',', ':'))),
                             quote_via=quote).encode()
            body2 = urlencode(dict(variables=json.dumps({"data": {"query": "keyword"}}, separators=(',', ':'))),
                              quote_via=quote).encode()
            data_file = "tests/resources/search_with_keyword/personalised.json"
        else:
            body = urlencode(dict(variables=json.dumps({"query": self.keyword}, separators=(',', ':'))),
                             quote_via=quote).encode()
            body2 = urlencode(dict(variables=json.dumps({"query": "keyword"}, separators=(',', ':'))),
                              quote_via=quote).encode()
            data_file = "tests/resources/search_with_keyword/not_personalised.json"

        with open(data_file, "r") as file:
            data = json.load(file)

        response = mock.Mock(headers={"Content-Type": JsonResponseContentType.text_javascript,
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())
        request = mock.Mock(url=url, body=body, response=response)

        request1 = mock.Mock(url=url, body=mock.MagicMock(), response=response)
        request2 = mock.Mock(url=url, body=body2, response=response)
        self.requests = [request1, request2, request]
        self.call_find_element_number += 1
        return mock.Mock()


@mock.patch("crawlinsta.collecting.search_with_keyword.time.sleep", return_value=None)
def test_search_with_keyword_pers(mocked_sleep):
    keyword = "shanghai"
    driver = MockedDriver(keyword=keyword)
    result = search_with_keyword(driver, keyword, pers=True)
    with open("tests/resources/search_with_keyword/personalised_result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


@mock.patch("crawlinsta.collecting.search_with_keyword.time.sleep", return_value=None)
def test_search_with_keyword_not_pers(mocked_sleep):
    keyword = "shanghai"
    driver = MockedDriver(keyword=keyword)
    result = search_with_keyword(driver, keyword, pers=False)
    with open("tests/resources/search_with_keyword/not_personalised_result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


@mock.patch("crawlinsta.collecting.search_with_keyword.time.sleep", return_value=None)
@mock.patch("crawlinsta.collecting.search_with_keyword.search_request", return_value=None)
@mock.patch("crawlinsta.collecting.search_with_keyword.logger")
def test_search_with_keyword_pers_no_request_found(mocked_logger, mocked_search_request, mocked_sleep):
    keyword = "shanghai"
    driver = MockedDriver(keyword=keyword)
    result = search_with_keyword(driver, keyword, pers=True)
    assert result == {"hashtags": [], "places": [], "users": [], "personalised": True}
    mocked_logger.warning.assert_called_once_with("No search results found for keyword 'shanghai'.")
