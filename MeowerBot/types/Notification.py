from dataclasses import dataclass
from . import User


@dataclass
class Notification:
    id: str
    recipient_id: str = None,
    type: int = None,
    data: dict = {},
    read: bool = False,
    time: int = None
