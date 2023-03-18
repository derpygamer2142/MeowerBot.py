from dataclasses import dataclass
from .errors import *
from typing import Optional, Union, Any
from aiohttp import ClientSession


@dataclass
class Masquerade:
    username: str
    pfp: str


# create a class that combines the two, but fetches the rest of the data from the API
@dataclass
class User:
    id: str
    username: str
    public_flags: int
    created: Optional[int] = None
    theme: Optional[str] = None
    icon: Optional[str] = None
    quote: Optional[str] = None
    badges: Optional[list[str]] = None
    stats: Optional[dict[str, int]] = None




    async def fetch(self, session: ClientSession) -> None:
        # check if the data is already there
        if self.created:
            return

        async with session.get(f"/v1/users/{self.id}") as resp:
            if resp.status != 200:
                raise BotError(resp.status)
            user = await resp.json()

            # update the data
            self.__init__(**user)


@dataclass
class FeedPost:
    id: str
    author: User
    masquerade: Masquerade
    content: str
    filtered_content: str | None
    time: int
    delete_after: int | None
    reply_to: Optional[str] = None
    public_flags: int = 0
    stats: Optional[dict[str, int]] = None


@dataclass
class Statuscode:
    code_id: int
    code: str


@dataclass
class WaitReturn:
    ok: bool
    packet: Any
    statuscode: Statuscode

