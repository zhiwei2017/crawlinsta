import json
from unittest import mock
from crawlinsta.collecting import INSTAGRAM_DOMAIN, API_VERSION, collect_user_info
from .base_mocked_driver import BaseMockedDriver


class MockedDriver(BaseMockedDriver):
    def get(self, url):
        username = url.split("/")[-2]
        url = f"{INSTAGRAM_DOMAIN}/{API_VERSION}/users/web_profile_info/?username={username}"
        with open("tests/resources/user_info/web_profile_info.json", "r") as file:
            data = json.load(file)
        request = mock.Mock()
        request.url = url
        request.response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]

    def find_element(self, by, value):
        url = "https://www.instagram.com/graphql/query/?doc_id=17901966028246171&variables=%7B%22id%22%3A%22528817151%22%7D"
        with open("tests/resources/user_info/query.json", "r") as file:
            data = json.load(file)
        request = mock.Mock()
        request.url = url
        request.response = mock.Mock(headers={"Content-Type": "application/json; charset=utf-8",
                                              'Content-Encoding': 'identity'},
                                     body=json.dumps(data).encode())
        self.requests = [request]
        return mock.Mock()


@mock.patch("crawlinsta.collecting.time.sleep", return_value=None)
def test_collect_user_info(mocked_sleep):
    result = collect_user_info(MockedDriver(), "nasa")
    assert result == {
        'id': '528817151',
        "username": "nasa",
        "fullname": "NASA",
        "biography": "🚀 🌎  Exploring the universe and our home planet. Verification: nasa.gov/socialmedia",
        'follower_count': 97956738,
        'following_count': 77,
        'following_tag_count': 10,
        "is_private": False,
        "is_verified": True,
        "profile_pic_url": 'https://scontent-muc2-1.cdninstagram.com/v/t51.2885-19/29090066_159271188110124_1152068159029641216_n.jpg?stp=dst-jpg_s150x150&_nc_ht=scontent-muc2-1.cdninstagram.com&_nc_cat=1&_nc_ohc=QR8vCKU7rFgAX-lnMuu&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfC3ixsrquc_5TCJtVEtyC3hGx2rL8bLgprss4AV7rw1Mg&oe=65E1C329&_nc_sid=8b3546',
        'post_count': 4116,
        'usertags_count': 0,
    }
