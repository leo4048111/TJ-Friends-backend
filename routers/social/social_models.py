from pydantic import BaseModel
from typing import Union

class room(BaseModel):
    roomPwd: Union[str, None] = None
    coverUrl: str
    videoUrl: str
    roomName: str
    roomDescription: str
    roomPms: int

class joinRoom(BaseModel):
    roomId: str
    roomPwd: Union[str, None] = None

class editRoomInfo(BaseModel):
    roomId: str
    coverUrl: str
    videoUrl: str
    roomName: str
    roomDescription: str
    roomPms: int
    roomPwd: Union[str, None] = None

class leaveRoomInfo(BaseModel):
    userId: str
    roomId: str

class roomMessage(BaseModel):
    roomId: str
    text: str
    image: str

class roomVideo(BaseModel):
    positionMillis: int
    shouldPlay: bool
    curTime: str
    roomId: str

class ImageRequest(BaseModel):
    file: str
    fileName: str

class noticeIn(BaseModel):
    noticeId: int
    typ: str

class memoryIn(BaseModel):
    postContent: str
    isAnonymous: bool
    pms: Union[int, None] = None
    photoUrl: list

class follow_info(BaseModel):
    stuid: str

class draft(BaseModel):
    postContent: str
    photoUrl: list
    pms: int
    isAnonymous: int
    draftId: Union[int, None] = None

class DraftId(BaseModel):
    draftId: str

class deleteCommentInfo(BaseModel):
    comment_id: str
class postCommentIn(BaseModel):
    content: str
    postId: int


class userIdIn(BaseModel):
    userId: str


class sendMessageIn(BaseModel):
    userId: str
    text: str
    image: str


class deleteMessageIn(BaseModel):
    messageId: int


class recallMessageIn(BaseModel):
    messageId: int

class BlockInfo(BaseModel):
    userId: str

    