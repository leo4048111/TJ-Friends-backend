from fastapi import APIRouter, Depends
from database import models
from dependencies import get_db, get_current_user, DEFAULT_ROOM_PASSWORD
from sqlalchemy.orm import Session

from routers.user.user_models import SocketId
from routers.user.user_handler import endMatch_handler, startMatch_handler, queryMatch_handler, uploadSocketId_handler, getSocketId_handler

router = APIRouter()

# 结束匹配
@router.post("/endMatch")
async def endMatch(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return endMatch_handler(db=db, current_user=current_user)


# 开始匹配
@router.post("/startMatch")
async def startMatch(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return startMatch_handler(db=db, current_user=current_user)


# 查询匹配状态
@router.get("/queryMatch")
async def queryMatch(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return queryMatch_handler(db=db, current_user=current_user)
        

# 更新socketId
@router.post("/match/uploadSocketId")
async def uploadSocketId(r: SocketId, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return uploadSocketId_handler(db=db, current_user=current_user, r=r)


# 获取socketId
@router.get("/match/getSocketId/{userId}")
async def getSocketId(userId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getSocketId_handler(db=db, current_user=current_user, userId=userId)