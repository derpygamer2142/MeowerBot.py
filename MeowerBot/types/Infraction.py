from dataclasses import dataclass
from . import User

@dataclass
class Infraction:
    id: str
    user: User
    action: str
    reason: str
    offending_content: str
    status: int
    created: int
    expires: int | None

    
