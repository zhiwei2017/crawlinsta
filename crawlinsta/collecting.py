from pydantic import Json
from .schemas import (
    UserInfo, Users, Likers, Comments, Medias, Hashtag, SearchingResult
)


def collect_user_info(username: str) -> Json:
    """Collect user information through username, including user_id, username,
    profile_pic_url, biography, media_count, follower_count, following_count,
    medias.

    Strategy: click the username, get to the main page of the user, the user
    information is returned in the response body.

    Alternatively, put the mouse over the user's name in home page, the user
    information will show in a popup. A request triggered by the mouseover was
    sent to the path `/api/v1/users/<user_id>/info/` or
    `/api/v1/users/web_profile_info/?username=<user_name>`

    Args:
        username (str): name of the user.

    Returns:
        Json: user information in json format.
    """
    return UserInfo().model_dump(mode="json")


def collect_medias_of_user(username: str) -> Json:
    """Collect medias of the given user.

    Strategy: click the username, get to the main page of the user, a few medias
    are displayed in the user's main page. The request was sent to the path
    `/api/v1/feed/user/<user_name>/username/?count=6` to get the medias and a
    next_max_id for loading other medias. To load the other medias, move the mouse
    to the bottom of the page, it will trigger another request sent to
    `/api/v1/feed/user/<user_id>/?count=12&max_id=<next_max_id>`
    to have more medias.

    Args:
        username (str): name of the user.

    Returns:
        Json: all visible followers' user information of the given user in json format.
    """
    return Medias().model_dump(mode="json")


def collect_followers_of_user(username: str) -> Json:
    """Collect followers of the given user.

    Strategy: click the username, get to the main page of the user, then click followers, a list of
    followers of the user shows in a popup. A request triggered by the clicking was sent to the path
    `/api/v1/friendships/<user_id>/followers/?count=12&search_surface=follow_list_page`.

    Args:
        username (str): name of the user.

    Returns:
        Json: all visible followers' user information of the given user in json format.
    """
    return Users().model_dump(mode="json")


def collect_following_of_user(username: str) -> Json:
    """Collect following of the given user.

    Strategy: click the username, get to the main page of the user, then click following, a list of
    following of the user shows in a popup. A request triggered by the clicking was sent to the path
    `/api/v1/friendships/373735170/following/?count=12`.

    Args:
        username (str): name of the user.

    Returns:
        Json: all visible followings' user information of the given user in json format.
    """
    return Users().model_dump(mode="json")


def collect_likers_of_media(media_code: str) -> Json:
    """Collect the users, who likes a given media.

    Strategy: click the likes (a button with link `/p/<media_code>/liked_by/`), a list of likers shows in a popup.
    A request triggered by the clicking was sent to the path `/api/v1/media/<media_id>/likers/`

    Args:
        media_code (str): media short code for generating access url.

    Returns:
        Json: all likers' user information of the given media in json format.
    """
    return Likers().model_dump(mode="json")


def collect_comments_of_media(media_code: str) -> Json:
    """Collect comments of a given media.

    Strategy: click the media (a button with link `/p/<media_code>/`), a list of
    comments shows in a popup. A request triggered by the clicking was sent to the path
    `/api/v1/media/<media_id>/comments/?can_support_threading=true&permalink_enabled=false`
    The comments are paginated, to load more comments, have to use the mouse to click
    a button to load more comments.

    Args:
        media_code (str): media short code for generating access url.

    Returns:
        Json: all comments of the given media in json format.
    """
    return Comments().model_dump(mode="json")


def search_with_keyword(keyword: str) -> Json:
    """Search hashtags or users with given keyword.

    Args:
        keyword (str): keyword for searching.

    Returns:
        Json: found users/hashtags.
    """
    return SearchingResult().model_dump(mode="json")


def collect_hashtag_top_medias(hashtag: str) -> Json:
    """Collect top medias of a given hashtag.

    Strategy: click the search button from the left navigation bar, and input the hashtag in
    the searchbar, and select the desired hashtag from searching results. This action will
    trigger a request sent to the path `/api/v1/tags/web_info/?tag_name=<tag name>`, as result
    the top medias are showed.

    Args:
        hashtag (str): hashtag.

    Returns:
        Json: Hashtag information in a json format.
    """
    return Hashtag().model_dump(mode="json")