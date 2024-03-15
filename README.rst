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

.. list-table:: Title
   :widths: 10 30 30 30
   :header-rows: 1

   * - Function
     - Description
     - Function Parameters
     - Example
   * - crawlinsta.collecting.collect_user_info
     - Collects user information for the given `username`
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import collect_user_info
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        collect_user_info(driver, "dummy_instagram_username")

   * - crawlinsta.collecting.collect_posts_of_user
     - Collects n posts from the account with given `username`
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of posts, which should be collected. By default, it's 100. If it's set to 0, collect all posts.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import collect_posts_of_user
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        collect_posts_of_user(driver, "dummy_instagram_username", 100)

   * - crawlinsta.collecting.collect_reels_of_user
     - Collects n reels from the account with given `username`
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of reels, which should be collected. By default, it's 100. If it's set to 0, collect all reels.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import collect_reels_of_user
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        collect_reels_of_user(driver, "dummy_instagram_username", 100)

   * - crawlinsta.collecting.collect_tagged_posts_of_user
     - Collects n posts in which the user with given `username` is tagged
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of tagged posts, which should be collected. By default, it's 100. If it's set to 0, collect all tagged posts.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import collect_tagged_posts_of_user
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        collect_tagged_posts_of_user(driver, "dummy_instagram_username", 100)

   * - crawlinsta.collecting.get_friendship_status
     - Get the relationship between the user with `username1` and the user with `username2`, i.e. finding out who is following whom.
     -
        * driver: browser driver instance
        * username1 (:obj:`str`): username of the person A.
        * username2 (:obj:`str`): username of the person B.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import get_friendship_status
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        get_friendship_status(driver, "dummy_instagram_username1", "dummy_instagram_username2")

   * - crawlinsta.collecting.collect_followers_of_user
     - Collects n followers from the account with given `username`
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of followers, which should be collected. By default, it's 100. If it's set to 0, collect all followers.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import collect_followers_of_user
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        collect_followers_of_user(driver, "dummy_instagram_username", 100)

   * - crawlinsta.collecting.collect_followings_of_user
     - Collects n following users from the account with given `username`
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of following users, which should be collected. By default, it's 100. If it's set to 0, collect all following users.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import collect_followings_of_user
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        collect_followings_of_user(driver, "dummy_instagram_username", 100)

   * - crawlinsta.collecting.collect_following_hashtags_of_user
     - Collects n following hashtags from the account with given `username`
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of following hashtags, which should be collected. By default, it's 100. If it's set to 0, collect all following hashtags.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import collect_following_hashtags_of_user
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        collect_following_hashtags_of_user(driver, "dummy_instagram_username", 100)

   * - crawlinsta.collecting.collect_likers_of_post
     - Collect the users, who likes a given post.
     -
        * driver: browser driver instance
        * post_code (:obj:`str`): post code, used for generating post directly accessible url.
        * n (:obj:`int`): maximum number of likers, which should be collected. By default, it's 100. If it's set to 0, collect all likers.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import collect_likers_of_post
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        collect_likers_of_post(driver, "dummy_post_code", 100)

   * - crawlinsta.collecting.collect_comments_of_post
     - Collect n comments of a given post.
     -
        * driver: browser driver instance
        * post_code (:obj:`str`): post code, used for generating post directly accessible url.
        * n (:obj:`int`): maximum number of comments, which should be collected. By default, it's 100. If it's set to 0, collect all comments.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import collect_comments_of_post
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        collect_comments_of_post(driver, "dummy_post_code", 100)

   * - crawlinsta.collecting.search_with_keyword
     - Search hashtags or users with given keyword.
     -
        * driver: browser driver instance
        * keyword (:obj:`str`): keyword for searching.
        * pers (:obj:`bool`): indicating whether results should be personalized or not.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import search_with_keyword
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        search_with_keyword(driver, "dummy_searching_keyword", pers=True)

   * - crawlinsta.collecting.collect_top_posts_of_hashtag
     - Collect top posts of a given hashtag.
     -
        * driver: browser driver instance
        * hashtag (:obj:`str`): hashtag
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import collect_top_posts_of_hashtag
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        collect_top_posts_of_hashtag(driver, "dummy_hashtag")

   * - crawlinsta.collecting.collect_posts_by_music_id
     - Collect n posts containing the given music_id. If n is set to 0, collect all posts.
     -
        * driver: browser driver instance.
        * music_id (:obj:`str`): id of the music.
        * n (:obj:`int`): maximum number of posts, which should be collected. By default, it's 100. If it's set to 0, collect all posts.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import collect_posts_by_music_id
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        collect_posts_by_music_id(driver, "dummy_music_id", 100)

   * - crawlinsta.collecting.download_media
     - Download the image/video based on the given media_url, and store it to the given path.
     -
        * driver: browser driver instance
        * media_url (:obj:`str`): url of the media for downloading.
        * file_name (:obj:`str`): path for storing the downloaded media.
     - ::

        from crawlinsta import webdriver
        from crawlinsta.login import login, login_with_cookies
        from crawlinsta.collecting import download_media
        driver = webdriver.Chrome('path_to_chromedriver')
        # if you already used once the login function, you can use the
        # login_with_cookies function to login with the cookie file.
        login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        download_media(driver, "dummy_media_url", "dummy")

Maintainers
-----------

..
    TODO: List here the people responsible for the development and maintaining of this project.
    Format: **Name** - *Role/Responsibility* - Email

* **Zhiwei Zhang** - *Maintainer* - `zhiwei2017@gmail.com <mailto:zhiwei2017@gmail.com?subject=[GitHub]Instagram%20Crawler>`_