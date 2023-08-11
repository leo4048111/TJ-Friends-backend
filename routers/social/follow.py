from fastapi import APIRouter, Depends
from database import models
from dependencies import get_db, get_current_user
from sqlalchemy.orm import Session

from routers.social.social_models import follow_info
from routers.social.social_handler import follow_handler, unfollow_handler

router = APIRouter()

# current_user 关注 stuid
@router.post("/follow")
async def follow(info: follow_info, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return follow_handler(db=db, current_user=current_user, info=info)

# current_user 取关 stuid
@router.post("/unfollow")
async def unfollow(info: follow_info, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return unfollow_handler(db=db, current_user=current_user, info=info)