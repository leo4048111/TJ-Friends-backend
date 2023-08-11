from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies import get_db

from routers.user.user_models import registerIn, updatePwdIn
from routers.user.user_handler import register_error_handler, register_valid_handler, updatePassword_handler


router = APIRouter()


@router.get("/register")
async def register():
    return register_error_handler()

@router.post("/register")
async def register(r: registerIn, db: Session = Depends(get_db)):
    return register_valid_handler(r=r, db=db)


# 修改密码
@router.post("/updatePassword")
async def updatePassword(r: updatePwdIn, db: Session = Depends(get_db)):
    return updatePassword_handler(r=r, db=db)