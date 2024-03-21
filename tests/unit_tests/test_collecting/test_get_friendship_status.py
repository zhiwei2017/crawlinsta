import json
import pytest
from unittest import mock
from urllib.parse import urlencode, quote
from crawlinsta.collecting import INSTAGRAM_DOMAIN, API_VERSION, get_friendship_status
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def __init__(self, user_dict):
        self.user_dict = user_dict
        self.user_name = None
        super().__init__()

    def get(self, url):
        self.username = url.split("/")[-2]
        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={self.username}"
        with open(self.user_dict[self.username]["profile_file"], "r") as file:
            data = json.load(file)
        response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())
        request = mock.Mock(url=url, response=response)

        self.requests = [request]

    def find_element(self, by, value):
        user_id = self.user_dict[self.username]["id"]
        data_file = self.user_dict[self.username]["data_file"]

        searching_username = self.user_dict[self.username]["searching_username"]
        query_dict = dict(query=searching_username)

        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_id}/following/?{urlencode(query_dict, quote_via=quote)}"

        with open(data_file, "r") as file:
            data = json.load(file)
        response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())
        request = mock.Mock(url=url, response=response)
        self.requests = [request]
        return mock.MagicMock()


@pytest.mark.parametrize("username1, username2, user_id1, user_id2",
                         [("nasa", "astro_frankrubio", "528817151", "54688074404"),
                          ("regina_steinhauer", "nasa", "2057642850", "528817151")])
@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_get_friendship_status(mocked_sleep, username1, username2, user_id1, user_id2):
    user_dict = {
        username1: {
            "profile_file": f"tests/resources/friendship/{username1}_profile.json",
            "id": user_id1,
            "data_file": f"tests/resources/friendship/{username1}_following_search_{username2}.json",
            "searching_username": username2
        },
        username2: {
            "profile_file": f"tests/resources/friendship/{username2}_profile.json",
            "id": user_id2,
            "data_file": f"tests/resources/friendship/{username2}_following_search_{username1}.json",
            "searching_username": username1
        }
    }
    driver = MockedDriver(user_dict)
    result = get_friendship_status(driver, username1, username2)
    with open(f"tests/resources/friendship/{username1}_{username2}_result.json", "r") as file:
        expected = json.load(file)
    assert result == expected


@pytest.mark.parametrize("username1, username2, user_id1, user_id2",
                         [("nasa", "astro_frankrubio", "528817151", "54688074404"),
                          ("regina_steinhauer", "nasa", "2057642850", "528817151")])
@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
@mock.patch("crawlinsta.collecting.search_request", return_value=None)
@mock.patch("crawlinsta.collecting.logger")
def test_get_friendship_status_no_request_found(mocked_logger, mocked_search_request, mocked_sleep, username1, username2, user_id1, user_id2):
    user_dict = {
        username1: {
            "profile_file": f"tests/resources/friendship/{username1}_profile.json",
            "id": user_id1,
            "data_file": f"tests/resources/friendship/{username1}_following_search_{username2}.json",
            "searching_username": username2
        },
        username2: {
            "profile_file": f"tests/resources/friendship/{username2}_profile.json",
            "id": user_id2,
            "data_file": f"tests/resources/friendship/{username2}_following_search_{username1}.json",
            "searching_username": username1
        }
    }
    driver = MockedDriver(user_dict)
    result = get_friendship_status(driver, username1, username2)
    assert result == {"following": False, "followed_by": False}
    calls = [mock.call(f"Searching request for user '{username2}' in followings of user '{username1}' not found."),
             mock.call(f"Searching request for user '{username1}' in followings of user '{username2}' not found.")]
    mocked_logger.warning.assert_has_calls(calls, any_order=False)


class MockedDriverPrivate(MockedDriver):
    def __init__(self, user_dict):
        self.user_dict = user_dict
        self.user_name = None
        super().__init__(user_dict)

    def get(self, url):
        self.username = url.split("/")[-2]
        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={self.username}"
        with open(self.user_dict[self.username]["profile_file"], "r") as file:
            data = json.load(file)
        data["data"]["user"]["is_private"] = True
        response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())
        request = mock.Mock(url=url, response=response)

        self.requests = [request]

    def find_element(self, by, value):
        user_id = self.user_dict[self.username]["id"]
        data_file = self.user_dict[self.username]["data_file"]

        searching_username = self.user_dict[self.username]["searching_username"]
        query_dict = dict(query=searching_username)

        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/friendships/{user_id}/following/?{urlencode(query_dict, quote_via=quote)}"

        with open(data_file, "r") as file:
            data = json.load(file)
        response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                      'Content-Encoding': 'identity'},
                             body=json.dumps(data).encode())
        request = mock.Mock(url=url, response=response)
        self.requests = [request]
        return mock.MagicMock()


@pytest.mark.parametrize("username1, username2, user_id1, user_id2",
                         [("nasa", "astro_frankrubio", "528817151", "54688074404"),
                          ("regina_steinhauer", "nasa", "2057642850", "528817151")])
@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_get_friendship_status_private_account(mocked_sleep, username1, username2, user_id1, user_id2):
    user_dict = {
        username1: {
            "profile_file": f"tests/resources/friendship/{username1}_profile.json",
            "id": user_id1,
            "data_file": f"tests/resources/friendship/{username1}_following_search_{username2}.json",
            "searching_username": username2
        },
        username2: {
            "profile_file": f"tests/resources/friendship/{username2}_profile.json",
            "id": user_id2,
            "data_file": f"tests/resources/friendship/{username2}_following_search_{username1}.json",
            "searching_username": username1
        }
    }
    driver = MockedDriverPrivate(user_dict)
    result = get_friendship_status(driver, username1, username2)
    assert result == {"following": False, "followed_by": False}


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_collect_posts_of_user_no_request(mocked_sleep):
    with pytest.raises(ValueError) as exc_info:
        get_friendship_status(BaseMockedDriver(), "nasa", "astro_frankrubio")
    assert str(exc_info.value) == "User 'nasa' not found."
