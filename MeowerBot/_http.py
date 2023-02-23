from typing import Optional, Any

from aiohttp import ClientSession
from .types import Masquerade, FeedPost, User, UserIcon
from .errors import NotAllowedError, BotError

class _http:
    API_URL = "https://api.beta.meower.org/"

    def __init__(self, token: str) -> None:
        self.token = token
        self.session = ClientSession(base_url=self.API_URL, headers={"Authorization": token})

    async def send_feed_post(
        self, content: str, masquerade: Optional[Masquerade] = None, bridged=False
    ) -> FeedPost:
        
        data: dict[str, Any] = {"content": content}
        if masquerade:

            data["masquerade"] = {
                "username": masquerade.username,
                "pfp": {"type": masquerade.pfp.type, "data": masquerade.pfp.data},
            }

        if bridged:
            data["bridged"] = True

        async with self.session.post("/vl/home", data=data) as resp:
            if resp.status in [403, 401]:
                raise NotAllowedError(resp.status)

            if resp.status != 200:
                raise BotError(resp.status)

            post = await resp.json()
            return FeedPost(
                **post,
                author=User(**post["author"], icon=UserIcon(**post["author"]["icon"])),
                masquerade=Masquerade(**post["masquerade"]),
                stats=post["stats"],
            )
        
    async def get_user(self, id: str) -> User:
        async with self.session.get(f"/v1/users/{id}") as resp:
            if resp.status != 200:
                raise BotError(resp.status)
            user = await resp.json()
            return User(**user, icon=UserIcon(**user["icon"]))
        
    
