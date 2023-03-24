from . import Masquerade
from .User import User

@dataclass
class FeedPost:
    id: str
    author: User
    masquerade: Masquerade | None
    public_flags: int
    stats: dict[str, int]
    content: str
    filtered_content: str
    time: int
    delete_after: int | None





@dataclass
class Comment:
    id: str
    post_id: str
    parent_id: str
    author: User
    masquerade: Masquerade
    public_flags: int
    likes: int
    content: str
    filtered_content: str
    time: int
    delete_after: int | None

@dataclass
class Post:
    id: str
    chat_id: str
    author: User
    masquerade: Masquerade | None
    reply_to: str
    flags: int
    content: str
    filtered_content: str
    likes: int
    time: int
    delete_after: int | None

