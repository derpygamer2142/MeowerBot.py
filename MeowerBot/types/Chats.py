from dataclasses import dataclass

@dataclass
class Chat:
    id: str
    name: str
    direct: bool
    flags: int
    members: list[str]
    permissions: int
    invite_code: str
    created: int