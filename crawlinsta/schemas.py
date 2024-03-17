from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Union
import typing_extensions


class PreferDefaultsModel(BaseModel):
    """
    Pydantic model that will use default values in place of an explicitly passed `None` value.
    This is helpful when consuming APIs payloads which may explicitly define a field as `null`
    rather than omitting it.
    """

    def _field_allows_none(self, field_name):
        """
        Returns True if the field is exists in the model's __fields__ and it's allow_none property is True.
        Returns False otherwise.
        """
        field = self.model_fields.get(field_name)
        if field is None:
            return False
        allow_none = type(None) in typing_extensions.get_args(field.annotation)
        return allow_none

    def __init__(self, **data):
        """
        Removes any fields from the data which are None and are not allowed to be None.
        The results are then passed to the super class's init method.
        """
        data_without_null_fields = {k: v for k, v in data.items() if (
            v is not None or self._field_allows_none(k)
        )}
        super().__init__(**data_without_null_fields)


class UserBasicInfo(BaseModel):
    """User basic information, contains `id`, `username`."""
    model_config = ConfigDict(coerce_numbers_to_str=True)

    id: Optional[str] = Field(None,
                              description="unique identifier if an user. It's 9 digits in string format.",
                              examples=["387381865"])
    username: str = Field("",
                          description="It's limited to 30 characters and must contain only "
                                      "letters in lowercase, numbers, periods, and underscores."
                                      "It's the unique identifier for the user besides the user id,"
                                      "which is generated by instagram automatically.",
                          examples=["dummy_user"])


class UserProfile(PreferDefaultsModel, UserBasicInfo):
    """User basic information, contains `id`, `username`, `fullname`, `profile_pic_url` and `is_verified`."""
    fullname: str = Field("",
                          description="It's limited to 30 characters and must contain only "
                                      "letters, numbers, periods, underscores and spaces.",
                          examples=["Dummy User"])
    profile_pic_url: str = Field("",
                                 description="Url of the profile picture for downloading. "
                                             "The generated link is usually available only for couple hours.",
                                 examples=["https://dummy-pic.com"])
    is_private: Optional[bool] = Field(None,
                                       description="Indicates that the user account is private or public."
                                                   "Please check https://help.instagram.com/448523408565555"
                                                   "for detailed information.",
                                       examples=[False])
    is_verified: Optional[bool] = Field(None,
                                        description="Indicates whether the user account is verified as "
                                                    "business/official account or not.",
                                        examples=[False])


class UserEngagementInfo(PreferDefaultsModel):
    """User engagement information, contains mainly about the interactions between the given user with
    other users or posts. It contains fields like `follower_count`, `following_count`, `following_tag_count`,
    `post_count`."""
    follower_count: int = Field(0,
                                description="Number of the followers.",
                                examples=[10])
    following_count: int = Field(0,
                                 description="Number of the following.",
                                 examples=[10])
    following_tag_count: int = Field(0,
                                     description="Number of the tags, which are followed by the user.",
                                     examples=[0])
    post_count: int = Field(0,
                            description="Number of the posts of the user.",
                            examples=[20])


class UserInfo(UserProfile, UserEngagementInfo):
    """User information contains `id`, `username`, `full name`, `biography` and son on ."""
    biography: str = Field("",
                           description="A short description of the user account.",
                           examples=["Hello, welcome to my instagram."])


class Users(PreferDefaultsModel):
    """An aggregation class to have the field `users` for storing a list of
    instances of `UserInfo`."""
    users: List[UserProfile] = Field([],
                                     description="A list of user information.",
                                     examples=[[UserProfile(id="387381865",
                                                            username="dummy_user",
                                                            fullname="Dummy User",
                                                            profile_pic_url="https://dummy-pic.com",
                                                            is_verified=False,
                                                            is_private=False)]])
    count: int = Field(0,
                       description="Number of users contained.",
                       examples=[100])


class FriendshipStatus(PreferDefaultsModel):
    """Describe the relationship between the liker and the post owner. """
    following: Optional[bool] = Field(None,
                                      description="Does the liker follow the post owner?",
                                      examples=[False])
    followed_by: Optional[bool] = Field(False,
                                        description="Does the post owner follow the liker?",
                                        examples=[False])


class Comment(PreferDefaultsModel):
    """Relevant information about a comment, including `id`, `user_id`, `post_id`
    `type` etc."""
    model_config = ConfigDict(coerce_numbers_to_str=True)

    id: Optional[str] = Field(...,
                              description="Unique identifier of the comment. It consists of 17 digits.",
                              examples=["18016617763686865"])
    user: UserBasicInfo = Field(...,
                                description="User, who made the comment.",
                                examples=[UserBasicInfo(id="387381865",
                                                        username="dummy_user")])
    post_id: str = Field(...,
                         description="Id reference to the post.",
                         examples=["3194677555662724330"])
    created_at_utc: Optional[int] = Field(None,
                                          description="Timestamp of when the comment was made.",
                                          examples=[1695060863])
    status: Optional[str] = Field(None,
                                  description="Status of the comment, Active or Inactive. The inactive comments "
                                              "refers to the comments which are hidden by the post owner with certain"
                                              "conditions, such as filtered with certain words, default spam filter, or"
                                              "manually controlled by the post owner.",
                                  examples=["Active"])
    share_enabled: Optional[bool] = Field(None,
                                          description="Is the comment enabled for sharing? Generally all the visible "
                                                      "commends are legit for sharing, only the hidden commends are "
                                                      "not enabled for sharing. This is a duplicated feature "
                                                      "of status.",
                                          examples=[True])
    is_ranked_comment: Optional[bool] = Field(None,
                                              description="Is the comment a ranked one? The Instagram comments feature "
                                                          "is set up in such a way that it shows first the comments of "
                                                          "people you follow. Or, sometimes, a comment by a verified "
                                                          "account or a comment that is most liked shows up first.",
                                              examples=[True])
    text: str = Field("",
                      description="Comment content in free text format. The Instagram comment character "
                                  "limit is also 2200 characters, just like the caption. Instagram comments"
                                  " can only contain up to 30 hashtags.",
                      examples=["Cool stuff!"])
    has_translation: bool = Field(False,
                                  description="Does the comment have a translation? "
                                              "Captions and comments on posts in feed, "
                                              "as well as the bio that you include on your profile, "
                                              "are translated automatically based on the language "
                                              "they're written in and the language settings of the "
                                              "person viewing it. If your language is available as a "
                                              "translation, you can tap See translation below the text "
                                              "to see it.",
                                  examples=[True])
    is_liked_by_post_owner: Optional[bool] = Field(None,
                                                   description="Is the comment liked by the post owner?",
                                                   examples=[True])
    comment_like_count: int = Field(0,
                                    description="Number of people liked the comment.",
                                    examples=[1])


class Comments(PreferDefaultsModel):
    """An aggregation of comments."""
    comments: List[Comment] = Field([],
                                    description="A list of comments.",
                                    examples=[[Comment(id="18016617763686865",
                                                       user=UserBasicInfo(id="387381865",
                                                                          username="dummy_user"),
                                                       post_id="3194677555662724330",
                                                       created_at_utc=1695060863,
                                                       status="Active",
                                                       share_enabled=True,
                                                       is_ranked_comment=True,
                                                       text="Cool Stuff!",
                                                       has_translation=False,
                                                       is_liked_by_post_owner=True,
                                                       comment_like_count=1)]])
    count: int = Field(0,
                       description="Number of comments contained.",
                       examples=[100])


class Usertag(PreferDefaultsModel):
    """Usertag information, mainly about who is tagged at which position at what time
    in video and how long the tagged user appears."""
    user: UserProfile = Field(...,
                              description="User who is tagged in the post.",
                              examples=[UserProfile(id="387381865",
                                                    username="dummy_user",
                                                    fullname="Dummy User",
                                                    profile_pic_url="https://dummy-pic.com",
                                                    is_verified=False,
                                                    is_private=None)])
    position: Optional[List[float]] = Field(None,
                                            description="A list of two floats, which is "
                                                        "used to identify the position of "
                                                        "the tagged user in the post.",
                                            examples=[[0.6794871795, 0.7564102564]])
    start_time_in_video_in_sec: Optional[float] = Field(None,
                                                        description="Start time in video in seconds "
                                                                    "when the tagged user shows up",
                                                        examples=[None])
    duration_in_video_in_sec: Optional[float] = Field(None,
                                                      description="Duration in the video in seconds, "
                                                                  "when the tagged user shows up",
                                                      examples=[None])


class LocationBasicInfo(PreferDefaultsModel):
    """Location information, contains location name, city, longitude, latitude and
     address etc. The location information is provided by the post owner, while
     creating/editing the post."""
    model_config = ConfigDict(coerce_numbers_to_str=True)

    id: Optional[str] = Field(...,
                              description="Unique identifier of the location.",
                              examples=["1107837019238536"])
    name: str = Field(...,
                      description="Full name of the location.",
                      examples=["Kedrodasos Beach"])


class Location(LocationBasicInfo):
    """Location information, contains location name, city, longitude, latitude and
     address etc. The location information is provided by the post owner, while
     creating/editing the post."""
    short_name: str = Field("",
                            description="Short name of the location",
                            examples=["Kedro-beach"])
    city: str = Field("",
                      description="to which city the location belongs",
                      examples=["Kántanos, Khania, Greece"])
    lng: Optional[float] = Field(None,
                                 description="Longitude of the location.",
                                 examples=[23.5619])
    lat: Optional[float] = Field(None,
                                 description="Latitude of the location.",
                                 examples=[35.26861])
    address: str = Field("",
                         description="Address of the location. Typically is empty.",
                         examples=[""])


class Caption(PreferDefaultsModel):
    """Caption of the post."""
    model_config = ConfigDict(coerce_numbers_to_str=True)

    id: Optional[str] = Field(None,
                              description="Unique identifier of the caption.",
                              examples=["1107837019238536"])
    text: str = Field("",
                      description="Text content of the caption. The Instagram caption character "
                                  "limit is also 2200 characters, just like the comment. "
                                  "Instagram caption can only contain up to 30 hashtags.",
                      examples=["Life's a beach, and I'm just playing in the sand."])
    created_at_utc: Optional[int] = Field(None,
                                          description="Timestamp when the caption was created. In unix epoch time.",
                                          examples=[1693213015])


class PostEngagementInfo(PreferDefaultsModel):
    """Post engagement information about count of likes and count of comments."""
    like_count: int = Field(0,
                            description="Count of likes.",
                            examples=[10])
    comment_count: int = Field(0,
                               description="Count of comments.",
                               examples=[10])


class PostBasicInfo(PostEngagementInfo):
    """Post information about when it was created, its caption, width, height
    etc."""
    model_config = ConfigDict(coerce_numbers_to_str=True)

    id: Optional[str] = Field(...,
                              description="Unique identifier of the post.",
                              examples=["3179223655971394742"])
    code: str = Field(...,
                      description="Short code of the post url. Can be used in "
                                  "form of www.instagram.com/<code> to access the post.",
                      examples=["Cx4I1irBSnk"])
    user: UserBasicInfo = Field(...,
                                description="User who owns the post.",
                                examples=[UserBasicInfo(id="387381865",
                                                        username="dummy_user")])
    taken_at: Optional[int] = Field(None,
                                    description="When the post was created, in unix epoch time.",
                                    examples=[1695060863])
    media_type: str = Field(...,
                            description="Media type: Photo, Video, IGTV, Reel, Album.",
                            examples=["Photo"])
    caption: Optional[Caption] = Field(None,
                                       description="Caption of the post.",
                                       examples=[None])
    accessibility_caption: str = Field("",
                                       description="Accessibility caption in text format. Alt text describes "
                                                   "your photos for people with visual impairments. Alt text "
                                                   "will be automatically created for your photos or you can "
                                                   "choose to write your own.",
                                       examples=["Photo is taken by John."])
    original_width: int = Field(...,
                                description="Original width of the media, can be used to "
                                            "get the downloading url of the media.",
                                examples=[1440])
    original_height: int = Field(...,
                                 description="Original height of the media, can be used to "
                                             "get the downloading url of the media.",
                                 examples=[1440])
    # the url signature has a time limitation.
    urls: List[str] = Field([],
                            description="Download URL of the media, which is only accessible in a few hours.",
                            examples=[["https://scontent-muc2-1.cdninstagram.com/v/t39.30808-6/369866.jpg"]])


class MusicBasicInfo(PreferDefaultsModel):
    """Music information about its url, duration, title, originally from which
    post it comes, artist etc."""
    model_config = ConfigDict(coerce_numbers_to_str=True)

    id: Optional[str] = Field(...,
                              description="id of this audio asset.",
                              examples=["664212705901923"])
    is_trending_in_clips: bool = Field(False,
                                       description="Is this music trending in clips?",
                                       examples=[True, False])
    artist: Optional[UserProfile] = Field(None,
                                          description="Artist who created this audio/music. For a music, it will only "
                                                      "contain the name of the artist. For a sound, it will contain the"
                                                      "creator's instagram information, such as id, username etc.",
                                          examples=[UserProfile(id="387381865",
                                                                username="dummy_user",
                                                                fullname="Dummy User",
                                                                profile_pic_url="https://dummy-pic.com",
                                                                is_verified=False,
                                                                is_private=None)])
    title: str = Field("Original audio", description="Title.", examples=["Original audio"])
    duration_in_ms: Optional[int] = Field(None, description="Music duration", examples=[6617])
    url: Optional[str] = Field(None,
                               description="the download url of the music",
                               examples=["https://scontent-muc2-1.xx.fbcdn.net/v/t39.12897-6/4.m4a"])


class Music(MusicBasicInfo):
    """Extended Music information, contains time created, original post id,
    clips count and photos count."""
    clips_count: int = Field(0,
                             description="Number of clips are using this music.",
                             examples=[12])
    photos_count: int = Field(0,
                              description="Number of photos are using this music.",
                              examples=[10])


class Post(PostBasicInfo):
    """Post information about when it was created, who is tagged in it, its
    caption, location width, height etc. """
    user: UserProfile = Field(...,
                              description="User who owns the post.",
                              examples=[UserProfile(id="387381865",
                                                    username="dummy_user",
                                                    fullname="Dummy User",
                                                    profile_pic_url="https://dummy-pic.com",
                                                    is_verified=False,
                                                    is_private=None)])
    has_shared_to_fb: Optional[bool] = Field(None,
                                             description="Is the post shared to facebook?",
                                             examples=[False])
    usertags: List[Usertag] = Field([],
                                    description="Usertags appear in the post.",
                                    examples=[])
    location: Optional[Location] = Field(None,
                                         description="Location of the post, most of the time it's not given.",
                                         examples=[])
    music: Optional[MusicBasicInfo] = Field(
        None,
        description="music used in this post.",
        examples=[MusicBasicInfo(id="664212705901923",
                                 is_trending_in_clips=False,
                                 duration_in_ms=6617,
                                 url="https://scontent-muc2-1.xx.fbcdn.net/v.m4a",
                                 artist=UserProfile(id="387381865",
                                                    username="dummy_user",
                                                    fullname="Dummy User",
                                                    profile_pic_url="https://dummy-pic.com",
                                                    is_verified=False,
                                                    is_private=True),
                                 title="Original audio")])


class Posts(PreferDefaultsModel):
    """Aggregate a list of posts into a field to easily render as a JSON response. """
    posts: Union[List[Post], List[PostBasicInfo]] = Field([],
                                                          description="A list of posts.",
                                                          examples=[])
    count: int = Field(0,
                       description="Number of posts contained.",
                       examples=[100])


class MusicPosts(Posts):
    """Aggregate a list of posts into a field to easily render as a JSON response. """
    music: Music = Field(...,
                         description="A music which is used in all posts.",
                         examples=[])


class HashtagBasicInfo(PreferDefaultsModel):
    """Hashtag basic information"""
    model_config = ConfigDict(coerce_numbers_to_str=True)

    id: Optional[str] = Field(...,
                              description="Unique identifier of the hashtag.",
                              examples=["17843820562040860"])
    name: str = Field(...,
                      description="name of the hashtag.",
                      examples=["asiangames"])
    post_count: int = Field(0,
                            description="Count of the posts with the hashtag.",
                            examples=[405268])
    profile_pic_url: str = Field("",
                                 description="Hashtag profile picture url. It's created by instagram using one of the "
                                             "popular pictures from posts with the hashtag.",
                                 examples=["https://scontent-muc2-1.cdninstagram.com/vad"])


class HashtagBasicInfos(PreferDefaultsModel):
    """A list of hashtag basic infos are contained for storing user following
    hashtags information."""
    hashtags: List[HashtagBasicInfo] = Field([],
                                             description="Found hashtags matched to the keywords.",
                                             examples=[[HashtagBasicInfo(id="17843654935044234",
                                                                         name="primeleague",
                                                                         profile_pic_url="https://cdninstagram.com/vad",
                                                                         post_count=16)]])
    count: int = Field(0,
                       description="Number of hashtags contained.",
                       examples=[100])


class Hashtag(HashtagBasicInfo):
    """Hashtag information"""
    is_trending: bool = Field(False,
                              description="Is it a trending hashtag?",
                              examples=[False])
    related_tags: Optional[List[str]] = Field(None,
                                              description="Related tags in a list. This is calculated by instagram "
                                                          "based on co-occurrence of posts.",
                                              examples=["asiangames2023"])
    subtitle: str = Field("",
                          description="subtitle of the hastag.",
                          examples=["See a few top posts each week"])
    posts: List[Post] = Field([],
                              description="A list of top posts. Instagram only shows top posts (up to 30) from "
                                          "the hashtag.",
                              examples=[[]])


class SearchingResultBasicInfo(PreferDefaultsModel):
    """Hashtag appears in searching result."""
    position: int = Field(...,
                          description="Position of the search result.",
                          examples=[0, 1])


class SearchingResultHashtag(SearchingResultBasicInfo):
    """Hashtag appears in searching result."""
    hashtag: HashtagBasicInfo = Field(...,
                                      description="Hashtag shows in the search result at the associated position.",
                                      examples=[HashtagBasicInfo(id="17843654935044234",
                                                                 name="primeleague",
                                                                 profile_pic_url="https://sconte.cdninstagram.com/vad",
                                                                 post_count=16)])


class SearchingResultUser(SearchingResultBasicInfo):
    """User appears in searching result."""
    user: UserProfile = Field(...,
                              description="User appears in the search result at the associated position.",
                              examples=[UserProfile(id="387381865",
                                                    username="dummy_user",
                                                    fullname="Dummy User",
                                                    profile_pic_url="https://dummy-pic.com",
                                                    is_verified=False,
                                                    is_private=None)])


class Place(PreferDefaultsModel):
    location: LocationBasicInfo = Field(...,
                                        description="Place appears in the search result at the associated position.",
                                        examples=[LocationBasicInfo(id="213502500",
                                                                    name="Beijing, China")])
    subtitle: str = Field("",
                          description="Subtitle of the place, normally it can be in a different language.",
                          examples=["Puerto Del Rosario, Canarias, Spain"])
    title: str = Field("",
                       description="Title of the place, normally it can be in a different language.",
                       examples=["Morro Jable"])


class SearchingResultPlace(SearchingResultBasicInfo):
    """User appears in searching result."""
    place: Place = Field(...,
                         description="Place appears in the search result at the associated position.",
                         examples=[Place(location=LocationBasicInfo(id="213502500",
                                                                    name="Beijing, China"),
                                         subtitle="",
                                         title="Beijing, China")])


class SearchingResult(PreferDefaultsModel):
    """Searching result contains found hashtags, users and places."""
    hashtags: List[SearchingResultHashtag] = Field(
        [],
        description="Found hashtags matched to the keywords.",
        examples=[[SearchingResultHashtag(position=0,
                                          hashtag=HashtagBasicInfo(
                                              id="17843654935044234",
                                              name="primeleague",
                                              profile_pic_url="https://scontent-muc2-1.cdninstagram.com/vad",
                                              post_count=16))]])
    users: List[SearchingResultUser] = Field([],
                                             description="Found users matched to the keywords.",
                                             examples=[[SearchingResultUser(
                                                 position=1,
                                                 user=UserProfile(id="387381865",
                                                                  username="dummy_user",
                                                                  fullname="Dummy User",
                                                                  profile_pic_url="https://dummy-pic.com",
                                                                  is_verified=False,
                                                                  is_private=None))]])
    places: List[SearchingResultPlace] = Field([],
                                               description="Found places matched to the keywords.",
                                               examples=[[SearchingResultPlace(position=1,
                                                                               place=Place(location=LocationBasicInfo(
                                                                                           id="213502500",
                                                                                           name="Beijing, China"),
                                                                                           subtitle="",
                                                                                           title="Beijing, China"))]])
    personalised: bool = Field(...,
                               description="Indicate whether the searching result is personalised or not.",
                               examples=[True, False])
