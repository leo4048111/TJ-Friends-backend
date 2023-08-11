from fastapi import APIRouter, Depends
from database import models
from dependencies import get_db, get_current_user
from sqlalchemy.orm import Session

from routers.social.social_models import BlockInfo
from routers.social.social_handler import blockUser_handler, unBlockUser_handler, getBlockList_handler
router = APIRouter()

# 拉黑用户
@router.post("/block")
async def blockUser(r: BlockInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return blockUser_handler(db=db, current_user=current_user, r=r)

# 解除拉黑
@router.post("/cancelBlock")
async def unBlockUser(r: BlockInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return unBlockUser_handler(db=db, current_user=current_user, r=r, cancel=True)

# 查看黑名单
@router.get("/getBlockList")
async def getBlockList(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getBlockList_handler(db=db, current_user=current_user)