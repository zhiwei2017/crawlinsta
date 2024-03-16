from typing import Dict, Any, List, Union
from .schemas import (
    UserProfile,
    Usertag, Location, Caption, Post, MusicBasicInfo
)
from .utils import get_media_type


def extract_id(info_dict: Dict[str, Any]) -> Union[str, int, None]:
    """Extracts the id from the given dictionary.

    Args:
        info_dict (Dict[str, Any]): Dictionary containing the information.

    Returns:
        Union[str, int, None]: The extracted id. If not found, returns None.

    Examples:
        >>> extract_id({"pk": 123})
        123
        >>> extract_id({"id": "123"})
        "123"
        >>> extract_id({})
        None
    """
    return info_dict.get("pk") or info_dict.get("id")


def extract_post_urls(post_info_dict: Dict[str, Any]) -> List[str]:
    """Extracts the post urls from the given post information dictionary.

    Args:
        post_info_dict (Dict[str, Any]): Dictionary containing the post information.

    Returns:
        List[str]: The extracted post urls.

    Examples:
        >>> extract_post_urls({"media_type": 1, "image_versions2": {"candidates": [{"url": "https://example.com"}]})
        ["https://example.com"]
        >>> extract_post_urls({"media_type": 2, "video_versions": [{"url": "https://example.com"}]})
        ["https://example.com"]
        >>> extract_post_urls({"media_type": 8, "carousel_media": [{"image_versions2": {"candidates": [{"url": "https://example.com"}]}}]})
        ["https://example.com"]
    """
    post_urls = []
    if post_info_dict['media_type'] == 2:
        post_urls.append(post_info_dict["video_versions"][-1]["url"])
    elif post_info_dict['media_type'] == 8:
        for media_dict in post_info_dict["carousel_media"]:
            post_urls.append(media_dict["image_versions2"]['candidates'][0]["url"])
    else:
        post_urls.append(post_info_dict["image_versions2"]['candidates'][0]["url"])
    return post_urls


def extract_music_info(music_info_dict: Dict[str, Any]) -> Union[MusicBasicInfo, None]:
    """Extracts the music information from the given dictionary.

    Args:
        music_info_dict (Dict[str, Any]): Dictionary containing the music information.

    Returns:
        Union[MusicBasicInfo, None]: The extracted music information.

    Examples:
        >>> extract_music_info({"music_asset_info": {"audio_cluster_id": 123, "display_artist": "artist", "title": "title", "duration_in_ms": 1000, "progressive_download_url": "https://example.com"}, "music_consumption_info": {"is_trending_in_clips": True}})
        MusicBasicInfo(id=123, is_trending_in_clips=True, artist=UserProfile(fullname="artist"), title="title", duration_in_ms=1000, url="https://example.com")
    """
    artist = None
    if music_info_dict["music_asset_info"].get("display_artist"):
        artist = UserProfile(fullname=music_info_dict["music_asset_info"]["display_artist"])
    music = MusicBasicInfo(id=music_info_dict["music_asset_info"]["audio_cluster_id"],
                           is_trending_in_clips=music_info_dict["music_consumption_info"].get("is_trending_in_clips"),
                           artist=artist,
                           title=music_info_dict["music_asset_info"].get("title"),
                           duration_in_ms=music_info_dict["music_asset_info"].get("duration_in_ms"),
                           url=music_info_dict["music_asset_info"].get("progressive_download_url"))
    return music


def extract_sound_info(sound_info_dict: Dict[str, Any]) -> Union[MusicBasicInfo, None]:
    """Extracts the sound information from the given dictionary.

    Args:
        sound_info_dict (Dict[str, Any]): Dictionary containing the sound information.

    Returns:
        Union[MusicBasicInfo, None]: The extracted sound information.

    Examples:
        >>> extract_sound_info({"audio_asset_id": 123, "consumption_info": {"is_trending_in_clips": True}, "ig_artist": {"pk": 123, "username": "username", "fullname": "fullname", "profile_pic_url": "https://example.com", "is_verified": True, "is_private": False}, "original_audio_title": "title", "duration_in_ms": 1000, "progressive_download_url": "https://example.com"})
        MusicBasicInfo(id=123, is_trending_in_clips=True, artist=UserProfile(id=123, username="username", fullname="fullname", profile_pic_url="https://example.com", is_verified=True, is_private=False), title="title", duration_in_ms=1000, url="https://example.com")
    """
    ig_artist = None
    if sound_info_dict.get("ig_artist"):
        ig_artist = UserProfile(id=extract_id(sound_info_dict["ig_artist"]),
                                username=sound_info_dict["ig_artist"]["username"],
                                fullname=sound_info_dict["ig_artist"].get("fullname"),
                                profile_pic_url=sound_info_dict["ig_artist"].get("profile_pic_url"),
                                is_verified=sound_info_dict["ig_artist"].get("is_verified"),
                                is_private=sound_info_dict["ig_artist"].get("is_private"))
    music = MusicBasicInfo(id=sound_info_dict["audio_asset_id"],
                           is_trending_in_clips=sound_info_dict["consumption_info"].get("is_trending_in_clips"),
                           artist=ig_artist,
                           title=sound_info_dict.get("original_audio_title"),
                           duration_in_ms=sound_info_dict.get("duration_in_ms"),
                           url=sound_info_dict.get("progressive_download_url"))
    return music


def extract_music(post_info_dict: Dict[str, Any]) -> Union[MusicBasicInfo, None]:
    """Extracts the music from the given post information dictionary.

    Args:
        post_info_dict (Dict[str, Any]): Dictionary containing the post information.

    Returns:
        Union[MusicBasicInfo, None]: The extracted music.

    Examples:
        >>> extract_music({"clips_metadata": {"audio_type": "licensed_music", "music_info": {"music_asset_info": {"audio_cluster_id": 123, "display_artist": "artist", "title": "title", "duration_in_ms": 1000, "progressive_download_url": "https://example.com"}, "music_consumption_info": {"is_trending_in_clips": True}}}})
        MusicBasicInfo(id=123, is_trending_in_clips=True, artist=UserProfile(fullname="artist"), title="title", duration_in_ms=1000, url="https://example.com")
        >>> extract_music({"clips_metadata": {"audio_type": "original_sounds", "original_sound_info": {"audio_asset_id": 123, "consumption_info": {"is_trending_in_clips": True}, "ig_artist": {"pk": 123, "username": "username", "fullname": "fullname", "profile_pic_url": "https://example.com", "is_verified": True, "is_private": False}, "original_audio_title": "title", "duration_in_ms": 1000, "progressive_download_url": "https://example.com"}}})
        MusicBasicInfo(id=123, is_trending_in_clips=True, artist=UserProfile(id=123, username="username", fullname="fullname", profile_pic_url="https://example.com", is_verified=True, is_private=False), title="title", duration_in_ms=1000, url="https://example.com")
    """
    metadata = post_info_dict.get("clips_metadata")
    if not metadata:
        return None
    audio_type = metadata.get("audio_type")
    music = None
    match audio_type:
        case "licensed_music":
            music = extract_music_info(metadata["music_info"])
        case "original_sounds":
            music = extract_sound_info(metadata["original_sound_info"])
        case other:
            if metadata.get("music_info"):
                music = extract_music_info(metadata["music_info"])
            elif metadata.get("original_sound_info"):
                music = extract_sound_info(metadata["original_sound_info"])
    return music


def extract_post(post_info_dict: Dict[str, Any]) -> Post:
    """Extracts the post from the given post information dictionary.

    Args:
        post_info_dict (Dict[str, Any]): Dictionary containing the post information.

    Returns:
        Post: The extracted post.

    Examples:
        >>> extract_post({"usertags": {"in": [{"user": {"pk": 123, "username": "username", "full_name": "fullname", "profile_pic_url": "https://example.com", "is_private": False, "is_verified": True}, "position": [0.5, 0.5], "start_time_in_video_in_sec": 0, "duration_in_video_in_sec": 10}]}, "location": {"pk": 123, "short_name": "short_name", "name": "name", "city": "city", "lng": 123, "lat": 123, "address": "address"}, "caption": {"pk": 123, "text": "text", "created_at_utc": 123}, "user": {"pk": 123, "username": "username", "full_name": "fullname", "profile_pic_url": "https://example.com", "is_private": False, "is_verified": True}, "media_type": 1, "product_type": "feed", "taken_at": 123, "has_shared_to_fb": 1, "original_width": 123, "original_height": 123, "image_versions2": {"candidates": [{"url": "https://example.com"}]}, "like_count": 123, "comment_count": 123})
        Post(id=123, code="123", user=UserProfile(id=123, username="username", fullname="fullname", profile_pic_url="https://example.com", is_private=False, is_verified=True), taken_at=123, has_shared_to_fb=True, usertags=[Usertag(user=UserProfile(id=123, username="username", fullname="fullname", profile_pic_url="https://example.com", is_private=False, is_verified=True), position=[0.5, 0.5], start_time_in_video_in_sec=0, duration_in_video_in_sec=10)], media_type="photo", caption=Caption(id=123, text="text", created_at_utc=123), accessibility_caption="text", location=Location(id=123, short_name="short_name", name="name", city="city", lng=123, lat=123, address="address"), original_width=123, original_height=123, urls=["https://example.com"], like_count=123, comment_count=123, music=None)
    """
    usertags = []
    usertags_dict = post_info_dict.get("usertags", dict()) or dict()
    for usertag_info in usertags_dict.get("in", []):
        tagged_user_info = usertag_info["user"]
        tagged_user = UserProfile(id=extract_id(tagged_user_info),
                                  username=tagged_user_info["username"],
                                  fullname=tagged_user_info.get("full_name"),
                                  profile_pic_url=tagged_user_info.get("profile_pic_url"),
                                  is_private=tagged_user_info.get("is_private"),
                                  is_verified=tagged_user_info.get("is_verified"))
        usertag = Usertag(user=tagged_user,
                          position=usertag_info.get("position"),
                          start_time_in_video_in_sec=usertag_info.get("start_time_in_video_in_sec"),
                          duration_in_video_in_sec=usertag_info.get("duration_in_video_in_sec"))
        usertags.append(usertag)

    location = post_info_dict.get("location")
    if location:
        location = Location(id=extract_id(location),
                            short_name=location.get("short_name"),
                            name=location["name"],
                            city=location.get("city"),
                            lng=location.get("lng"),
                            lat=location.get("lat"),
                            address=location.get("address"))

    caption = post_info_dict.get("caption")
    default_accessibility_caption = ""
    if caption:
        caption = Caption(id=extract_id(caption),
                          text=caption.get("text"),
                          created_at_utc=caption.get("created_at_utc"))
        default_accessibility_caption = caption.text

    owner = post_info_dict["user"]
    user = UserProfile(id=extract_id(owner),
                       username=owner.get("username"),
                       fullname=owner.get("full_name"),
                       profile_pic_url=owner.get("profile_pic_url"),
                       is_private=owner.get("is_private"),
                       is_verified=owner.get("is_verified"))

    music = extract_music(post_info_dict)
    media_type = get_media_type(post_info_dict['media_type'], post_info_dict['product_type'])
    post_urls = extract_post_urls(post_info_dict)
    post = Post(id=extract_id(post_info_dict),
                code=post_info_dict['code'],
                user=user,
                taken_at=post_info_dict.get('taken_at'),
                has_shared_to_fb=bool(post_info_dict.get('has_shared_to_fb')),
                usertags=usertags,
                media_type=media_type,
                caption=caption,
                accessibility_caption=post_info_dict.get("accessibility_caption", default_accessibility_caption),
                location=location,
                original_width=post_info_dict['original_width'],
                original_height=post_info_dict['original_height'],
                urls=post_urls,
                like_count=post_info_dict.get('like_count'),
                comment_count=post_info_dict.get('comment_count'),
                music=music)
    return post
