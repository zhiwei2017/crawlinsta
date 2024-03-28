import logging
import random
import time
from seleniumwire.webdriver import Chrome, Edge, Firefox, Safari, Remote
from typing import Union
from ..decorators import driver_implicit_wait
from ..utils import search_request

logger = logging.getLogger("crawlinsta")


@driver_implicit_wait(10)
def download_media(driver: Union[Chrome, Edge, Firefox, Safari, Remote],
                   media_url: str,
                   file_name: str) -> None:
    """Download the image/video based on the given media_url, and store it to
    the given path.

    Normally, the media_url is valid for 1 week (max. 3 weeks).

    Args:
        driver (selenium.webdriver.remote.webdriver.WebDriver): selenium
         driver for controlling the browser to perform certain actions.
        media_url (str): url of the media for downloading.
        file_name (str): path for storing the downloaded media.

    Raises:
        ValueError: if the media url is not found.

    Examples:
        >>> from crawlinsta import webdriver
        >>> from crawlinsta.login import login, login_with_cookies
        >>> from crawlinsta.collecting import download_media
        >>> driver = webdriver.Chrome('path_to_chromedriver')
        >>> # if you already used once the login function, you can use the
        >>> # login_with_cookies function to login with the cookie file.
        >>> login(driver, "your_username", "your_password")  # or login_with_cookies(driver)
        >>> download_media(driver, "https://scontent-muc2-1.xx.fbcdn.net/v/t39.12897-6/4197848_n.m4a", "tmp")
    """
    driver.get(media_url)
    time.sleep(random.SystemRandom().randint(4, 6))

    idx = search_request(driver.requests, media_url, response_content_type=None)
    if idx is None:
        raise ValueError(f"Media url '{media_url}' not found.")
    request = driver.requests.pop(idx)
    file_extension = request.response.headers["Content-Type"].split("/")[1]
    with open(f"{file_name}.{file_extension}", "wb") as f:
        f.write(request.response.body)
        f.close()
    logger.info(f"Media downloaded successfully to '{file_name}.{file_extension}'.")