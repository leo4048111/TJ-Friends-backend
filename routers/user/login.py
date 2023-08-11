from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dependencies import get_db

from routers.user.user_handler import login_error_handler, login_valid_handler

router = APIRouter()

@router.get("/login")
async def login():
    return login_error_handler()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return login_valid_handler(form_data=form_data, db=db)
