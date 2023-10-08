from pydantic import BaseModel, Field
from typing import List, ForwardRef, Union, Optional


class UserBasicInfo(BaseModel):
    """User basic information, contains `id`, `username`, `fullname`, `profile_pic_url` and `is_verified`."""
    id: Optional[str] = Field(None,
                              description="unique identifier if an user. It's 9 digits in string format.",
                              examples=["387381865"])
    username: str = Field(...,
                          description="It's limited to 30 characters and must contain only "
                                      "letters in lowercase, numbers, periods, and underscores.",
                          examples=["dummy_user"])
    fullname: str = Field(...,
                          description="It's limited to 30 characters and must contain only "
                                      "letters, numbers, periods, underscores and spaces.",
                          examples=["Dummy User"])
    profile_pic_url: str = Field(...,
                                 description="Url of the profile picture for downloading. "
                                             "The generated link is usually available only for couple hours.",
                                 examples=["https://dummy-pic.com"])
    is_private: Optional[bool] = Field(None,
                                       description="Indicates whether the user account is private or public.",
                                       examples=[False])
    is_verified: bool = Field(False,
                              description="Indicates whether the user account is verified as business/official "
                                          "account or not.",
                              examples=[False])


class UserEngagementInfo(BaseModel):
    """User engagement information, contains mainly about the interactions between the given user with
    other users or medias. It contains fields like `follower_count`, `following_count`, `following_tag_count`,
    `media_count`, `usertags_count`."""
    follower_count: int = Field(...,
                                description="Number of the followers.",
                                examples=[10])
    following_count: int = Field(...,
                                 description="Number of the following.",
                                 examples=[10])
    following_tag_count: int = Field(...,
                                     description="Number of the tags, which followed by the user.",
                                     examples=[0])
    media_count: int = Field(...,
                             description="Number of the medias of the user.",
                             examples=[20])
    usertags_count: int = Field(...,
                                description="Number of the times, that the user was tagged in medias.",
                                examples=[20])


class UserInfo(UserBasicInfo, UserEngagementInfo):
    """User information contains `id`, `username`, `full name`, `biography` and son on ."""
    biography: str = Field(...,
                           description="A shot description of the user account.",
                           examples=["Hello, welcome to my instagram."])


class Users(BaseModel):
    """An aggregation class to have the field `users` for storing a list of
    instances of `UserInfo`."""
    users: List[UserInfo] = Field(...,
                                  description="A list of user information.",
                                  examples=[[UserInfo(id="387381865",
                                                      username="dummy_user",
                                                      fullname="Dummy User",
                                                      profile_pic_url="https://dummy-pic.com",
                                                      is_verified=False,
                                                      follower_count=5,
                                                      following_count=5,
                                                      following_tag_count=0,
                                                      media_count=2,
                                                      usertags_count=2,
                                                      biography="Hello, welcome to my instagram.")]])


class FriendshipStatus(BaseModel):
    """Describe the relationship between the liker and the media owner. """
    following: bool = Field(...,
                            description="Does the liker follow the media owner?",
                            examples=[False])
    followed_by: bool = Field(...,
                              description="Does the media owner follow the liker?",
                              examples=[False])
    blocking: bool = Field(...,
                           description="Is the liker blocked by the media owner? "
                                       "Blocked users' likes are not showed.",
                           examples=[False])
    muting: bool = Field(...,
                         description="Is the media owner muted by the liker?",
                         examples=[False])
    is_private: bool = Field(...,
                             description="is a private friend. For a private friend, "
                                         "the liker are not displayed in likes",
                             examples=[False])
    incoming_request: bool = Field(...,
                                   description="Does the media owner send a follower request to the liker?",
                                   examples=[False])
    outgoing_request: bool = Field(...,
                                   description="Does the liker send a follower request to the media owner?",
                                   examples=[False])
    is_blocking_reel: bool = Field(...,
                                   description="Is the liker blocking reel?",
                                   examples=[False])
    is_muting_reel: bool = Field(...,
                                 description="Is the liker muting reel?",
                                 examples=[False])
    is_bestie: bool = Field(...,
                            description="Is the liker bestie of the media owner?",
                            examples=[False])
    is_restricted: bool = Field(..., examples=[False])
    is_feed_favorite: bool = Field(...,
                                   description="Is the feed of the media owner favorite of the liker?",
                                   examples=[False])
    subscribed: bool = Field(...,
                             description="Does the liker subscribe the media owner?",
                             examples=[False])
    is_eligible_to_subscribe: bool = Field(...,
                                           description="Is the liker eligible to subscribe the media owner?",
                                           examples=[False])


class Liker(UserBasicInfo):
    """Liker, who likes a media. It contains the basic user information of `id`,
    `username`, `full name` etc, and additionally a `friendship_status` field to
    describe the relationship between the liker and the media owner."""
    friendship_status: FriendshipStatus = Field(..., examples=[])


class Likers(BaseModel):
    """An aggregation class to have the field `likers` for storing a list of
    instances of `Liker`."""
    likers: List[Liker] = Field(..., examples=[[]])


Comment = ForwardRef('Comment')


class Comment(BaseModel):
    """Relevant information about a comment, including `id`, `user_id`, `media_id`
    `type` etc."""
    id: str = Field(...,
                    description="Unique identifier of the comment. It consists of 17 digits.",
                    examples=["18016617763686865"])
    user_id: str = Field(...,
                         description="Id reference to the user, who made the comment.",
                         examples=["8659188880"])
    media_id: str = Field(...,
                         description="Id reference to the user, who made the comment.",
                         examples=["3194677555662724330"])
    created_at_utc: int = Field(...,
                                description="Timestamp of when the comment was made.",
                                examples=[1695060863])
    status: str = Field(...,
                        description="Status of the comment, Active or Inactive.",
                        examples=["Active"])
    share_enabled: bool = Field(...,
                                description="Is the comment enabled for sharing.",
                                examples=[True])
    is_ranked_comment: bool = Field(...,
                                    description="Is the comment a ranked one?",
                                    examples=[True])
    text: str = Field(...,
                      description="Comment content in free text format.",
                      examples=["Cool stuff!"])
    has_translation: bool = Field(...,
                                  description="Does the comment have a translation",
                                  examples=[True])
    is_liked_by_media_owner: bool = Field(...,
                                          description="Is the comment liked by the media owner.", examples=[True])
    comment_like_count: int = Field(...,
                                    description="Number of people liked the comment.",
                                    examples=[1])
    child_comments: List[Comment] = Field(...,
                                          description="Comments for this comment.",
                                          examples=[[]])


class Comments(BaseModel):
    """An aggregation of comments."""
    comments: List[Comment] = Field(...,
                                    description="A list of comments.",
                                    examples=[[Comment(id="18016617763686865",
                                                       user_id="8659188880",
                                                       media_id="3194677555662724330",
                                                       type=0,
                                                       created_at_utc=1695060863,
                                                       content_type="comment",
                                                       status="Active",
                                                       share_enabled=True,
                                                       is_ranked_comment=True,
                                                       text="Cool Stuff!",
                                                       has_translation=False,
                                                       is_liked_by_media_owner=True,
                                                       has_liked_comment=True,
                                                       comment_like_count=1,
                                                       child_comments=[])]])


class Usertag(UserBasicInfo):
    """Usertag information, mainly about who is tagged at which position at what time
    in video and how long the tagged user appears."""
    user: UserBasicInfo = Field(...,
                                description="User who is tagged in the media.",
                                examples=[UserBasicInfo])
    position: List[float] = Field(...,
                                  description="A list of two floats, which is "
                                              "used to identify the position of "
                                              "the tagged user in the media.",
                                  examples=[[0.6794871795, 0.7564102564]])
    start_time_in_video_in_sec: Optional[float] = Field(None,
                                                        description="Start time in video in seconds "
                                                                    "when the tagged user shows up",
                                                        examples=[None])
    duration_in_video_in_sec: Optional[float] = Field(None,
                                                      description="Duration in the video in seconds, "
                                                                  "when the tagged user shows up",
                                                      examples=[None])


class Location(BaseModel):
    """Location information, contains location name, city, longitude, latitude and
     address etc."""
    id: str = Field(...,
                    description="Unique identifier of the location.",
                    examples=["1107837019238536"])
    short_name: str = Field(...,
                            description="Short name of the location",
                            examples=["Kedrodasos Beach"])
    name: str = Field(...,
                      description="Full name of the location.",
                      examples=["Kedrodasos Beach"])
    city: str = Field(...,
                      description="to which city the location belongs",
                      examples=["Kántanos, Khania, Greece"])
    lng: float = Field(...,
                       description="Longitude of the location.",
                       examples=[23.5619])
    lat: float = Field(...,
                       description="Latitude of the location.",
                       examples=[35.26861])
    address: str = Field(...,
                         description="Address of the location. Typically is empty.",
                         examples=[""])


class Caption(BaseModel):
    """Caption of the media."""
    id: str = Field(...,
                    description="Unique identifier of the caption.",
                    examples=["1107837019238536"])
    text: str = Field(...,
                      description="Text content of the caption.",
                      examples=["Life's a beach, and I'm just playing in the sand."])
    created_at_utc: int = Field(...,
                                description="Timestamp when the caption was created. In unix epoch time.",
                                examples=[1693213015])
    content_type: str = Field(...,
                              description="Content type of the Caption.",
                              examples=["comment"])


class MediaEngagementInfo(BaseModel):
    """Media engagement information about count of likes and count of comments."""
    like_count: int = Field(...,
                            description="Count of likes.",
                            examples=[10])
    comment_count: int = Field(...,
                               description="Count of comments.",
                               examples=[10])


class Media(MediaEngagementInfo):
    """Media information about when it was created, who is tagged in it, its
    caption, location width, height etc. """
    id: str = Field(...,
                    description="Unique identifier of the media.",
                    examples=["3179223655971394742"])
    code: str = Field(...,
                      description="Short code of the media url. Can be used in "
                                  "form of www.instagram.com/<code> to access the media.",
                      examples=["Cx4I1irBSnk"])
    taken_at: int = Field(...,
                          description="When the media was created, in unix epoch time.",
                          examples=[1695060863])
    has_shared_to_fb: bool = Field(...,
                                   description="Is the media shared to facebook?",
                                   examples=[False])
    usertags: List[Usertag] = Field(...,
                                    description="Usertags appear in the media.",
                                    examples=[])
    media_type: str = Field(...,
                            description="media type: Photo, Video, IGTV, Reel, Album.",
                            examples=["Photo"])
    caption: Caption = Field(...,
                             description="Caption of the port.",
                             examples=[])
    accessibility_caption: str = Field(...,
                                       description="Accessibility caption in text format.",
                                       examples=["Photo is taken by John."])
    location: Optional[Location] = Field(...,
                                         description="Location of the media, most of the time it's not given.",
                                         examples=[])
    original_width: int = Field(..., description="Original width of the media, can be used to "
                                                 "get the downloading url of the media.", examples=[1440])
    original_height: int = Field(..., description="Original height of the media, can be used to "
                                                  "get the downloading url of the media.", examples=[1440])
    # the url signature has a time limitation.
    url: str = Field(...,
                     description="Download URL of the media, which is only accessible in fea hours.",
                     examples=["https://scontent-muc2-1.cdninstagram.com/v/t39.30808-6/369866539_18384091342039171_8947783907607888457_n.jpg?stp=dst-jpg_e15&_nc_ht=scontent-muc2-1.cdninstagram.com&_nc_cat=107&_nc_ohc=MK-DDNIWpOsAX9XOSOU&edm=ABmJApAAAAAA&ccb=7-5&ig_cache_key=MzE3NzEzMTk0MjI3MjUxNjgwOQ%3D%3D.2-ccb7-5&oh=00_AfASOeklyljD2tiuunU9AfSJplcSGFnMoJIzujuYa1DC9g&oe=650EF52B&_nc_sid=b41fef"])


class Medias(BaseModel):
    """Aggregate a list of medias into a field to easily render as a JSON response. """
    medias: List[Media] = Field(...,
                              description="A list of medias.",
                              examples=[])


class HashtagBasicInfo(BaseModel):
    """Hashtag basic information"""
    id: str = Field(...,
                    description="Unique identifier of the hashtag.",
                    examples=["17843820562040860"])
    name: str = Field(...,
                      description="name of the hashtag.",
                      examples=["asiangames"])
    media_count: int = Field(...,
                            description="Count of the medias with the hashtag.",
                            examples=[405268])


class Hashtag(HashtagBasicInfo, Medias):
    """Hashtag information"""
    profile_pic_url: str = Field(...,
                                 description="Profile picture url.",
                                 examples=["https://scontent-muc2-1.cdninstagram.com/v/t51.2885-15/384945060_3382351958743676_8236780213784037973_n.heic?stp=dst-jpg_e35&_nc_ht=scontent-muc2-1.cdninstagram.com&_nc_cat=108&_nc_ohc=z0_PSswODrcAX-UzX_h&edm=AGyKU4gBAAAA&ccb=7-5&ig_cache_key=MzIwNDA1MjAyOTI2NTQ2Nzc0OA%3D%3D.2-ccb7-5&oh=00_AfDfikF5zUMBZVxEx7KCDJDMEa7xnrtU3FQAKRMl8DgUVw&oe=651FC6D7&_nc_sid=2011ad"])
    is_trending: bool = Field(...,
                              description="Is it a trending hashtag?",
                              examples=[False])
    related_tags: Optional[List[str]] = Field(None,
                                              description="related tags in a list.",
                                              examples=["asiangames2023"])
    subtitle: str = Field("",
                          description="subtitle of the hastag.",
                          examples=["See a few top medias each week"])
    social_context: str = Field("",
                                description="Social context of the hashtag.",
                                examples=[""])
    social_context_profile_links: List[str] = Field([],
                                                    description="Social context profile links.",
                                                    examples=[[]])


class SearchingResultHashtag(BaseModel):
    """Hashtag appears in searching result."""
    position: int = Field(...,
                          description="Position of the search result hashtag.",
                          examples=[0, 1])
    hashtag: HashtagBasicInfo = Field(...,
                                      description="Hashtag shows in the search result at the associated position.",
                                      examples=[HashtagBasicInfo(id="17843654935044234",
                                                                 name="primeleague",
                                                                 media_count=16)])


class SearchingResultUser(BaseModel):
    """User appears in searching result."""
    position: int = Field(...,
                          description="Position of the search result user.",
                          examples=[0, 1])
    user: UserBasicInfo = Field(...,
                                description="User appears in the search result at the associated position.",
                                examples=[UserBasicInfo(id="387381865",
                                                        username="dummy_user",
                                                        fullname="Dummy User",
                                                        profile_pic_url="https://dummy-pic.com",
                                                        is_verified=False,
                                                        is_private=None)])


class SearchingResult(BaseModel):
    """Searching result contains found hashtags and/or users."""
    hashtags: List[SearchingResultHashtag] = Field([],
                                                   description="Found hashtags matched to the keywords.",
                                                   examples=[[SearchingResultHashtag(position=0,
                                                                                     hashtag=HashtagBasicInfo(id="17843654935044234",
                                                                                                              name="primeleague",
                                                                                                              media_count=16))]])
    users: List[SearchingResultUser] = Field([],
                                             description="Found users matched to the keywords.",
                                             examples=[[SearchingResultUser(position=1,
                                                                            user=UserBasicInfo(id="387381865",
                                                                                               username="dummy_user",
                                                                                               fullname="Dummy User",
                                                                                               profile_pic_url="https://dummy-pic.com",
                                                                                               is_verified=False,
                                                                                               is_private=None))]])
