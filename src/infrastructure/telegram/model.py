from dataclasses import dataclass

@dataclass
class Channel:
    # Unique channel identifier.
    channel_id: str
    # Human readable channel title.
    title: str

@dataclass
class Message:
    # Unique message identifier.
    message_id: int
    # Message text.
    text: str
    # Channel where this message is posted.
    channel_id: str
    # Channel where this message was forwarded from.
    channel_fwd_from_id: str
    # Number of views.
    views: int
    # Number of forwards.
    forwards: int
    # Publication datetime
    datetime: str