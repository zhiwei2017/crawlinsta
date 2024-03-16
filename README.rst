Crawlinsta
==========

Introduction
------------
A python package for crawling instagram based on [selenium](https://selenium-python.readthedocs.io)
and [selenium-wire](https://github.com/wkeeling/selenium-wire). The idea is to use selenium
to trigger the javascript in browser to send requests to the server for a specific action,
and meanwhile selenium-wire will keep tracking on the network and capture the responses
for data extraction purpose.

User Guide
----------

How to Install
++++++++++++++

Please install it via::

    pip install git+https://github.com/zhiwei2017/crawlinsta.git@master

How to Use
++++++++++

Create Browser Driver
~~~~~~~~~~~~~~~~~~~~~
To create a browser driver, you need to first import **webdriver** from
**crawlinsta** package and initiate a browser instance via::

    >>> from crawlinsta import webdriver
    >>> driver = webdriver.Chrome('path_to_chromedriver')
    >>> # Do some crawling with driver
    >>> driver.quit()

If you don't specify the Chrome driver path, the default one will be used.

Please remember to call::

    >>> driver.quit()

when you finish the crawling.

Login
~~~~~

For the first time login, you need to prepare your username and password, and
use the function **login** from module **crawlinsta.login**, such as::

    >>> from crawlinsta.login import login
    >>> login(driver, "your_username", "your_password")

Once you login with your username and password, a cookie will be created with
default name *instagram_cookies.pkl*. You can use the function **login_with_cookies**
from module **crawlinsta.login** to login with the cookie file, such as::

    >>> from crawlinsta.login import login_with_cookies
    >>> login_with_cookies(driver)

Crawling
~~~~~~~~

Current available crawling functions:

`crawlinsta.collecting.collect_user_info`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Collects user information for the given `username`.

    Input:
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl

    Output:
        * user_info (:obj:`dict`): user information, including username, full name, biography, external url, number of posts, number of followers, number of followings, and number of reels.

    **Example**:

        >>> collect_user_info(driver, "nasa")
        {
          "id": "528817151",
          "username": "nasa",
          "fullname": "NASA",
          "biography": "Exploring the universe and our home planet.",
          "follower_count": 97956738,
          "following_count": 77,
          "following_tag_count": 10,
          "is_private": false,
          "is_verified": true,
          "profile_pic_url": "https://dummy.pic.com",
          "post_count": 4116,
          "usertags_count": 0
        }


`crawlinsta.collecting.collect_posts_of_user`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Collects n posts from the account with given `username`

    Input:
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of posts, which should be collected. By default, it's 100. If it's set to 0, collect all posts.

    Output:
        * posts (:obj:`list`): list of posts, each post is a dictionary containing post information, including post code, post url, post type, post caption, post location, post time, number of likes, number of comments, and media url.

    **Example**:

        >>> collect_posts_of_user(driver, "dummy_instagram_username", 100)
        {
          "posts": [
            {
              "like_count": 817982,
              "comment_count": 3000,
              "id": "3215769692664507668",
              "code": "CygtX9ivC0U",
              "user": {
                "id": "50269116275",
                "username": "dummy_instagram_username",
                "fullname": "",
                "profile_pic_url": "https://scontent.cdninstagram.com/v",
                "is_private": false,
                "is_verified": false
              },
              "taken_at": 1697569769,
              "media_type": "Photo",
              "caption": {
                "id": "17985380039262083",
                "text": "I know what she’s gonna say before she even has the chance 😂",
                "created_at_utc": null
              },
              "accessibility_caption": "",
              "original_width": 1080,
              "original_height": 1920,
              "urls": [
                "https://scontent.cdninstagram.com/o1"
              ],
              "has_shared_to_fb": false,
              "usertags": [],
              "location": null,
              "music": {
                "id": "2614441095386924",
                "is_trending_in_clips": false,
                "artist": {
                  "id": "50269116275",
                  "username": "dummy_instagram_username",
                  "fullname": "",
                  "profile_pic_url": "",
                  "is_private": null,
                  "is_verified": null
                },
                "title": "Original audio",
                "duration_in_ms": null,
                "url": null
              }
            },
            ...
            ],
          "count": 100
        }

`crawlinsta.collecting.collect_reels_of_user`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Collects n reels from the account with given `username`

    Input:
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of reels, which should be collected. By default, it's 100. If it's set to 0, collect all reels.

    Output:
        * reels (:obj:`list`): list of reels, each reel is a dictionary containing reel information, including reel code, reel url, reel caption, reel time, number of likes, number of comments, and media url.

    **Example**:

        >>> collect_reels_of_user(driver, "dummy_instagram_username", 100)
        {
          "reels": [
            {
              "like_count": 817982,
              "comment_count": 3000,
              "id": "3215769692664507668",
              "code": "CygtX9ivC0U",
              "user": {
                "id": "50269116275",
                "username": "dummy_instagram_username",
                "fullname": "",
                "profile_pic_url": "https://scontent.cdninstagram.com/v",
                "is_private": false,
                "is_verified": false
              },
              "taken_at": 1697569769,
              "media_type": "Reel",
              "caption": {
                "id": "17985380039262083",
                "text": "I know what she’s gonna say before she even has the chance 😂",
                "created_at_utc": null
              },
              "accessibility_caption": "",
              "original_width": 1080,
              "original_height": 1920,
              "urls": [
                "https://scontent.cdninstagram.com/o1"
              ],
              "has_shared_to_fb": false,
              "usertags": [],
              "location": null,
              "music": {
                "id": "2614441095386924",
                "is_trending_in_clips": false,
                "artist": {
                  "id": "50269116275",
                  "username": "dummy_instagram_username",
                  "fullname": "",
                  "profile_pic_url": "",
                  "is_private": null,
                  "is_verified": null
                },
                "title": "Original audio",
                "duration_in_ms": null,
                "url": null
              }
            },
            ...
            ],
          "count": 100
        }

`crawlinsta.collecting.collect_tagged_posts_of_user`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Collects n posts in which the user with given `username` is tagged

    Input:
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of tagged posts, which should be collected. By default, it's 100. If it's set to 0, collect all tagged posts.

    Output:
        * tagged_posts (:obj:`list`): list of tagged posts, each post is a dictionary containing post information, including post code, post url, post type, post caption, post location, post time, number of likes, number of comments, and media url.

    **Example**:

        >>> collect_tagged_posts_of_user(driver, "dummy_instagram_username", 100)
        {
          "tagged_posts": [
            {
              "like_count": 817982,
              "comment_count": 3000,
              "id": "3215769692664507668",
              "code": "CygtX9ivC0U",
              "user": {
                "id": "50269116275",
                "username": "dummy_instagram_username",
                "fullname": "",
                "profile_pic_url": "https://scontent.cdninstagram.com/v",
                "is_private": false,
                "is_verified": false
              },
              "taken_at": 1697569769,
              "media_type": "Reel",
              "caption": {
                "id": "17985380039262083",
                "text": "I know what she’s gonna say before she even has the chance 😂",
                "created_at_utc": null
              },
              "accessibility_caption": "",
              "original_width": 1080,
              "original_height": 1920,
              "urls": [
                "https://scontent.cdninstagram.com/o1"
              ],
              "has_shared_to_fb": false,
              "usertags": [],
              "location": null,
              "music": {
                "id": "2614441095386924",
                "is_trending_in_clips": false,
                "artist": {
                  "id": "50269116275",
                  "username": "dummy_instagram_username",
                  "fullname": "",
                  "profile_pic_url": "",
                  "is_private": null,
                  "is_verified": null
                },
                "title": "Original audio",
                "duration_in_ms": null,
                "url": null
              }
            },
            ...
            ],
          "count": 100
        }

`crawlinsta.collecting.get_friendship_status`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Get the relationship between the user with `username1` and the user with `username2`, i.e. finding out who is following whom.

    Input:
        * driver: browser driver instance
        * username1 (:obj:`str`): username of the person A.
        * username2 (:obj:`str`): username of the person B.

    Output:
        * friendship_status (:obj:`dict`): relationship between the two users, including whether person A is following person B and whether person B is following person A.

    **Example**:

        >>> get_friendship_status(driver, "dummy_instagram_username1", "dummy_instagram_username2")
        {
          "following": false,
          "followed_by": true
        }

`crawlinsta.collecting.collect_followers_of_user`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Collects n followers from the account with given `username`

    Input:
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of followers, which should be collected. By default, it's 100. If it's set to 0, collect all followers.

    Output:
        * followers (:obj:`list`): list of followers, each follower is a dictionary containing follower information, including follower username, follower full name, follower profile picture url etc.

    **Example**:

        >>> collect_followers_of_user(driver, "dummy_instagram_username", 100)
        {
          "users": [
            {
              "id": "528817151",
              "username": "nasa",
              "fullname": "NASA",
              "is_private": false,
              "is_verified": true,
              "profile_pic_url": "https://dummy.pic.com",
            },
            ...
            ],
          "count": 100
        }

`crawlinsta.collecting.collect_followings_of_user`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Collects n following users from the account with given `username`

    Input:
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of following users, which should be collected. By default, it's 100. If it's set to 0, collect all following users.

    Output:
        * followings (:obj:`list`): list of following users, each following user is a dictionary containing following user information, including following username, following full name, following profile picture url etc.

    **Example**:

        >>> collect_followings_of_user(driver, "dummy_instagram_username", 100)
        {
          "users": [
            {
              "id": "528817151",
              "username": "nasa",
              "fullname": "NASA",
              "is_private": false,
              "is_verified": true,
              "profile_pic_url": "https://dummy.pic.com",
            },
            ...
            ],
          "count": 100
        }

`crawlinsta.collecting.collect_following_hashtags_of_user`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Collects n following hashtags from the account with given `username`

    Input:
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of following hashtags, which should be collected. By default, it's 100. If it's set to 0, collect all following hashtags.

    Output:
        * following_hashtags (:obj:`list`): list of following hashtags, each following hashtag is a dictionary containing following hashtag information, including hashtag id, hashtag name, hashtag post count, hashtag profile picture url.

    **Example**:

        >>> collect_following_hashtags_of_user(driver, "dummy_instagram_username", 100)
        {
          "hashtags": [
            {
              "id": "528817151",
              "name": "asiangames",
              "post_count": 1000000,
              "profile_pic_url": "https://dummy.pic.com",
            },
            ...
            ],
          "count": 100
        }

`crawlinsta.collecting.collect_likers_of_post`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Collect the users, who likes a given post.

    Input:
        * driver: browser driver instance
        * post_code (:obj:`str`): post code, used for generating post directly accessible url.
        * n (:obj:`int`): maximum number of likers, which should be collected. By default, it's 100. If it's set to 0, collect all likers.

    Output:
        * likers (:obj:`list`): list of likers, each liker is a dictionary containing liker information, including liker username, liker full name, liker profile picture url etc and friendship status between the post owner and the liker.

    **Example**:

        >>> collect_likers_of_post(driver, "WGDBS3D", 100)
        {
          "likers": [
            {
              "id": "528817151",
              "username": "nasa",
              "fullname": "NASA",
              "is_private": false,
              "is_verified": true,
              "profile_pic_url": "https://dummy.pic.com",
            },
            ...
            ],
          "count": 100
        }

`crawlinsta.collecting.collect_comments_of_post`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Collect n comments of a given post.

    Input:
        * driver: browser driver instance
        * post_code (:obj:`str`): post code, used for generating post directly accessible url.
        * n (:obj:`int`): maximum number of comments, which should be collected. By default, it's 100. If it's set to 0, collect all comments.

    Output:
        * comments (:obj:`list`): list of comments, each comment is a dictionary containing comment information, including comment id, comment text, comment time, comment likes count, comment owner username, comment owner full name, comment owner profile picture url etc.

    **Example**:

        >>> collect_comments_of_post(driver, "WGDBS3D", 100)
        {
          "comments": [
            {
              "id": "18278957755095859",
              "user": {
                "id": "6293392719",
                "username": "dummy_user"
              },
              "post_id": "3275298868401088037",
              "created_at_utc": 1704669275,
              "status": null,
              "share_enabled": null,
              "is_ranked_comment": null,
              "text": "Fantastic Job",
              "has_translation": false,
              "is_liked_by_post_owner": null,
              "comment_like_count": 0
            },
            ...
            ],
          "count": 100
        }

`crawlinsta.collecting.search_with_keyword`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Search hashtags or users with given keyword.

    Input:
        * driver: browser driver instance
        * keyword (:obj:`str`): keyword for searching.
        * pers (:obj:`bool`): indicating whether results should be personalized or not.

    Output:
        * search_results (:obj:`dict`): search results, including users, places and hashtags.

    **Example**:

        >>> search_with_keyword(driver, "shanghai", pers=True)
        {
          "hashtags": [
            {
              "position": 1,
              "hashtag": {
                "id": "17841563224118980",
                "name": "shanghai",
                "post_count": 11302316,
                "profile_pic_url": ""
              }
            }
          ],
          "users": [
            {
              "position": 0,
              "user": {
                "id": "7594441262",
                "username": "shanghai.explore",
                "fullname": "Shanghai 🇨🇳 Travel | Hotels | Food | Tips",
                "profile_pic_url": "https://scontent.cdninstagram.com/v/t51.2885-19/409741157_243678455262812_2168807265478461941_n.jpg?stp=dst-jpg_s150x150&_nc_ht=scontent.cdninstagram.com&_nc_cat=108&_nc_ohc=S3SAe59tdbUAX9SLkyd&edm=APs17CUBAAAA&ccb=7-5&oh=00_AfALvv52ytTyye_PDEjKCmWAUetHX8BXCGsS7rnFThzNTQ&oe=65ECAABE&_nc_sid=10d13b",
                "is_private": null,
                "is_verified": true
              }
            }
          ],
          "places": [
            {
              "position": 2,
              "place": {
                "location": {
                  "id": "106324046073002",
                  "name": "Shanghai, China"
                },
                "subtitle": "",
                "title": "Shanghai, China"
              }
            }
          ],
          "personalised": true
        }

`crawlinsta.collecting.collect_top_posts_of_hashtag`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Collect top posts of a given hashtag.

    Input:
        * driver: browser driver instance
        * hashtag (:obj:`str`): hashtag

    Output:
        * top_posts (:obj:`list`): list of top posts, each post is a dictionary containing post information, including post code, post url, post type, post caption, post location, post time, number of likes, number of comments, and media url.

    **Example**:

        >>> collect_top_posts_of_hashtag(driver, "shanghai")
        {
          "top_posts": [
            {
              "like_count": 817982,
              "comment_count": 3000,
              "id": "3215769692664507668",
              "code": "CygtX9ivC0U",
              "user": {
                "id": "50269116275",
                "username": "dummy_instagram_username",
                "fullname": "",
                "profile_pic_url": "https://scontent.cdninstagram.com/v",
                "is_private": false,
                "is_verified": false
              },
              "taken_at": 1697569769,
              "media_type": "Reel",
              "caption": {
                "id": "17985380039262083",
                "text": "I know what she’s gonna say before she even has the chance 😂#shanghai",
                "created_at_utc": null
              },
              "accessibility_caption": "",
              "original_width": 1080,
              "original_height": 1920,
              "urls": [
                "https://scontent.cdninstagram.com/o1"
              ],
              "has_shared_to_fb": false,
              "usertags": [],
              "location": null,
              "music": {
                "id": "2614441095386924",
                "is_trending_in_clips": false,
                "artist": {
                  "id": "50269116275",
                  "username": "dummy_instagram_username",
                  "fullname": "",
                  "profile_pic_url": "",
                  "is_private": null,
                  "is_verified": null
                },
                "title": "Original audio",
                "duration_in_ms": null,
                "url": null
              }
            },
            ...
            ],
          "count": 100
        }

`crawlinsta.collecting.collect_posts_by_music_id`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Collect n posts containing the given music_id. If n is set to 0, collect all posts.

    Input:
        * driver: browser driver instance.
        * music_id (:obj:`str`): id of the music.
        * n (:obj:`int`): maximum number of posts, which should be collected. By default, it's 100. If it's set to 0, collect all posts.

    Output:
        * posts (:obj:`list`): list of posts, each post is a dictionary containing post information, including post code, post url, post type, post caption, post location, post time, number of likes, number of comments, and media url.

    **Example**:

        >>> collect_posts_by_music_id(driver, "2614441095386924", 100)
        {
          "posts": [
            {
              "like_count": 817982,
              "comment_count": 3000,
              "id": "3215769692664507668",
              "code": "CygtX9ivC0U",
              "user": {
                "id": "50269116275",
                "username": "dummy_instagram_username",
                "fullname": "",
                "profile_pic_url": "https://scontent.cdninstagram.com/v",
                "is_private": false,
                "is_verified": false
              },
              "taken_at": 1697569769,
              "media_type": "Reel",
              "caption": {
                "id": "17985380039262083",
                "text": "I know what she’s gonna say before she even has the chance 😂",
                "created_at_utc": null
              },
              "accessibility_caption": "",
              "original_width": 1080,
              "original_height": 1920,
              "urls": [
                "https://scontent.cdninstagram.com/o1"
              ],
              "has_shared_to_fb": false,
              "usertags": [],
              "location": null,
              "music": {
                "id": "2614441095386924",
                "is_trending_in_clips": false,
                "artist": {
                  "id": "50269116275",
                  "username": "dummy_instagram_username",
                  "fullname": "",
                  "profile_pic_url": "",
                  "is_private": null,
                  "is_verified": null
                },
                "title": "Original audio",
                "duration_in_ms": null,
                "url": null
              }
            },
            ...
            ],
          "count": 100
        }

`crawlinsta.collecting.download_media`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Download the image/video based on the given media_url, and store it to the given path.

    Input:
        * driver: browser driver instance
        * media_url (:obj:`str`): url of the media for downloading.
        * file_name (:obj:`str`): path for storing the downloaded media.

    **Example**:

        >>> download_media(driver, "dummy_media_url", "dummy")

Maintainers
-----------
* **Zhiwei Zhang** - *Maintainer* - `zhiwei2017@gmail.com <mailto:zhiwei2017@gmail.com?subject=[GitHub]Instagram%20Crawler>`_