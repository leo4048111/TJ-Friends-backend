from sqlalchemy.orm import Session
from fastapi import Depends
from dependencies import get_db, get_current_user, DEFAULT_ROOM_PASSWORD

from database import models, crud
from social_models import room
from social_utils import get_password_hash

# -- room --
def createRoom_handler(r: room, db: Session, current_user: models.User):
    if r.roomPwd == None:
        r.roomPwd = DEFAULT_ROOM_PASSWORD

    room = crud.create_room(
        db=db, 
        creator_id=current_user.stu_id, 
        password=get_password_hash(r.roomPwd), 
        cover_url=r.coverUrl, 
        video_url=r.videoUrl, 
        name=r.roomName, 
        description=r.roomDescription, 
        pms=r.roomPms)

    return { "code": 0, "msg": "success", "data": room }

def getAllRooms_handler(db: Session, current_user: models.User):
    code = 1
    msg = "没有房间"
    data = []

    room_list = crud.get_all_rooms(db=db)
    room_list.reverse()

    if room_list:
        code = 0
        msg = "返回成功"
        for room in room_list:
            if room.pms:
                continue
            e = {}
            try:
                e['creatorId'] = crud.get_user(db=db, stu_id=room.creator_id).stu_id
                e['creatorName'] = crud.get_user(db=db, stu_id=room.creator_id).user_name
            except:
                return { "code": 2, "msg": "房间对应用户出错", "data": data }
            e['roomId'] = room.id
            e['coverUrl'] = room.cover_url
            e['roomName'] = room.name
            e['roomDescription'] = room.description
            data.append(e)
    return { "code": code, "msg": msg, "data": data }