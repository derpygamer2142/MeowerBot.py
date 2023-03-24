from dataclasses import dataclass
from .errors import *
from typing import Optional, Union, Any
from aiohttp import ClientSession

#type aliases
from typing import NewType

ticket = NewType("ticket", str)

@dataclass 
class Masquerade:
    username: str
    pfp: str

# create a class that combines the two, but fetches the rest of the data from the API




@dataclass
class Statuscode:
    code_id: int
    code: str


@dataclass
class WaitReturn:
    ok: bool
    packet: Any
    statuscode: Statuscode


from .Application import Application, PrivateApplication
from .Chats import Chat
from .messages import Post, FeedPost, Comment
from .Notification import Notification
from .User import User, PrivateUser
from .Session import UserSession, AuthorizedAppSession, Session

__all__ = [
    "Application",
    "PrivateApplication",
    "Chat",
    "Post",
    "FeedPost",
    "Comment",
    "Notification",
    "User",
    "UserSession",
    "Statuscode",
    "WaitReturn",
    "Masquerade",
    "ticket",
    "PrivateUser",
    "Session",
]