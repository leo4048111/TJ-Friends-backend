from fastapi import APIRouter, Depends
from database import models
from dependencies import get_db, get_current_user
from sqlalchemy.orm import Session

from routers.user.user_models import userIn
from routers.user.user_handler import followers_handler, followings_handler, getUserInfo_handler, updateUserInfo_handler, \
    getLabels_handler, getUserMemories_handler

router = APIRouter()

# 粉丝
@router.get("/profile/{stuid}/followers")
async def followers(stuid: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return followers_handler(db=db, current_user=current_user, stuid=stuid)

# 获取关注的人
@router.get("/profile/{stuid}/followings")
async def followings(stuid: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return followings_handler(db=db, current_user=current_user, stuid=stuid)

# 获得用户资料
@router.get("/profile/{stuid}")
async def getUserInfo(stuid: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getUserInfo_handler(db=db, current_user=current_user, stuid=stuid)

# 修改用户信息
@router.put("/updateUserInfo")
async def updateUserInfo(r: userIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return updateUserInfo_handler(db=db, current_user=current_user, r=r)


# 获取所有标签
@router.get("/getAllLabels")
async def getLabels(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getLabels_handler(db=db, current_user=current_user)


# 获取用户所有动态
@router.get("/getUserMemories/{userId}")
async def getUserMemories(userId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getUserMemories_handler(db=db, current_user=current_user, userId=userId)

