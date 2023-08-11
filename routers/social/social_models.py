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