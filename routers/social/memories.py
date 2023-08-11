from fastapi import APIRouter, Depends
from database import models
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user

from routers.social.social_handler import getMemories_handler, getMemoryDetail_handler, updateMemory_handler, postMemory_handler, deleteMemory_handler, updateLikeMemory_handler
from routers.social.social_models import memoryIn

router = APIRouter()

# 动态广场
# pms == 0 时, 所有人可见
# pms == 1 时, 仅互关好友可见
# pms == 2 时, 仅关注当前用户的人可见
# pms == 3 时, 仅自己可见
@router.get("/Memories")
async def getMemories(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getMemories_handler(db=db, current_user=current_user)


# 动态详情
@router.get("/Memories/{postId}")
async def getMemoryDetail(postId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getMemoryDetail_handler(db=db, current_user=current_user, postId=postId)


# 发布动态
@router.post("/Post")
async def postMemory(r: memoryIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return postMemory_handler(db=db, current_user=current_user, r=r)

# 编辑动态
@router.put("/updateMemory/{postId}")
async def updateMemory(postId: str, r: memoryIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return updateMemory_handler(db=db, current_user=current_user, postId=postId, r=r)


# 删除动态
@router.get("/deleteMemory/{postId}")
async def deleteMemory(postId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return deleteMemory_handler(db=db, current_user=current_user, postId=postId)


# 更新点赞状态
@router.get("/updateLikeMemory/{postId}")
async def updateLikeMemory(postId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return updateLikeMemory_handler(db=db, current_user=current_user, postId=postId)
