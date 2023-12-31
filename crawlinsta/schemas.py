from pydantic import BaseModel, Field
from typing import List, ForwardRef, Optional


class UserBasicInfo(BaseModel):
    """User basic information, contains `id`, `username`, `fullname`, `profile_pic_url` and `is_verified`."""
    id: Optional[str] = Field(None,
                              description="unique identifier if an user. It's 9 digits in string format.",
                              examples=["387381865"])
    username: str = Field(...,
                          description="It's limited to 30 characters and must contain only "
                                      "letters in lowercase, numbers, periods, and underscores."
                                      "It's the unique identifier for the user besides the user id,"
                                      "which is generated by instagram automatically.",
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
                                       description="Indicates that the user account is private or public."
                                                   "Please check https://help.instagram.com/448523408565555"
                                                   "for detailed information.",
                                       examples=[False])
    is_verified: bool = Field(False,
                              description="Indicates whether the user account is verified as business/official "
                                          "account or not.",
                              examples=[False])


class UserEngagementInfo(BaseModel):
    """User engagement information, contains mainly about the interactions between the given user with
    other users or posts. It contains fields like `follower_count`, `following_count`, `following_tag_count`,
    `post_count`, `usertags_count`."""
    follower_count: int = Field(...,
                                description="Number of the followers.",
                                examples=[10])
    following_count: int = Field(...,
                                 description="Number of the following.",
                                 examples=[10])
    following_tag_count: int = Field(...,
                                     description="Number of the tags, which are followed by the user.",
                                     examples=[0])
    post_count: int = Field(...,
                            description="Number of the posts of the user.",
                            examples=[20])
    usertags_count: int = Field(0,
                                description="Number of the times, that the user was tagged in posts.",
                                examples=[20])


class UserInfo(UserBasicInfo, UserEngagementInfo):
    """User information contains `id`, `username`, `full name`, `biography` and son on ."""
    biography: str = Field(...,
                           description="A short description of the user account.",
                           examples=["Hello, welcome to my instagram."])


class Users(BaseModel):
    """An aggregation class to have the field `users` for storing a list of
    instances of `UserInfo`."""
    users: List[UserBasicInfo] = Field(...,
                                       description="A list of user information.",
                                       examples=[[UserBasicInfo(id="387381865",
                                                                username="dummy_user",
                                                                fullname="Dummy User",
                                                                profile_pic_url="https://dummy-pic.com",
                                                                is_verified=False,
                                                                is_private=False)]])


class FriendshipStatus(BaseModel):
    """Describe the relationship between the liker and the post owner. """
    following: bool = Field(...,
                            description="Does the liker follow the post owner?",
                            examples=[False])
    followed_by: bool = Field(...,
                              description="Does the post owner follow the liker?",
                              examples=[False])
    blocking: Optional[bool] = Field(None,
                                     description="Is the liker blocked by the post owner? "
                                                 "Blocked users' likes are not showed.",
                                     examples=[False])
    muting: Optional[bool] = Field(None,
                                   description="Is the post owner muted by the liker?",
                                   examples=[False])
    is_private: bool = Field(...,
                             description="Is the liker's account private? For a private account, "
                                         "it's not displayed in likes.",
                             examples=[False])
    incoming_request: Optional[bool] = Field(None,
                                             description="Has the post owner sent a follower request to the liker?",
                                             examples=[False])
    outgoing_request: Optional[bool] = Field(None,
                                             description="Has the liker sent a follower request to the post owner?",
                                             examples=[False])
    is_blocking_reel: Optional[bool] = Field(None,
                                             description="Is the liker blocking reel to show in his personal feed?",
                                             examples=[False])
    is_muting_reel: Optional[bool] = Field(None,
                                           description="Is the liker muting reel in his personal feed?",
                                           examples=[False])
    is_bestie: Optional[bool] = Field(None,
                                      description="Is the liker bestie of the post owner? Only the uer can "
                                                  "see his/her besties list. Please check "
                                                  "https://help.instagram.com/476003390920140/?cms_platform=android-app&helpref=platform_switcher"
                                                  "for more detailed information.",
                                      examples=[False])
    is_restricted: Optional[bool] = Field(None,
                                          description="Is the liker's account restricted?",
                                          examples=[False])
    is_feed_favorite: Optional[bool] = Field(None,
                                             description="Is the feed of the post owner favorite of the liker?",
                                             examples=[False])
    subscribed: Optional[bool] = Field(None,
                                       description="Has the liker subscribed the post owner?",
                                       examples=[False])
    is_eligible_to_subscribe: Optional[bool] = Field(None,
                                                     description="Is the liker eligible to subscribe the post owner?"
                                                                 "Please check https://help.instagram.com/478012211024479# for "
                                                                 "more details about criteria eligibility to subscriptions.",
                                                     examples=[False])


class Liker(UserBasicInfo):
    """Liker, who likes a post. It contains the basic user information of `id`,
    `username`, `full name` etc, and additionally a `friendship_status` field to
    describe the relationship between the liker and the post owner."""
    friendship_status: FriendshipStatus = Field(...,
                                                description="Indicates the friendship between the "
                                                            "liker and post owner.",
                                                examples=[])


class Likers(BaseModel):
    """An aggregation class to have the field `likers` for storing a list of
    instances of `Liker`."""
    likers: List[Liker] = Field(...,
                                description="A list of likers.",
                                examples=[[]])


Comment = ForwardRef('Comment')


class Comment(BaseModel):
    """Relevant information about a comment, including `id`, `user_id`, `post_id`
    `type` etc."""
    id: str = Field(...,
                    description="Unique identifier of the comment. It consists of 17 digits.",
                    examples=["18016617763686865"])
    user_id: str = Field(...,
                         description="Id reference to the user, who made the comment.",
                         examples=["8659188880"])
    post_id: str = Field(...,
                         description="Id reference to the user, who made the comment.",
                         examples=["3194677555662724330"])
    created_at_utc: int = Field(...,
                                description="Timestamp of when the comment was made.",
                                examples=[1695060863])
    status: str = Field(...,
                        description="Status of the comment, Active or Inactive. The inactive comments "
                                    "refers to the comments which are hidden by the post owner with certain"
                                    "conditions, such as filtered with certain words, default spam filter, or"
                                    "manually controlled by the post owner.",
                        examples=["Active"])
    share_enabled: bool = Field(...,
                                description="Is the comment enabled for sharing? Generally all the visible commends"
                                            "are legit for sharing, only the hidden commends are not enabled for "
                                            "sharing. This is a duplicated feature of status.",
                                examples=[True])
    is_ranked_comment: bool = Field(...,
                                    description="Is the comment a ranked one? The Instagram comments feature "
                                                "is set up in such a way that it shows first the comments of "
                                                "people you follow. Or, sometimes, a comment by a verified "
                                                "account or a comment that is most liked shows up first.",
                                    examples=[True])
    text: str = Field(...,
                      description="Comment content in free text format. The Instagram comment character "
                                  "limit is also 2200 characters, just like the caption. Instagram comments"
                                  " can only contain up to 30 hashtags.",
                      examples=["Cool stuff!"])
    has_translation: bool = Field(...,
                                  description="Does the comment have a translation? "
                                              "Captions and comments on posts in feed, "
                                              "as well as the bio that you include on your profile, "
                                              "are translated automatically based on the language "
                                              "they're written in and the language settings of the "
                                              "person viewing it. If your language is available as a "
                                              "translation, you can tap See translation below the text "
                                              "to see it.",
                                  examples=[True])
    is_liked_by_post_owner: bool = Field(...,
                                         description="Is the comment liked by the post owner?",
                                         examples=[True])
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
                                                       post_id="3194677555662724330",
                                                       type=0,
                                                       created_at_utc=1695060863,
                                                       content_type="comment",
                                                       status="Active",
                                                       share_enabled=True,
                                                       is_ranked_comment=True,
                                                       text="Cool Stuff!",
                                                       has_translation=False,
                                                       is_liked_by_post_owner=True,
                                                       has_liked_comment=True,
                                                       comment_like_count=1,
                                                       child_comments=[])]])


class Usertag(BaseModel):
    """Usertag information, mainly about who is tagged at which position at what time
    in video and how long the tagged user appears."""
    user: UserBasicInfo = Field(...,
                                description="User who is tagged in the post.",
                                examples=[UserBasicInfo])
    position: List[float] = Field(...,
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


class Location(BaseModel):
    """Location information, contains location name, city, longitude, latitude and
     address etc. The location information is provided by the post owner, while
     creating/editing the post."""
    id: str = Field(...,
                    description="Unique identifier of the location.",
                    examples=["1107837019238536"])
    short_name: str = Field(...,
                            description="Short name of the location",
                            examples=["Kedro-beach"])
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
    """Caption of the post."""
    id: str = Field(...,
                    description="Unique identifier of the caption.",
                    examples=["1107837019238536"])
    text: str = Field(...,
                      description="Text content of the caption. The Instagram caption character "
                                  "limit is also 2200 characters, just like the comment. "
                                  "Instagram caption can only contain up to 30 hashtags.",
                      examples=["Life's a beach, and I'm just playing in the sand."])
    created_at_utc: int = Field(...,
                                description="Timestamp when the caption was created. In unix epoch time.",
                                examples=[1693213015])


class PostEngagementInfo(BaseModel):
    """Post engagement information about count of likes and count of comments."""
    like_count: int = Field(...,
                            description="Count of likes.",
                            examples=[10])
    comment_count: int = Field(...,
                               description="Count of comments.",
                               examples=[10])


class Post(PostEngagementInfo):
    """Post information about when it was created, who is tagged in it, its
    caption, location width, height etc. """
    id: str = Field(...,
                    description="Unique identifier of the post.",
                    examples=["3179223655971394742"])
    code: str = Field(...,
                      description="Short code of the post url. Can be used in "
                                  "form of www.instagram.com/<code> to access the post.",
                      examples=["Cx4I1irBSnk"])
    user: UserBasicInfo = Field(...,
                                description="User who owns the post.",
                                examples=[UserBasicInfo])
    taken_at: int = Field(...,
                          description="When the post was created, in unix epoch time.",
                          examples=[1695060863])
    has_shared_to_fb: bool = Field(...,
                                   description="Is the post shared to facebook?",
                                   examples=[False])
    usertags: List[Usertag] = Field(...,
                                    description="Usertags appear in the post.",
                                    examples=[])
    media_type: str = Field(...,
                            description="Media type: Photo, Video, IGTV, Reel, Album.",
                            examples=["Photo"])
    caption: Optional[Caption] = Field(...,
                                       description="Caption of the post.",
                                       examples=[None])
    accessibility_caption: str = Field(...,
                                       description="Accessibility caption in text format. Alt text describes "
                                                   "your photos for people with visual impairments. Alt text "
                                                   "will be automatically created for your photos or you can "
                                                   "choose to write your own.",
                                       examples=["Photo is taken by John."])
    location: Optional[Location] = Field(...,
                                         description="Location of the post, most of the time it's not given.",
                                         examples=[])
    original_width: int = Field(...,
                                description="Original width of the media, can be used to "
                                            "get the downloading url of the media.",
                                examples=[1440])
    original_height: int = Field(...,
                                 description="Original height of the media, can be used to "
                                             "get the downloading url of the media.",
                                 examples=[1440])
    # the url signature has a time limitation.
    url: str = Field(...,
                     description="Download URL of the media, which is only accessible in a few hours.",
                     examples=["https://scontent-muc2-1.cdninstagram.com/v/t39.30808-6/369866539_18384091342039171_8947783907607888457_n.jpg?stp=dst-jpg_e15&_nc_ht=scontent-muc2-1.cdninstagram.com&_nc_cat=107&_nc_ohc=MK-DDNIWpOsAX9XOSOU&edm=ABmJApAAAAAA&ccb=7-5&ig_cache_key=MzE3NzEzMTk0MjI3MjUxNjgwOQ%3D%3D.2-ccb7-5&oh=00_AfASOeklyljD2tiuunU9AfSJplcSGFnMoJIzujuYa1DC9g&oe=650EF52B&_nc_sid=b41fef"])


class Posts(BaseModel):
    """Aggregate a list of posts into a field to easily render as a JSON response. """
    posts: List[Post] = Field(...,
                              description="A list of posts.",
                              examples=[])


class HashtagBasicInfo(BaseModel):
    """Hashtag basic information"""
    id: str = Field(...,
                    description="Unique identifier of the hashtag.",
                    examples=["17843820562040860"])
    name: str = Field(...,
                      description="name of the hashtag.",
                      examples=["asiangames"])
    post_count: int = Field(...,
                            description="Count of the posts with the hashtag.",
                            examples=[405268])
    profile_pic_url: str = Field("",
                                 description="Hashtag profile picture url. It's created by instagram using one of the "
                                             "popular pictures from posts with the hashtag.",
                                 examples=[
                                     "https://scontent-muc2-1.cdninstagram.com/v/t51.2885-15/384945060_3382351958743676_8236780213784037973_n.heic?stp=dst-jpg_e35&_nc_ht=scontent-muc2-1.cdninstagram.com&_nc_cat=108&_nc_ohc=z0_PSswODrcAX-UzX_h&edm=AGyKU4gBAAAA&ccb=7-5&ig_cache_key=MzIwNDA1MjAyOTI2NTQ2Nzc0OA%3D%3D.2-ccb7-5&oh=00_AfDfikF5zUMBZVxEx7KCDJDMEa7xnrtU3FQAKRMl8DgUVw&oe=651FC6D7&_nc_sid=2011ad"])


class HashtagBasicInfos(BaseModel):
    """A list of hashtag basic infos are contained for storing user following
    hashtags information."""
    hashtags: List[HashtagBasicInfo] = Field([],
                                             description="Found hashtags matched to the keywords.",
                                             examples=[[HashtagBasicInfo(id="17843654935044234",
                                                                        name="primeleague",
                                                                        post_count=16)]])


class Hashtag(HashtagBasicInfo):
    """Hashtag information"""
    is_trending: bool = Field(...,
                              description="Is it a trending hashtag?",
                              examples=[False])
    related_tags: Optional[List[str]] = Field(None,
                                              description="Related tags in a list. This is calculated by instagram "
                                                          "based on co-occurrence of posts.",
                                              examples=["asiangames2023"])
    subtitle: str = Field("",
                          description="subtitle of the hastag.",
                          examples=["See a few top posts each week"])
    posts: List[Post] = Field(...,
                              description="A list of top posts. Instagram only shows top posts (up to 30) from "
                                          "the hashtag.",
                              examples=[])


class SearchingResultHashtag(BaseModel):
    """Hashtag appears in searching result."""
    position: int = Field(...,
                          description="Position of the search result hashtag.",
                          examples=[0, 1])
    hashtag: HashtagBasicInfo = Field(...,
                                      description="Hashtag shows in the search result at the associated position.",
                                      examples=[HashtagBasicInfo(id="17843654935044234",
                                                                 name="primeleague",
                                                                 post_count=16)])


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
                                                                                                              post_count=16))]])
    users: List[SearchingResultUser] = Field([],
                                             description="Found users matched to the keywords.",
                                             examples=[[SearchingResultUser(position=1,
                                                                            user=UserBasicInfo(id="387381865",
                                                                                               username="dummy_user",
                                                                                               fullname="Dummy User",
                                                                                               profile_pic_url="https://dummy-pic.com",
                                                                                               is_verified=False,
                                                                                               is_private=None))]])
