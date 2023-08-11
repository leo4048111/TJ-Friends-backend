from fastapi import APIRouter, Depends
from database import crud, models
from dependencies import get_db, get_current_user, DEFAULT_ROOM_PASSWORD
from sqlalchemy.orm import Session
import time

from routers.social.social_models import room, joinRoom, editRoomInfo, roomMessage, leaveRoomInfo, roomVideo
from routers.social.social_utils import getRoomInfoById
from routers.social.social_handler import createRoom_handler, getAllRooms_handler, \
joinRooms_handler, editRoom_handler, receiveAllRoomMessages_handler, \
receiveRoomMessages_handler, sendRoomMessage_handler, leaveRoom_handler, \
updateProgress_handler, getProgress_handler

router = APIRouter()

# 创建房间
@router.post("/createRoom")
async def createRoom(r: room, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return createRoom_handler(r=r, db=db, current_user=current_user)

# 获取房间列表
@router.get("/rooms")
async def getAllRooms(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getAllRooms_handler(db=db, current_user=current_user)

# 加入房间
@router.post("/joinRoom")
async def joinRooms(r: joinRoom, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return joinRooms_handler(r=r, db=db, current_user=current_user)

# 获取房间详情
@router.get("/getRoomInfo")
async def getRoomInfo(roomId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return {"code": 0, "msg": "success", "data": getRoomInfoById(roomId=roomId, db=db)}

# 编辑房间信息
@router.put("/editRoom")
async def editRoom(r: editRoomInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return editRoom_handler(r=r, db=db, current_user=current_user)

# 接收房间所有消息
@router.get("/receiveAllRoomMessages")
async def receiveAllRoomMessages(roomId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return receiveAllRoomMessages_handler(roomId=roomId, db=db, current_user=current_user)

# 接受房间未读消息
@router.get("/receiveRoomMessages")
async def receiveRoomMessages(roomId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return receiveRoomMessages_handler(roomId=roomId, db=db, current_user=current_user)


# 发送房间信息
@router.post("/sendRoomMessage")
async def sendRoomMessage(r: roomMessage, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return sendRoomMessage_handler(r=r, db=db, current_user=current_user)

# 从房间移除一个用户
@router.post("/leaveRoom")
async def leaveRoom(r: leaveRoomInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    leaveRoom_handler(r=r, db=db, current_user=current_user)


# 更新视频进度
@router.post("/updateProgress")
async def updateProgress(r: roomVideo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    updateProgress_handler(r=r, db=db, current_user=current_user)


# 获取当前视频进度
@router.get("/getProgress")
async def getProgress(roomId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    getProgress_handler(roomId=roomId, db=db, current_user=current_user)