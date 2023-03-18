from typing import Optional, Any

from aiohttp import ClientSession
from .types import Masquerade, FeedPost, User
from .errors import NotAllowedError, BotError

#get the python version
import sys

from . import __version__

class _http:
    API_URL = "http://localhost:3000"

    def __init__(self, token: str) -> None:
        self.token = token
        self.session = ClientSession(base_url=self.API_URL, headers={
            "Authorization": token,
            "User-Agent": f"MeowerBot {__version__}  (Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]})",
            "X-Client-Name": "MeowerBot",
            "X-Client-Version": f"{__version__}",
            "X-Client-Type": "Bot"
        })

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

        async with self.session.post("/v1/home", json=data) as resp:
            if resp.status in [403, 401]:
                raise NotAllowedError(resp.status)

            if resp.status != 200:
                raise BotError(resp.status)

            post = await resp.json()
            author = post["author"]
            masquerade = post.get("masquerade")

            
            del post["author"]
            del post["masquerade"]
            return FeedPost(
                **post,
                author=User(**author),
                masquerade=Masquerade(**masquerade) if masquerade else None,
                
            )
        
    async def get_user(self, id: str) -> User:
        async with self.session.get(f"/v1/users/{id}") as resp:
            if resp.status != 200:
                raise BotError(resp.status)
            user = await resp.json()
            return User(**user, icon=UserIcon(**user["icon"]))
        
    
