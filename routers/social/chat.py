from fastapi import APIRouter, Depends
from database import crud, models
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
import time

from routers.social.social_models import sendMessageIn, userIdIn, deleteMessageIn, recallMessageIn
from routers.social.social_handler import getLastMessage_handler, sendMessage_handler, receiveAllMessages_handler, \
    deleteMessages_handler, readMessageInfo_handler, receiveUnreadMessages_handler, deleteMessage_handler, recallMessage_handler

router = APIRouter()

@router.get("/chat/getMessageInfo")
async def getLastMessage(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return getLastMessage_handler(db=db, current_user=current_user)


@router.post("/chat/sendMessage")
async def sendMessage(r: sendMessageIn, db: Session = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    return sendMessage_handler(db=db, current_user=current_user, r=r)


@router.get("/chat/receiveAllMessages")
async def receiveAllMessages(userId: str, db: Session = Depends(get_db),
                             current_user: models.User = Depends(get_current_user)):
    return receiveAllMessages_handler(db=db, current_user=current_user, userId=userId)


@router.post("/chat/deleteMessages")
async def deleteMessages(r: userIdIn, db: Session = Depends(get_db),
                        current_user: models.User = Depends(get_current_user)):
    return deleteMessages_handler(db=db, current_user=current_user, r=r)


@router.post("/chat/readMessageInfo")
async def readMessageInfo(r: userIdIn, db: Session = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    return readMessageInfo_handler(db=db, current_user=current_user, r=r)


@router.get("/chat/receiveUnreadMessages")
async def receiveUnreadMessages(userId: str, db: Session = Depends(get_db),
                                current_user: models.User = Depends(get_current_user)):
    return receiveUnreadMessages_handler(db=db, current_user=current_user, userId=userId)


@router.post("/chat/deleteMessage")
async def deleteMessage(r: deleteMessageIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return deleteMessage_handler(db=db, current_user=current_user, r=r)


@router.post("/chat/recallMessage")
async def recallMessage(r: recallMessageIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return recallMessage_handler(db=db, current_user=current_user, r=r)


