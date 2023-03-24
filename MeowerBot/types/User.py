from dataclasses import dataclass
from MeowerBot.util import bitflag
from typing import Optional

from . import flags
#named tuple
from typing import NamedTuple

@dataclass
class Account:
    id: str
    email: str
    password: str | None
    mfa_methods: list[str]
    last_updated: int | None


@dataclass
class User:
    #only things that are in partial user
    id: str
    username: str
    public_flags: int
    created: Optional[int] = None
    theme: Optional[str] = None
    icon: Optional[str] = None
    quote: Optional[str] = None
    badges: list[str]
    stats: dict[str, int]
    bot: bool = False



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

            await self.set_flag_options()

    async def set_flag_options(self):
        # set bot to true if the bot flag is set, and if the user is verified set verified to true
        self.bot = NamedTuple("bool", ["verified"], verified=bitflag.has(self.public_flags, flags.users.verifiedBot)) if bitflag.has(self.public_flags, flags.users.bot) else False
        



@dataclass
class PrivateUser(User):
    flags: int
    admin: int

