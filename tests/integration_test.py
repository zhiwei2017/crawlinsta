import os
import pytest
import random
import shutil
import tempfile
import time
from crawlinsta import webdriver
from crawlinsta.login import login, login_with_cookies
from crawlinsta.collecting import (
    collect_user_info,
    collect_posts_of_user,
    collect_reels_of_user,
    collect_tagged_posts_of_user,
    get_friendship_status,
    collect_followers_of_user,
    collect_followings_of_user,
    collect_following_hashtags_of_user,
    collect_likers_of_post,
    collect_comments_of_post,
    search_with_keyword,
    collect_top_posts_of_hashtag,
    collect_posts_by_music_id,
    download_media
)
from crawlinsta.schemas import (
    UserInfo, Posts, Users, HashtagBasicInfos, Comments, SearchingResult,
    Hashtag, MusicPosts, FriendshipStatus
)


@pytest.fixture(scope="module")
def chrome_driver():
    driver = webdriver.Chrome()
    username = os.environ.get("INSTAGRAM_USERNAME")
    password = os.environ.get("INSTAGRAM_PASSWORD")
    if os.path.exists("instagram_cookies.pkl"):
        login_with_cookies(driver, "instagram_cookies.pkl")
    elif username and password:
        login(driver, username, password)
    else:
        raise ValueError("Please provide username and password in environment variables.")
    del driver.requests
    yield driver
    driver.quit()


def generic_test(driver, func_to_test, result_model, key_with_list=None, *args, **kwargs):
    time.sleep(random.randint(4, 6))
    result = func_to_test(driver, *args, **kwargs)
    assert result is not None
    assert isinstance(result, dict)
    assert len(result) > 0
    validated_instance = result_model.model_validate(result)
    assert validated_instance.model_dump(mode="json") == result
    if key_with_list:
        assert result["count"] == len(result[key_with_list])
    del driver.requests


@pytest.mark.parametrize("username", ["angibieneck"])
def test_collect_user_info(chrome_driver, username):
    generic_test(chrome_driver, collect_user_info, UserInfo, None, username)


@pytest.mark.parametrize("username, number_of_posts", [("onesmileymonkey", 20)])
def test_collect_posts_of_user(chrome_driver, username, number_of_posts):
    generic_test(chrome_driver, collect_posts_of_user, Posts, "posts", username, number_of_posts)


@pytest.mark.parametrize("username, number_of_posts", [("onesmileymonkey", 20)])
def test_collect_reels_of_user(chrome_driver, username, number_of_posts):
    generic_test(chrome_driver, collect_reels_of_user, Posts, "posts", username, number_of_posts)


@pytest.mark.parametrize("username, number_of_posts", [("onesmileymonkey", 20)])
def test_collect_tagged_posts_of_user(chrome_driver, username, number_of_posts):
    generic_test(chrome_driver, collect_tagged_posts_of_user, Posts, "posts", username, number_of_posts)


@pytest.mark.parametrize("username1, username2", [("nasa", "astro_frankrubio")])
def test_get_friendship_status(chrome_driver, username1, username2):
    generic_test(chrome_driver, get_friendship_status, FriendshipStatus, None, username1, username2)


@pytest.mark.parametrize("username, number_of_users", [("onesmileymonkey", 20)])
def test_collect_followers_of_user(chrome_driver, username, number_of_users):
    generic_test(chrome_driver, collect_followers_of_user, Users, "users", username, number_of_users)


@pytest.mark.parametrize("username, number_of_users", [("onesmileymonkey", 20),
                                                       ("angibieneck", 100)])
def test_collect_followings_of_user(chrome_driver, username, number_of_users):
    generic_test(chrome_driver, collect_followings_of_user, Users, "users", username, number_of_users)


@pytest.mark.parametrize("username, number_of_hashtags", [("angibieneck", 100)])
def test_collect_following_hashtags_of_user(chrome_driver, username, number_of_hashtags):
    generic_test(chrome_driver, collect_following_hashtags_of_user, HashtagBasicInfos, "hashtags", username, number_of_hashtags)


@pytest.mark.parametrize("post_code, number_of_users", [("C2P19gPrUw5", 100)])
def test_collect_likers_of_post(chrome_driver, post_code, number_of_users):
    generic_test(chrome_driver, collect_likers_of_post, Users, "users", post_code, number_of_users)


@pytest.mark.parametrize("post_code, number_of_comments", [("C10MvewSSYl", 100)])
def test_collect_comments_of_post(chrome_driver, post_code, number_of_comments):
    generic_test(chrome_driver, collect_comments_of_post, Comments, "comments", post_code, number_of_comments)


@pytest.mark.parametrize("keyword, personalized", [("shanghai", False), ("shanghai", True)])
def test_search_with_keyword(chrome_driver, keyword, personalized):
    generic_test(chrome_driver, search_with_keyword, SearchingResult, None, keyword, personalized)


@pytest.mark.parametrize("hashtag", ["shanghai"])
def test_collect_top_posts_of_hashtag(chrome_driver, hashtag):
    generic_test(chrome_driver, collect_top_posts_of_hashtag, Hashtag, None, hashtag)


@pytest.mark.parametrize("music_id, number_of_posts", [("997508674672914", 20)])
def test_collect_posts_by_music_id(chrome_driver, music_id, number_of_posts):
    generic_test(chrome_driver, collect_posts_by_music_id, MusicPosts, "posts", music_id, number_of_posts)


@pytest.mark.parametrize("music_id, number_of_posts", [("997508674672914", 20)])
def test_download_media(chrome_driver, music_id, number_of_posts):
    user_info = collect_user_info(chrome_driver, "angibieneck")
    tmp_dir = tempfile.mkdtemp()
    tmp_filename = os.path.join(tmp_dir, "image")
    download_media(chrome_driver, user_info["profile_pic_url"], tmp_filename)
    assert len(os.listdir(tmp_dir)) > 0
    shutil.rmtree(tmp_dir)
