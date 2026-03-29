from enum import Enum


class FriendshipStatus(str, Enum):
    INVITE_SENT = "INVITE_SENT"
    INVITE_RECEIVED = "INVITE_RECEIVED"
    FRIEND = "FRIEND"
