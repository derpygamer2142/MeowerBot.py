from dataclasses import dataclass
from . import User

@dataclass
class Application:
    id: str
    name: str
    description: str
    flags: int
    created: int

@dataclass
class PrivateApplication(Application):
    owner_id: str
    maintainers: list[User]

