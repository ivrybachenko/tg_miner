from dataclasses import dataclass

@dataclass
class Channel:
    id: str
    title: str

@dataclass
class Message:
    id: int
    text: str