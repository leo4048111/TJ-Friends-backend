from fastapi import APIRouter, Depends
from database import models
from dependencies import get_db, get_current_user
from sqlalchemy.orm import Session

from routers.social.social_handler import getDrafts_handler, createDraft_handler, updateDraft_handler, postDraft_handler, getDraft_handler, deleteDraft_handler
from routers.social.social_models import draft, DraftId 

router = APIRouter()

# drafts 草稿列表
@router.get("/drafts")
async def getDrafts(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getDrafts_handler(db=db, current_user=current_user)
    

# 创建草稿
@router.post("/createDraft")
async def createDraft(r: draft, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return createDraft_handler(db=db, current_user=current_user, r=r)


# 编辑草稿
@router.post("/updateDraft")
async def updateDraft(r: draft, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return updateDraft_handler(db=db, current_user=current_user, r=r)


# 发布草稿
@router.post("/postDraft")
async def postDraft(r: DraftId, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return postDraft_handler(db=db, current_user=current_user, r=r)

# 获取草稿详情
@router.get("/getDraft")
async def getDraft(draftId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getDraft_handler(db=db, current_user=current_user, draftId=draftId)

# 删除草稿
@router.post("/deleteDraft")
def deleteDraft(r: DraftId, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return deleteDraft_handler(db=db, current_user=current_user, r=r)
