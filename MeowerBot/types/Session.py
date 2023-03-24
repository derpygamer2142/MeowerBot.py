from dataclasses import dataclass
from .User import User, PrivateUser
from .Application import Application
from .Chats import Chat
from .Infraction import Infraction
from .Account import Account

@dataclass
class UserSession:
    id: str
    user: User
    device: str
    country: str
    last_refreshed: int
    created: int

@dataclass
class AuthorizedAppSession:
    id: str
    application: Application
    scopes: list[str]
    first_authorized: int
    last_authorized: int | None

@dataclass
class Session:

    session_id: str
    bot_session: bool
    user: PrivateUser
    account: Account
    application: Application
    chats: list[Chat]
    following: list[str]
    blocked: list[str]
    infractions: list[Infraction]
    time_taken: int