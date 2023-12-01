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

    pip install git+https://github.com/zhiwei2017/crawlinsta.git@init

How to Use
++++++++++

Create Browser Driver
~~~~~~~~~~~~~~~~~~~~~
To create a browser driver, you need to first import **webdriver** from
**crawlinsta** package and initiate a browser instance via::

    >>> from crawlinsta import webdriver
    >>> driver = webdriver.Chrome('path_to_chromedriver')
    >>> "Do some crawling with driver"
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
     - collect_user_info(driver, "dummy_instagram_username")
   * - crawlinsta.collecting.collect_posts_of_user
     - Collects n posts from the account with given `username`
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of posts, which should be collected. By default, it's 100. If it's set to 0, collect all posts.
     - collect_posts_of_user(driver, "dummy_instagram_username", 100)
   * - crawlinsta.collecting.collect_reels_of_user
     - Collects n reels from the account with given `username`
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of reels, which should be collected. By default, it's 100. If it's set to 0, collect all reels.
     - collect_reels_of_user(driver, "dummy_instagram_username", 100)
   * - crawlinsta.collecting.collect_followers
     - Collects n followers from the account with given `username`
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of followers, which should be collected. By default, it's 100. If it's set to 0, collect all followers.
     - collect_followers(driver, "dummy_instagram_username", 100)
   * - crawlinsta.collecting.collect_followings
     - Collects n following users from the account with given `username`
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of following users, which should be collected. By default, it's 100. If it's set to 0, collect all following users.
     - collect_following(driver, "dummy_instagram_username", 100)
   * - crawlinsta.collecting.collect_following_hashtags
     - Collects n following hashtags from the account with given `username`
     -
        * driver: browser driver instance
        * username (:obj:`str`): username to crawl
        * n (:obj:`int`): maximum number of following hashtags, which should be collected. By default, it's 100. If it's set to 0, collect all following hashtags.
     - collect_following_hashtags(driver, "dummy_instagram_username", 100)

Maintainers
-----------

..
    TODO: List here the people responsible for the development and maintaining of this project.
    Format: **Name** - *Role/Responsibility* - Email

* **Zhiwei Zhang** - *Maintainer* - `zhiwei2017@gmail.com <mailto:zhiwei2017@gmail.com?subject=[GitHub]Instagram%20Crawler>`_