import enum
from typing import Mapping

class RoomType(enum.Enum):
    CHAT = 'c'
    PRIVATE = 'p'
    DIRECT = 'd'

class RawMessageType(enum.Enum):
    PING = 'ping'
    CONNECTED = 'connected'
    ADDED = 'added'
    CHANGED = 'changed'
    UPDATED = 'updated'
    REMOVED = 'removed'
    RESULT = 'result'
    FAILED = 'failed'
    ERROR = 'error'
    READY = 'ready'
    NONE = ''

class RoomMessage(enum.Enum):
    USER_JOINED = 'uj'
    USER_LEFT = 'ul'
    USER_ADDED = 'au'
    USER_REMOVED = 'ru'
    USER_MUTED = 'user-muted'
    USER_UNMUTED = 'user-unmuted'
    ROLE_ADDED = 'subscription-role-added'
    ROLE_REMOVED = 'subscription-role-removed'
    TOPIC_CHANGED = 'room_changed_topic'
    REMOVE = 'rm'
    NORMAL_MESSAGE = ''

class ErrorType(enum.Enum):
    TOO_MANY_REQUESTS = 'too-many-requests'

class ChangedStreamMessage(enum.Enum):
    NONE = ''
    USERS = 'users'
    NOTIFY_USER = 'stream-notify-user' # rooms-changed, subscriptions-changed
    NOTIFY_ROOM = 'stream-notify-room' # typing, delete message
    ROOM_MESSAGES = 'stream-room-messages' # main room events

class NotifyUser(enum.Enum):
    MESSAGE = 'message'
    OTR = 'otr'
    WEBRTC = 'webrtc'
    NOTIFICATION = 'notification'
    ROOMS_CHANGED = 'rooms-changed'
    SUBSCRIPTIONS_CHANGED = 'subscriptions-changed'

class User:
    __slots__ = ['id', 'name']
    def __init__(self, obj: Mapping[str, str]):
        self.id = obj['_id'] or 'unknown'
        self.name = obj['username'] or 'Unknown'

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name

    def __repr__(self) -> str:
        return '%s[%s]' % (self.name, self.id)

