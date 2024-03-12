import json
import pytest
from lxml import html
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting import INSTAGRAM_DOMAIN, JsonResponseContentType, collect_comments_of_post


class MockedDriverCached:
    def __init__(self, post_id="3275298868401088037"):
        self.requests = []
        self.call_find_element_number = 0
        self.post_id = post_id

    def implicitly_wait(self, seconds):
        pass

    def get(self, url):
        pass

    def find_elements(self, by, value):
        if not self.call_find_element_number:
            scripts = []
            with open("tests/resources/comments/C10MvewSSYl.html", "r") as file:
                content = html.fromstring(file.read())
            script_elements = content.xpath('//script[@type="application/json"]')
            for script_element in script_elements:
                script = mock.Mock(get_attribute=mock.Mock(return_value=script_element.text_content()))
                scripts.append(script)
            self.call_find_element_number += 1
            return scripts
        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        with open(f"tests/resources/comments/comments_cached{self.call_find_element_number}.json", "r") as file:
            data = json.load(file)
        response = mock.Mock(headers={"Content-Type": JsonResponseContentType.text_javascript,
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())
        request = mock.Mock(url=url, response=response)
        request.body = urlencode(dict(av="17841461911219001", doc_id="6974885689225067",
                                      variables=json.dumps({"media_id": self.post_id},
                                                           separators=(',', ':'))),
                                 quote_via=quote).encode()
        self.requests = [request]
        self.call_find_element_number += 1
        return [mock.Mock()]

    def find_element(self, by, value):
        mocked_element = mock.Mock()
        mocked_element.get_attribute = mock.Mock(return_value=self.post_id)
        return mocked_element

    def execute(self, *args, **kwargs):
        pass


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
@mock.patch("crawlinsta.collecting.ActionChains", return_value=mock.MagicMock())
def test_collect_comments_of_post_success_cached(mocked_action_chains, mocked_sleep):
    result = collect_comments_of_post(MockedDriverCached(), "C10MvewSSYl", 100)
    with open("tests/resources/comments/result_cached.json", "r") as file:
        expected = json.load(file)
    assert result == expected


class MockedDriver:
    def __init__(self, post_id="3275298868401088037"):
        self.requests = []
        self.call_find_element_number = 0
        self.post_id = post_id

    def implicitly_wait(self, seconds):
        pass

    def get(self, url):
        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        with open(f"tests/resources/comments/comments_load{self.call_find_element_number}.json", "r") as file:
            data = json.load(file)
        response = mock.Mock(headers={"Content-Type": JsonResponseContentType.text_javascript,
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())
        request = mock.Mock(url=url, response=response)
        request.body = urlencode(dict(av="17841461911219001", doc_id="7336110846449933",
                                      variables=json.dumps({"media_id": self.post_id},
                                                           separators=(',', ':'))),
                                 quote_via=quote).encode()
        self.requests = [request]

    def find_elements(self, by, value):
        if not self.call_find_element_number:
            self.call_find_element_number += 1
            return []
        url = f"{INSTAGRAM_DOMAIN}/api/graphql"
        with open(f"tests/resources/comments/comments_load{self.call_find_element_number}.json", "r") as file:
            data = json.load(file)
        response = mock.Mock(headers={"Content-Type": JsonResponseContentType.text_javascript,
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())
        request = mock.Mock(url=url, response=response)
        request.body = urlencode(dict(av="17841461911219001", doc_id="6974885689225067",
                                      variables=json.dumps({"media_id": self.post_id},
                                                           separators=(',', ':'))),
                                 quote_via=quote).encode()
        self.requests = [request]
        self.call_find_element_number += 1
        return [mock.Mock()]

    def find_element(self, by, value):
        mocked_element = mock.Mock()
        mocked_element.get_attribute = mock.Mock(return_value=self.post_id)
        return mocked_element

    def execute(self, *args, **kwargs):
        pass


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
@mock.patch("crawlinsta.collecting.ActionChains", return_value=mock.MagicMock())
def test_collect_comments_of_post_success_load(mocked_action_chains, mocked_sleep):
    result = collect_comments_of_post(MockedDriver(), "C10MvewSSYl", 100)
    with open("tests/resources/comments/result_loaded.json", "r") as file:
        expected = json.load(file)
    assert result == expected


@pytest.mark.parametrize("n", [0, -1])
def test_collect_comments_of_post_fail_on_wrong_n(n):
    with pytest.raises(ValueError) as exc:
        collect_comments_of_post(MockedDriver(), "C10MvewSSYl", n)
    assert str(exc.value) == "The number of comments to collect must be a positive integer."


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_collect_comments_of_post_on_no_post_id_found(mocked_sleep):
    result = collect_comments_of_post(MockedDriver(""), "C10MvewSSYl", 10)
    assert result == {'comments': [], 'count': 0}
