from pydantic import Json
from .schemas import (
    UserInfo, Users, Likers, Comments, Posts, Hashtag, SearchingResult,
    FriendshipStatus
)


def collect_user_info(username: str) -> Json:
    """Collect user information through username, including user_id, username,
    profile_pic_url, biography, post_count, follower_count, following_count.

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


def collect_posts_of_user(username: str, n: int = 100) -> Json:
    """Collect n posts of the given user.

    Strategy: click the username, get to the main page of the user, a few posts
    are displayed in the user's main page. The request was sent to the path
    `/api/v1/feed/user/<user_name>/username/?count=6` to get the posts and a
    next_max_id for loading other posts. To load the other posts, move the mouse
    to the bottom of the page, it will trigger another request sent to
    `/api/v1/feed/user/<user_id>/?count=12&max_id=<next_max_id>`
    to have more posts.

    Args:
        username (str): name of the user.
        n (int): maximum number of posts, which should be collected. By default,
         it's 100. If it's set to 0, collect all posts.

    Returns:
        Json: all visible post of the given user in json format.
    """
    return Posts().model_dump(mode="json")


def collect_reels_of_user(username: str, n: int = 100) -> Json:
    """Collect n reels of the given user.

    Strategy: click the username, get to the main page of the user, a few posts
    are displayed in the user's main page. Click the button reels to see all the
    reels from the user.The request was sent to the path
    `/api/v1/feed/user/<user_name>/username/?count=6` to get the posts/reels and a
    next_max_id for loading other posts/reels. To load the other posts/reels,
    move the mouse to the bottom of the page, it will trigger another request sent to
    `/api/v1/feed/user/<user_id>/?count=12&max_id=<next_max_id>`
    to have more posts/reels.

    Args:
        username (str): name of the user.
        n (int): maximum number of reels, which should be collected. By default,
         it's 100. If it's set to 0, collect all posts.

    Returns:
        Json: all visible reels user information of the given user in json format.
    """
    return Posts().model_dump(mode="json")


def collect_user_tagged_posts(username: str, n: int = 100) -> Json:
    """Collect n posts in which user was tagged.

    Strategy: click the username, get to the main page of the user, a few posts
    are displayed in the user's main page. Click the button tagged to see all the
    posts in which the user was tagged.The request was sent to the path
    `/<user_name>/tagged/` to get the tagged posts/reels and a next_max_id for
    loading other posts/reels. To load the other posts/reels, move the mouse to
    the bottom of the page, it will trigger another request sent to the path
    /graphql/query/?doc_id=<tagged_user_id>&variables=<next_max_id>

    Args:
        username (str): name of the user.
        n (int): maximum number of tagged posts, which should be collected. By
         default, it's 100. If it's set to 0, collect all posts.

    Returns:
        Json: all visible tagged posts in json format.
    """
    return Posts().model_dump(mode="json")


def get_friendship_status(username1: str, username2: str) -> Json:
    """Get the relationship between any two users.

    Strategy: the only way to do it is to check if user_A is contained in
    user_B's followings or followers.

    Args:
        username1 (str): username of the person A.
        username2 (str): username of the person B.

    Returns:
        Json: friendship indication between person A and person B.
    """
    return FriendshipStatus().model_dump(mode="json")


def collect_followers(username: str, n: int = 100) -> Json:
    """Collect n followers of the given user.

    Strategy: click the username, get to the main page of the user, then click followers, a list of
    followers of the user shows in a popup. A request triggered by the clicking was sent to the path
    `/api/v1/friendships/<user_id>/followers/?count=12&search_surface=follow_list_page`.

    Args:
        username (str): name of the user.
        n (int): maximum number of followers, which should be collected. By default,
         it's 100. If it's set to 0, collect all followers.

    Returns:
        Json: all visible followers' user information of the given user in json format.
    """
    return Users().model_dump(mode="json")


def collect_followings(username: str, n: int = 100) -> Json:
    """Collect n followings of the given user.

    Strategy: click the username, get to the main page of the user, then click following, a list of
    following of the user shows in a popup. A request triggered by the clicking was sent to the path
    `/api/v1/friendships/373735170/following/?count=12`.

    Args:
        username (str): name of the user.
        n (int): maximum number of followings, which should be collected. By default,
         it's 100. If it's set to 0, collect all followings.

    Returns:
        Json: all visible followings' user information of the given user in json format.
    """
    return Users().model_dump(mode="json")


def collect_likers_of_post(post_id: str, n: int = 100) -> Json:
    """Collect the users, who likes a given post.

    Strategy: click the likes (a button with link `/p/<post_code>/liked_by/`), a
    list of likers shows in a popup.
    A request triggered by the clicking was sent to the path `/api/v1/post/<post_id>/likers/`

    Args:
        post_id (str): id of the post for collecting.
        n (int): maximum number of likers, which should be collected. By default,
         it's 100. If it's set to 0, collect all likers.

    Returns:
        Json: all likers' user information of the given post in json format.
    """
    return Likers().model_dump(mode="json")


def collect_comments(post_id: str, n: int = 100) -> Json:
    """Collect n comments of a given post.

    Strategy: click the post (a button with link `/p/<post_code>/`), a list of
    comments shows in a popup. A request triggered by the clicking was sent to the path
    `/api/v1/post/<post_id>/comments/?can_support_threading=true&permalink_enabled=false`
    The comments are paginated, to load more comments, have to use the mouse to click
    a button to load more comments.

    Args:
        post_id (str): id of the post, whose comments will be collected.
        n (int): maximum number of comments, which should be collected. By default,
         it's 100. If it's set to 0, collect all comments.

    Returns:
        Json: all comments of the given post in json format.
    """
    return Comments().model_dump(mode="json")


def search_with_keyword(keyword: str, pers: bool) -> Json:
    """Search hashtags or users with given keyword.

    Args:
        keyword (str): keyword for searching.
        pers (bool): indicating whether results should be personalized or not.

    Returns:
        Json: found users/hashtags.
    """
    return SearchingResult().model_dump(mode="json")


def collect_hashtag_top_posts(hashtag: str) -> Json:
    """Collect top posts of a given hashtag.

    Strategy: click the search button from the left navigation bar, and input the hashtag in
    the searchbar, and select the desired hashtag from searching results. This action will
    trigger a request sent to the path `/api/v1/tags/web_info/?tag_name=<tag name>`, as result
    the top posts are showed.

    Args:
        hashtag (str): hashtag.

    Returns:
        Json: Hashtag information in a json format.
    """
    return Hashtag().model_dump(mode="json")


def collect_posts_by_music_id(music_id: str) -> Json:
    """Search for all posts containing the given music_id.

    Strategy: the only way to collect the posts using the same music, is to first find
    a post with this music, then click the link "original audio" to get all the posts
    using this music.

    The request was sent to the path /reels/audio/<music_id>/.

    Args:
        music_id (str): id of the music.

    Returns:
        Json: a list of posts containing the music.
    """
    return Posts().model_dump(mode="json")


def download_media(media_url: str, path: str) -> None:
    """Download the image/video based on the given media_url, and store it to
    the given path.

    Args:
        media_url (str): url of the media for downloading.
        path (str): path for storing the downloaded media..
    """
    pass
