from crawlinsta.data_extraction import (
    extract_id, extract_post_urls, extract_music_info, extract_sound_info,
    extract_music, extract_post, create_users_list
)


def test_extract_id():
    assert extract_id({"id": "123"}) == "123"
    assert extract_id({"id": 123}) == 123
    assert extract_id({"pk": "123", "id": "123"}) == "123"
    assert extract_id({"pk": 123, "id": 123}) == 123


def test_extract_post_urls():
    post_info_dict = {
        "media_type": 1,
        "image_versions2": {
            "candidates": [
                {"url": "https://www.instagram.com/p/1234567890"},
                {"url": "https://www.instagram.com/p/1234567891"}
            ]
        }
    }
    assert extract_post_urls(post_info_dict) == ["https://www.instagram.com/p/1234567890"]

    post_info_dict = {
        "media_type": 2,
        "video_versions": [
            {"url": "https://www.instagram.com/p/1234567889"},
            {"url": "https://www.instagram.com/p/1234567890"}
        ]
    }
    assert extract_post_urls(post_info_dict) == ["https://www.instagram.com/p/1234567890"]

    post_info_dict = {
        "media_type": 8,
        "carousel_media": [
            {
                "image_versions2": {
                    "candidates": [
                        {"url": "https://www.instagram.com/p/1234567890"}
                    ]
                }
            },
            {
                "image_versions2": {
                    "candidates": [
                        {"url": "https://www.instagram.com/p/1234567891"}
                    ]
                }
            },
            {
                "image_versions2": {
                    "candidates": [
                        {"url": "https://www.instagram.com/p/1234567892"}
                    ]
                }
            }
        ]
    }
    assert extract_post_urls(post_info_dict) == ["https://www.instagram.com/p/1234567890",
                                                 "https://www.instagram.com/p/1234567891",
                                                 "https://www.instagram.com/p/1234567892"]


def test_extract_music_info():
    music_info_dict = {
        "music_asset_info": {
            "audio_cluster_id": "1234567890",
            "title": "music title",
            "duration_in_ms": 1000,
            "progressive_download_url": "https://www.instagram.com/p/1234567890",
            "display_artist": "fullname"
        },
        "music_consumption_info": {
            "is_trending_in_clips": True,
        }
    }
    music = extract_music_info(music_info_dict)
    assert music.id == "1234567890"
    assert music.is_trending_in_clips is True
    assert music.artist.id is None
    assert music.artist.username == ""
    assert music.artist.fullname == "fullname"
    assert music.artist.profile_pic_url == ""
    assert music.artist.is_verified is None
    assert music.artist.is_private is None
    assert music.title == "music title"
    assert music.duration_in_ms == 1000
    assert music.url == "https://www.instagram.com/p/1234567890"

    music_info_dict = {
        "music_asset_info": {
            "audio_cluster_id": "1234567890",
            "title": "music title",
            "duration_in_ms": 1000,
        },
        "music_consumption_info": {
            "is_trending_in_clips": True,
        }
    }
    music = extract_music_info(music_info_dict)
    assert music.id == "1234567890"
    assert music.is_trending_in_clips is True
    assert music.artist is None
    assert music.title == "music title"
    assert music.duration_in_ms == 1000
    assert music.url is None


def test_extract_sound_info():
    sound_info_dict = {
        "audio_asset_id": "1234567890",
        "original_audio_title": "Original audio",
        "duration_in_ms": 1000,
        "progressive_download_url": "https://www.instagram.com/p/1234567890",
        "consumption_info": {
            "is_trending_in_clips": True
        },
        "ig_artist": {
            "id": "1234567890",
            "username": "username",
        }
    }
    music = extract_sound_info(sound_info_dict)
    assert music.id == "1234567890"
    assert music.is_trending_in_clips is True
    assert music.artist.id == "1234567890"
    assert music.artist.username == "username"
    assert music.artist.fullname == ""
    assert music.artist.profile_pic_url == ""
    assert music.artist.is_verified is None
    assert music.artist.is_private is None
    assert music.title == "Original audio"
    assert music.duration_in_ms == 1000
    assert music.url == "https://www.instagram.com/p/1234567890"

    sound_info_dict = {
        "audio_asset_id": "1234567890",
        "original_audio_title": "music title",
        "duration_in_ms": 1000,
        "consumption_info": {
            "is_trending_in_clips": True
        },
        "ig_artist": None
    }
    music = extract_sound_info(sound_info_dict)
    assert music.id == "1234567890"
    assert music.is_trending_in_clips is True
    assert music.artist is None
    assert music.title == "music title"
    assert music.duration_in_ms == 1000
    assert music.url is None


def test_extract_music():
    post_info_dict = {
        "media_type": 2,
        "product_type": "clips",
        "clips_metadata": {
            "audio_type": "licensed_music",
            "music_info": {
                "music_asset_info": {
                    "audio_cluster_id": "1234567890",
                    "title": "music title",
                    "duration_in_ms": 1000,
                    "progressive_download_url": "https://www.instagram.com/p/1234567890",
                    "display_artist": "fullname"
                },
                "music_consumption_info": {
                    "is_trending_in_clips": True,
                }
            }
        }
    }
    music = extract_music(post_info_dict)
    assert music.id == "1234567890"
    assert music.is_trending_in_clips is True
    assert music.artist.id == None
    assert music.artist.username == ""
    assert music.artist.fullname == "fullname"
    assert music.artist.profile_pic_url == ""
    assert music.artist.is_verified is None
    assert music.artist.is_private is None
    assert music.title == "music title"
    assert music.duration_in_ms == 1000
    assert music.url == "https://www.instagram.com/p/1234567890"

    post_info_dict = {
        "media_type": 2,
        "product_type": "clips",
        "clips_metadata": {
            "audio_type": "original_sounds",
            "original_sound_info": {
                "audio_asset_id": "1234567890",
                "original_audio_title": "music title",
                "duration_in_ms": 1000,
                "progressive_download_url": "https://www.instagram.com/p/1234567890",
                "consumption_info": {
                    "is_trending_in_clips": True
                },
                "ig_artist": {
                    "id": "1234567890",
                    "username": "username",
                    "fullname": "fullname",
                    "profile_pic_url": "https://www.instagram.com/p/1234567890",
                    "is_verified": True,
                    "is_private": False
                }
            }
        }
    }

    music = extract_music(post_info_dict)
    assert music.id == "1234567890"
    assert music.is_trending_in_clips is True
    assert music.artist.id == "1234567890"
    assert music.artist.username == "username"
    assert music.artist.fullname == "fullname"
    assert music.artist.profile_pic_url == "https://www.instagram.com/p/1234567890"
    assert music.artist.is_verified is True
    assert music.artist.is_private is False
    assert music.title == "music title"
    assert music.duration_in_ms == 1000
    assert music.url == "https://www.instagram.com/p/1234567890"

    post_info_dict = {
        "media_type": 8,
        "product_type": "album",
        "clips_metadata": {
            "music_info": {
                "music_asset_info": {
                    "audio_cluster_id": "1234567890",
                    "title": "music title",
                    "duration_in_ms": 1000,
                    "progressive_download_url": "https://www.instagram.com/p/1234567890",
                    "display_artist": "fullname"
                },
                "music_consumption_info": {
                    "is_trending_in_clips": True,
                }
            }
        }
    }
    music = extract_music(post_info_dict)
    assert music.id == "1234567890"
    assert music.is_trending_in_clips is True
    assert music.artist.id is None
    assert music.artist.username == ""
    assert music.artist.fullname == "fullname"
    assert music.artist.profile_pic_url == ""
    assert music.artist.is_verified is None
    assert music.artist.is_private is None
    assert music.title == "music title"
    assert music.duration_in_ms == 1000
    assert music.url == "https://www.instagram.com/p/1234567890"

    post_info_dict = {
        "media_type": 8,
        "product_type": "album",
        "clips_metadata": {
            "original_sound_info": {
                "audio_asset_id": "1234567890",
                "original_audio_title": "music title",
                "duration_in_ms": 1000,
                "progressive_download_url": "https://www.instagram.com/p/1234567890",
                "consumption_info": {
                    "is_trending_in_clips": True
                },
                "ig_artist": {
                    "id": "1234567890",
                    "username": "username",
                    "fullname": "fullname",
                    "profile_pic_url": "https://www.instagram.com/p/1234567890",
                    "is_verified": True,
                    "is_private": False
                }
            }
        }
    }

    music = extract_music(post_info_dict)
    assert music.id == "1234567890"
    assert music.is_trending_in_clips is True
    assert music.artist.id == "1234567890"
    assert music.artist.username == "username"
    assert music.artist.fullname == "fullname"
    assert music.artist.profile_pic_url == "https://www.instagram.com/p/1234567890"
    assert music.artist.is_verified is True
    assert music.artist.is_private is False
    assert music.title == "music title"
    assert music.duration_in_ms == 1000
    assert music.url == "https://www.instagram.com/p/1234567890"


def test_extract_post():
    post_info_dict = {
        "media_type": 2,
        "product_type": "clips",
        "video_versions": [
            {"url": "https://www.instagram.com/p/1234567889"},
            {"url": "https://www.instagram.com/p/1234567890"}
        ],
        "clips_metadata": {
            "audio_type": "licensed_music",
            "music_info": {
                "music_asset_info": {
                    "audio_cluster_id": "1234567890",
                    "title": "music title",
                    "duration_in_ms": 1000,
                    "progressive_download_url": "https://www.instagram.com/p/1234567890",
                    "display_artist": "fullname"
                },
                "music_consumption_info": {
                    "is_trending_in_clips": True,
                }
            }
        },
        "user": {
            "id": "1234567890",
            "username": "username",
            "full_name": "fullname",
            "profile_pic_url": "https://www.instagram.com/p/1234567890",
            "is_verified": True,
            "is_private": False
        },
        "usertags": {
            "in": [
                {
                    "user": {
                        "id": "1234567890",
                        "username": "username",
                        "full_name": "fullname",
                        "profile_pic_url": "https://www.instagram.com/p/1234567890",
                        "is_verified": True,
                        "is_private": False
                    },
                    "position": [0.0, 0.0],
                    "start_time_in_video_in_sec": 0.0,
                    "duration_in_video_in_sec": 0.0
                }
            ]
        },
        "caption": {
            "id": "123456",
            "text": "caption"
        },
        "like_count": 1000,
        "comment_count": 100,
        "taken_at": 1612345678,
        "id": "1234567890",
        "code": "1234567890",
        "location": {
            "id": "1234567890",
            "name": "location",
            "short_name": "location",
            "address": "address",
            "city": "city",
            "lng": 123.456,
            "lat": 123.456
        },
        "has_shared_to_fb": True,
        "accessibility_caption": "accessibility_caption",
        "original_height": 1080,
        "original_width": 1080
    }
    post = extract_post(post_info_dict)
    assert post.id == "1234567890"
    assert post.code == "1234567890"
    assert post.user.id == "1234567890"
    assert post.user.username == "username"
    assert post.user.fullname == "fullname"
    assert post.user.profile_pic_url == "https://www.instagram.com/p/1234567890"
    assert post.user.is_verified is True
    assert post.user.is_private is False
    assert post.caption.id == "123456"
    assert post.caption.text == "caption"
    assert post.like_count == 1000
    assert post.comment_count == 100
    assert post.taken_at == 1612345678
    assert post.has_shared_to_fb is True
    assert post.accessibility_caption == "accessibility_caption"
    assert post.original_height == 1080
    assert post.original_width == 1080
    assert post.location.id == "1234567890"
    assert post.location.name == "location"
    assert post.location.short_name == "location"
    assert post.location.address == "address"
    assert post.location.city == "city"
    assert post.location.lng == 123.456
    assert post.location.lat == 123.456
    assert post.urls == ["https://www.instagram.com/p/1234567890"]
    assert post.media_type == "Reel"
    assert post.music.id == "1234567890"
    assert post.music.is_trending_in_clips is True
    assert post.music.artist.id is None
    assert post.music.artist.username == ""
    assert post.music.artist.fullname == "fullname"
    assert post.music.artist.profile_pic_url == ""
    assert post.music.artist.is_verified is None
    assert post.music.artist.is_private is None
    assert post.music.title == "music title"
    assert post.music.duration_in_ms == 1000
    assert post.music.url == "https://www.instagram.com/p/1234567890"
    assert len(post.usertags) == 1
    assert post.usertags[0].user.id == "1234567890"
    assert post.usertags[0].user.username == "username"
    assert post.usertags[0].user.fullname == "fullname"
    assert post.usertags[0].user.profile_pic_url == "https://www.instagram.com/p/1234567890"
    assert post.usertags[0].user.is_verified is True
    assert post.usertags[0].user.is_private is False
    assert post.usertags[0].position == [0.0, 0.0]
    assert post.usertags[0].start_time_in_video_in_sec == 0.0
    assert post.usertags[0].duration_in_video_in_sec == 0.0


def test_create_users_list():
    user_info_list = [
        {"users": []},
        {"users": [
            {
                "id": "1234567890",
                "username": "username",
                "full_name": "fullname",
                "profile_pic_url": "https://www.instagram.com/p/1234567890",
                "is_verified": True,
                "is_private": False
            },
            {
                "pk": "1234567891",
                "username": "username1",
                "full_name": "fullname1",
                "profile_pic_url": "https://www.instagram.com/p/1234567891",
                "is_verified": False,
                "is_private": True
            }
        ]}
    ]
    users = create_users_list(user_info_list)
    assert len(users) == 2
    assert users[0].id == "1234567890"
    assert users[0].username == "username"
    assert users[0].fullname == "fullname"
    assert users[0].profile_pic_url == "https://www.instagram.com/p/1234567890"
    assert users[0].is_verified is True
    assert users[0].is_private is False
    assert users[1].id == "1234567891"
    assert users[1].username == "username1"
    assert users[1].fullname == "fullname1"
    assert users[1].profile_pic_url == "https://www.instagram.com/p/1234567891"
    assert users[1].is_verified is False
    assert users[1].is_private is True
