from fastapi import APIRouter, Depends, HTTPException, status
from database import crud, models
from dependencies import get_db, get_current_user
from sqlalchemy.orm import Session

from routers.social.social_models import noticeIn
from routers.social.social_handler import getNoticeNum_handler, getAllSystemNotice_handler, getNoticeByType_handler, \
    deleteNotice_handler, readNoticeByType_handler

router = APIRouter()

# 获取消息数量
@router.get("/notice/num4each")
async def getNoticeNum(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getNoticeNum_handler(db=db, current_user=current_user)


# 获取所有系统消息
@router.get("/notice/getAllSystemNotice")
async def getAllSystemNotice(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getAllSystemNotice_handler(db=db, current_user=current_user)


# 获取通知详情
@router.get("/notice/getNoticeByType/{typ}")
async def getNoticeByType(typ: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getNoticeByType_handler(db=db, current_user=current_user, typ=typ)


# 删除选定通知
@router.post("/notice/deleteNotice")
async def deleteNotice(r: noticeIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return deleteNotice_handler(db=db, current_user=current_user, r=r)


# 已读各类通知
@router.post("/notice/readNoticeByType/{typ}")
async def readNoticeByType(typ: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return readNoticeByType_handler(db=db, current_user=current_user, typ=typ)
