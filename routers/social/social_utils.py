from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import crud

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -- room --
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 将字符串形式的成员列表转为列表
def getMembers(user_list: str):
    ret = []
    for user in user_list.split(','):
        ret.append(user)
    return ret

# 通过房间号取得可以查看的信息
def getRoomInfoById(roomId: str, db: Session):
    room = crud.get_room_by_roomid(db=db, room_id=roomId)
    data = {}
    try:
        data['creatorId'] = crud.get_user(db=db, stu_id=room.creator_id).stu_id
        data['creatorName'] = crud.get_user(db=db, stu_id=room.creator_id).user_name
    except:
        return { "code": 3, "msg": "房间对应用户出错", "data": data }
    data['roomId'] = room.id
    data['ownerId'] = room.creator_id
    data['coverUrl'] = room.cover_url
    data['videoUrl'] = room.video_url
    data['roomName'] = room.name
    data['roomPms'] = bool(room.pms)
    data['roomDescription'] = room.description
    data['members'] = getMembers(room.user_list)
    return data