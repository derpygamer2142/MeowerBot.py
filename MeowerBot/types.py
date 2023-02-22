from dataclasses import dataclass
from .errors import *
from typing import Optional, Union, Any
from aiohttp import ClientSession

@dataclass
class UserIcon:
    type: int
    data: Union[str, int]


@dataclass
class Masquerade:
    username: str
    pfp: UserIcon


# create a class that combines the two, but fetches the rest of the data from the API
@dataclass
class User:
    id: int
    username: str
    public_flags: int
    icon: UserIcon
    created: Optional[int]
    theme: Optional[str]
    quote: Optional[str]
    badges: Optional[list[str]]
    stats: Optional[dict[str, int]]

    async def fetch(self, session: ClientSession) -> None:
        # check if the data is already there
        if self.created:
            return

        async with session.get(f"/v1/users/{self.id}") as resp:
            if resp.status != 200:
                raise BotError(resp.status)
            user = await resp.json()

            # update the data
            self.__init__(**user, icon=UserIcon(**user["icon"]))


@dataclass
class FeedPost:
    id: int
    author: User
    masquerade: Masquerade
    public_flags: int
    stats: dict[str, int]
    content: str
    filtered_content: str
    time: int
    delete_after: Optional[int]

@dataclass
class Statuscode:
    code_id: int
    code: str


@dataclass
class WaitReturn:
    ok: bool
    packet: Any
    statuscode: Statuscode

