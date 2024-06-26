import json
import logging
from seleniumwire.utils import decode
from seleniumwire.request import Request, Response
from typing import List, Callable, Optional, Dict, Any, Tuple, Union
from .constants import JsonResponseContentType


logger = logging.getLogger("crawlinsta")


def filter_requests(requests: List[Request],
                    response_content_type: str = JsonResponseContentType.application_json) -> List[Request]:
    """Filter requests based on the response content type.

    Args:
        requests (:obj:`list` of :obj:`seleniumwire.request.Request`): The list of requests.
        response_content_type (str): The content type of the response.

    Returns:
        seleniumwire.request.Request: The filtered list of requests.

    Raises:
        ValueError: If there are no requests to filter.

    Examples:
        >>> from crawlinsta import webdriver
        >>> driver = webdriver.Chrome()
        >>> driver.get("https://www.instagram.com")
        >>> from crawlinsta.utils import filter_requests
        >>> json_requests = filter_requests(driver.requests)
    """
    result = []
    if not requests:
        logger.error("No requests to filter.")
    for request in requests:
        if not request.response:
            continue
        elif request.response.headers['Content-Type'] != response_content_type:
            continue
        result.append(request)
    return result


def search_request(requests: List[Request],
                   request_url: str,
                   response_content_type: Optional[str] = JsonResponseContentType.application_json,
                   additional_search_func: Optional[Callable] = None,
                   *args, **kwargs) -> Union[int, None]:
    """Search for a request in the list of requests.

    Args:
        requests (:obj:`list` of :obj:`seleniumwire.request.Request`): The list of requests.
        request_url (str): The url to search for.
        response_content_type (Optional[str]): The content type of the response.
        additional_search_func (callable): Additional search function to apply.

    Returns:
        int: The index of the request in the list of requests. If the request is not found, returns None.

    Raises:
        ValueError: If there are no requests to search.
        ValueError: If no response with the specified content type to the url is found.

    Examples:
        >>> from crawlinsta import webdriver
        >>> driver = webdriver.Chrome()
        >>> driver.get("https://www.instagram.com")
        >>> from crawlinsta.utils import search_request
        >>> idx = search_request(driver.requests, "https://www.instagram.com", "application/json; charset=utf-8")
    """
    if not requests:
        logger.error("No requests to search.")
        return None
    for i, request in enumerate(requests):
        if request.url != request_url:
            continue
        elif not request.response:
            continue
        elif 'Content-Type' not in request.response.headers:
            continue
        elif response_content_type and request.response.headers['Content-Type'] != response_content_type:
            continue
        elif additional_search_func and not additional_search_func(request, *args, **kwargs):
            continue
        return i
    logger.error(f"No response with content-type [{response_content_type}] to the url '{request_url}' found.")
    return None


def get_json_data(response: Response) -> Dict[str, Any]:
    """Get the json data from the response.

    Args:
        response (:obj:`list` of :obj:`seleniumwire.request.Response`): The response object.

    Returns:
        Json: The json data from the response.

    Examples:
        >>> from crawlinsta import webdriver
        >>> driver = webdriver.Chrome()
        >>> driver.get("https://www.instagram.com")
        >>> from crawlinsta.utils import get_json_data
        >>> json_data = get_json_data(driver.requests[0].response)
    """
    data = decode(response.body,
                  response.headers.get('Content-Encoding', 'identity'))
    data = json.loads(data)
    return data


def get_media_type(media_type: int, product_type: str) -> str:
    """Determine the media type based on the provided media type and product type.

    Args:
        media_type (int): The numeric identifier representing the media type.
        product_type (str): The type of product (e.g., 'feed', 'igtv', 'clips')
         associated with the media.

    Returns:
        str: A string indicating the determined media type.

    Raises:
        ValueError: If the provided media_type or product_type does not match
        expected values.

    Examples:
        >>> # Determine media type for media_type = 1 and product_type = 'feed'
        >>> media = get_media_type(1, 'feed')  # Returns: "Photo"
        >>> # Determine media type for media_type = 2 and product_type = 'igtv'
        >>> media = get_media_type(2, 'igtv')  # Returns: "IGTV"
        >>> # Determine media type for media_type = 8
        >>> media = get_media_type(8, 'any')  # Returns: "Album"
        >>> # Raises a ValueError for invalid media_type or product_type
        >>> get_media_type(3, 'unknown')  # Raises ValueError
    """
    match media_type:
        case 1:
            return "Photo"
        case 2:
            match product_type:
                case 'feed':
                    return "Video"
                case 'igtv':
                    return "IGTV"
                case 'clips':
                    return "Reel"
                case _:
                    raise ValueError("Invalid product_type")
        case 8:
            return "Album"
        case _:
            raise ValueError("Invalid media_type")


def find_brackets(text: str) -> List[Tuple[int, int]]:
    """Find the brackets in the text.

    Args:
        text (str): The text to search for brackets.

    Returns:
        List[tuple]: The list of tuples containing the start and end indices of the brackets.

    Examples:
        >>> from crawlinsta.utils import find_brackets
        >>> brackets = find_brackets("{{hello}}")
        >>> print(brackets)
        [(0, 7)]
    """
    stack = []
    brackets = []
    for i, char in enumerate(text):
        if char == "{":
            stack.append(i)
        elif char == "}":
            if not stack:
                break
            brackets.append((stack.pop(), i))
    return brackets
