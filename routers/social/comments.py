from fastapi import APIRouter, Depends
from database import crud, models
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user, AUTH_USERNAME

from routers.social.social_models import postCommentIn, deleteCommentInfo
from routers.social.social_handler import updateLikeComment_handler, postComment_handler, deleteComment_handler

router = APIRouter()

# 更新点赞状态
@router.get("/updateLikeComment/{commentId}")
async def updateLikeComment(commentId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return updateLikeComment_handler(db=db, current_user=current_user, commentId=commentId)

# 发布评论
@router.post("/postComment")
async def postComment(r: postCommentIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return postComment_handler(db=db, current_user=current_user, r=r)

# 删除评论
@router.post("/deleteComment")
async def deleteComment(info: deleteCommentInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return deleteComment_handler(db=db, current_user=current_user, info=info)
