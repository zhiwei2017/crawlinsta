import json
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting import INSTAGRAM_DOMAIN, search_with_keyword


class MockedDriver:
    def __init__(self, keyword):
        self.requests = []
        self.call_find_element_number = 0
        self.keyword = keyword

    def implicitly_wait(self, seconds):
        pass

    def get(self, url):
        pass

    def find_element(self, by, value):
        if not self.call_find_element_number:
            self.call_find_element_number += 1
            return mock.Mock()
        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        request = mock.Mock(url=url)
        if self.call_find_element_number == 1:
            request.body = urlencode(dict(variables=json.dumps({"data": {"query": self.keyword}}, separators=(',', ':'))),
                                     quote_via=quote).encode()
            data_file = "tests/resources/search_with_keyword/personalised.json"
        else:
            request.body = urlencode(dict(variables=json.dumps({"query": self.keyword}, separators=(',', ':'))),
                                     quote_via=quote).encode()
            data_file = "tests/resources/search_with_keyword/not_personalised.json"

        with open(data_file, "r") as file:
            data = json.load(file)
        request.response = mock.Mock(headers={"Content-Type": "text/javascript; charset=utf-8",
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]
        self.call_find_element_number += 1
        return mock.Mock()

    def execute(self, *args, **kwargs):
        pass


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_search_with_keyword_pers(mocked_sleep):
    keyword = "shanghai"
    driver = MockedDriver(keyword=keyword)
    result = search_with_keyword(driver, keyword, pers=True)
    with open("tests/resources/search_with_keyword/personalised_result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_search_with_keyword_not_pers(mocked_sleep):
    keyword = "shanghai"
    driver = MockedDriver(keyword=keyword)
    result = search_with_keyword(driver, keyword, pers=False)
    with open("tests/resources/search_with_keyword/not_personalised_result.json", "r") as file:
        expected = json.load(file)
    assert result == expected
