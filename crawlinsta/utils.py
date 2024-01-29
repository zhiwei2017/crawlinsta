import json
from pydantic import Json
from seleniumwire.utils import decode
from seleniumwire.request import Request, Response
from typing import List, Union

JSON_RESPONSE_CONTENT_TYPE = "application/json; charset=utf-8"


def filter_requests(requests: List[Request],
                    response_content_type: str = JSON_RESPONSE_CONTENT_TYPE) -> List[Request]:
    """

    Args:
        requests (:obj:`list` of :obj:`seleniumwire.request.Request`):
        response_content_type (str):

    Returns:
        :obj:`seleniumwire.request.Request`:
    """
    if not requests:
        raise ValueError("No requests to filter.")
    result = []
    for request in requests:
        if not request.response:
            continue
        elif request.response.headers['Content-Type'] != response_content_type:
            continue
        result.append(request)
    return result


def search_request(requests: List[Request],
                   request_url: str,
                   response_content_type: str = JSON_RESPONSE_CONTENT_TYPE) -> Union[int, None]:
    """

    Args:
        requests (:obj:`list` of :obj:`seleniumwire.request.Request`):
        request_url (str):
        response_content_type (str):

    Returns:
        :obj:`seleniumwire.request.Request`:
    """
    if not requests:
        raise ValueError("No requests to search.")
    for i, request in enumerate(requests):
        if request.url != request_url:
            continue
        elif not request.response:
            continue
        elif request.response.headers['Content-Type'] != response_content_type:
            continue
        return i
    raise ValueError(f"No json response to the url '{request_url}' found.")


def get_json_data(response: Response) -> Json:
    """

    Args:
        response (:obj:`list` of :obj:`seleniumwire.request.Response`):

    Returns:
        Json:
    """
    data = decode(response.body,
                  response.headers.get('Content-Encoding', 'identity'))
    data = json.loads(data)
    return data


def get_media_type(media_type: int, product_type: str):
    """
    Determine the media type based on the provided media type and product type.

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
                case other:
                    raise ValueError("Invalid product_type")
        case 8:
            return "Album"
        case other:
            raise ValueError("Invalid media_type")
