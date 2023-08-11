import time
import os
import base64

from sqlalchemy.orm import Session
from fastapi import Depends
from starlette.responses import FileResponse
from dependencies import get_db, get_current_user, canSeeThisMemory, DEFAULT_ROOM_PASSWORD, IMAGE_DIR, AUTH_USERNAME

from database import models, crud
from routers.social.social_models import *
from routers.social.social_utils import *

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

def joinRooms_handler(r: joinRoom, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    room = crud.get_room_by_roomid(db=db, room_id=r.roomId)
    if not room:
        return { "code": 1, "msg": "房间不存在", "data":{} }
    # pms为1时需要密码
    if room.pms:
        # 验证密码
        if not verify_password(r.roomPwd, room.password):
            return { "code": 2, "msg": "密码错误", "data":{} }
    # 更新房间的成员列表
    crud.update_room_user_list(db=db, room=room, user_id=current_user.stu_id)
    # 返回房间基础信息
    data = getRoomInfoById(roomId=r.roomId, db=db)
    return { "code": 0, "msg": "success", "data": data }

def editRoom_handler(r: editRoomInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    room = crud.get_room_by_roomid(db=db, room_id=r.roomId)
    if not room:
        return { "code": 1, "msg": "房间不存在", "data":{} }
    if room.creator_id != current_user.stu_id:
        return { "code": 2, "msg": "不能修改其他人的房间信息", "data":{} }
    data = crud.update_room_info(
        db=db,
        roomId=r.roomId,
        coverUrl=r.coverUrl,
        videoUrl=r.videoUrl,
        roomName=r.roomName,
        roomDescription=r.roomDescription,
        roomPms=r.roomPms,
        roomPwd=get_password_hash(r.roomPwd)
    )
    return { "code": 0, "msg": "修改成功", "data": data }

def receiveAllRoomMessages_handler(roomId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_room = crud.get_room_by_roomid(db=db, room_id=int(roomId))
    if not db_room:
        return {"code": 1, "msg": "房间不存在", "data": {}}
    
    message_list = db_room.message_list.split(',')
    data = []
    for i in message_list:
        db_message = crud.get_message_by_id(db=db, id=i)
        if not db_message:
            continue
        r = {}
        r["text"] = db_message.text
        r["image"] = db_message.image
        r["time"] = db_message.time
        r["id"] = db_message.id
        r["isRecall"] = db_message.is_recall
        r["userId"] = db_message.from_id

        # 获取发送者消息
        db_user = crud.get_user(db=db, stu_id=db_message.from_id)
        db_user_add_info = crud.get_user_add_info(db=db, stu_id=db_message.from_id)
        if db_user:
            if db_user.user_name_perm:
                r["userNikeName"] = db_user.user_name
        if db_user_add_info:
            if db_user_add_info.avatar_perm:
                r["userAvatar"] = db_user_add_info.avatar

        data.append(r)
    
    rec = 0 if len(data) == 0 else data[-1]["id"]

    db_rec = crud.get_rec_by_stuid(db=db, stu_id=current_user.stu_id)
    if db_rec:
        db_rec = crud.update_rec(db=db, stu_id=db_rec.stu_id, room_id=db_rec.room_id, message_id=rec)
    else:
        db_rec = crud.create_rec(db=db, stu_id=current_user.stu_id, room_id=roomId, message_id=rec)

    return {"code": 0, "msg": "success", "data": data}

def receiveRoomMessages_handler(roomId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_room = crud.get_room_by_roomid(db=db, room_id=int(roomId))
    if not db_room:
        return {"code": 1, "msg": "房间不存在", "data": {}}
    
    rec = 0
    db_rec = crud.get_rec_by_stuid(db=db, stu_id=current_user.stu_id)
    if db_rec:
        rec = db_rec.message_id
    else:
        db_rec = crud.create_rec(db=db, stu_id=current_user.stu_id, room_id=roomId, message_id=0)

    message_list = db_room.message_list.split(',')
    data = []
    for i in message_list:
        db_message = crud.get_message_by_id(db=db, id=i)
        if not db_message:
            continue
        if db_message.id <= rec:
            continue
        r = {}
        r["text"] = db_message.text
        r["image"] = db_message.image
        r["time"] = db_message.time
        r["id"] = db_message.id
        r["isRecall"] = db_message.is_recall
        r["userId"] = db_message.from_id

        # 获取发送者消息
        db_user = crud.get_user(db=db, stu_id=db_message.from_id)
        db_user_add_info = crud.get_user_add_info(db=db, stu_id=db_message.from_id)
        if db_user:
            if db_user.user_name_perm:
                r["userNikeName"] = db_user.user_name
        if db_user_add_info:
            if db_user_add_info.avatar_perm:
                r["userAvatar"] = db_user_add_info.avatar

        data.append(r)
    
    rec = rec if len(data) == 0 else max(rec, data[-1]["id"])
    db_rec = crud.update_rec(db=db, stu_id=current_user.stu_id, room_id=roomId, message_id=rec)

    return {"code": 0, "msg": "success", "data": data}
    
def sendRoomMessage_handler(r: roomMessage, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_room = crud.get_room_by_roomid(db=db, room_id=str(r.roomId))
    if not db_room:
        return {"code": 1, "msg": "房间不存在", "data": {}}
    
    user_list = db_room.user_list.split(',')
    if current_user.stu_id not in user_list:
        return {"code": 2, "msg": "用户不在房间内", "data": {}}
    
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    db_message = crud.create_message(db=db, from_id=current_user.stu_id, to_id='r'+r.roomId, text=r.text, image=r.image, time=t, is_read=1, is_sender_delete=0, is_receiver_delete=0, is_recall=0)
    new_message_list = db_room.message_list + ',' + str(db_message.id) if db_room.message_list != "" else db_room.message_list + str(db_message.id)
    db_room = crud.update_room_message_list(db=db, room_id=r.roomId, message_list=new_message_list)
    data = {}
    data["messageId"] = db_message.id

    return {"code": 0, "msg": "success", "data": data}

async def leaveRoom_handler(r: leaveRoomInfo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 房主永远是user_list的首元素
    # 可以移除的情况: 房主移除别人, 普通用户自己退出
    # 当房主退出时, 需要移交房主, 直接使得下一个顺位的人成为房主
    # 当没有人在房间里, 需要删除这个房间
    room = crud.get_room_by_roomid(db=db, room_id=r.roomId)
    if not room:
        return { "code": 1, "msg": "对应房间不存在", "data": {} }

    db_rec = crud.get_rec_by_stuid(db=db, stu_id=r.userId)

    # 如果当前登录用户是房主
    if room.creator_id == current_user.stu_id:
        # 如果是房主自己退出, 且房间中还有人, 将房主设置为数组中的下一个人
        if r.userId == current_user.stu_id and len(room.user_list.split(',')) > 1:
            room.creator_id = room.user_list.split(',')[1]
        # 在user_list中移除这个用户
        crud.remove_user_in_user_list(db=db, room=room, remove_id=r.userId)
        if db_rec:
            crud.delete_rec(db=db, stu_id=r.userId)
    # 如果当前登录用户与要删除的用户一致
    elif r.userId == current_user.stu_id:
        crud.remove_user_in_user_list(db=db, room=room, remove_id=r.userId)
        if db_rec:
            crud.delete_rec(db=db, stu_id=r.userId)
    else:
        return { "code": 2, "msg": "你不能移除其他用户", "data": {} }

    # 没人了要删除这个房间
    if room.user_list == "":
        crud.delete_room(db=db, room_id=r.roomId)

    if crud.get_room_by_roomid(db=db, room_id=r.roomId):
        return { "code": 0, "msg": "成员已删除", "data": room }
    else:
        return { "code": 0, "msg": "房间已删除", "data": {} }
    
def updateProgress_handler(r: roomVideo, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_room = crud.get_room_by_roomid(db=db, room_id=r.roomId)
    if not db_room:
        return {"code": 1, "msg": "对应房间不存在", "data": {}}
    if db_room.creator_id != current_user.stu_id:
        return {"code": 2, "msg": "非房主无法更新视频进度", "data": {}}
    db_room = crud.update_room_video_progress(db=db, room_id=r.roomId, video_pos_millis=r.positionMillis, video_play=r.shouldPlay, video_cur_time=r.curTime)
    return {"code": 0, "msg": "success", "data": {}}

def getProgress_handler(roomId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_room = crud.get_room_by_roomid(db=db, room_id=roomId)
    if not db_room:
        return {"code": 1, "msg": "对应房间不存在", "data": {}}
    data = {}
    data["videoUrl"] = db_room.video_url
    data["curTime"] = db_room.video_cur_time
    data["shouldPlay"] = bool(db_room.video_play)
    data["positionMillis"] = db_room.video_pos_millis
    return {"code": 0, "msg": "success", "data": data}

# -- pics --
def upload_file_handler(r: ImageRequest, current_user: models.User = Depends(get_current_user)):
    ext = r.fileName.split(".")[-1]
    fileName = f"{random_filename()}.{ext}"
    filepath = os.path.join(IMAGE_DIR, fileName)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(r.file.split(',')[1]))
    return { "code": 0, "msg": "success", "data": {"url": f"/images/{fileName}"} }

def show_image_handler(filename: str):
    filepath = os.path.join(IMAGE_DIR, filename)
    if os.path.isfile(filepath):
        return FileResponse(filepath)
    else:
        return {"error": "File not found"}
    
# -- notice --
def getNoticeNum_handler(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    data = {}
    
    # get all the lists
    like_list = crud.get_likenotice(db=db, stu_id=current_user.stu_id)
    comment_list = crud.get_commentnotice(db=db, stu_id=current_user.stu_id)
    repo_list = crud.get_reponotice(db=db, stu_id=current_user.stu_id)
    follow_list = crud.get_follownotice(db=db, stu_id=current_user.stu_id)

    # return all the unread
    data['likeNum'] = get_unread_num(like_list)
    data['commentNum'] = get_unread_num(comment_list)
    data['repoNum'] = get_unread_num(repo_list)
    data['followNum'] = get_unread_num(follow_list)

    return { "code": 0, "msg": "success", "data": data }

def getAllSystemNotice_handler(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 0
    msg = "获取成功"
    data = []

    notice_list = crud.get_all_system_notice_by_stu_id(db=db, stu_id=current_user.stu_id)

    for i in notice_list:
        e = {}
        e['message'] = i.content
        e['senderName'] = i.title
        e['timeStamp'] = i.time
        e['noticeId'] = i.id
        e['readed'] = i.read
        try:
            e['senderAvatar'] = crud.get_user_add_info(db=db, stu_id=i.admin_id).avatar
        except:
            e['senderAvatar'] = "没有数据"
            code = 1
            msg = "数据对应管理员出错"

        data.append(e)
    
    return { "code": code, "msg": msg, "data": data}

def getNoticeByType_handler(typ: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 0
    msg = "success"

    if typ == "like":
        notice_list = crud.get_likenotice(db=db, stu_id=current_user.stu_id)
    elif typ == "comment":
        notice_list = crud.get_commentnotice(db=db, stu_id=current_user.stu_id)
    elif typ == "repo":
        notice_list = crud.get_reponotice(db=db, stu_id=current_user.stu_id)
    elif typ == "follow":
        notice_list = crud.get_follownotice(db=db, stu_id=current_user.stu_id)
    else:
        return { "code": 1, "msg": "type错误", "data": [] }

    data = []

    for i in notice_list:
        e = {}
        
        try:
            db_user = crud.get_user(db=db, stu_id=i.from_stu_id)
            db_user_add_info = crud.get_user_add_info(db=db, stu_id=i.from_stu_id)
        except:
            code = 1
            msg = "数据库对应stu_id出错"
            continue

        e['senderName'] = db_user.name
        e['sendMessage'] = db_user.name + translate_type(typ)
        e['originPostTitle'] = ''

        try:
            e['originPostId'] = i.post_id
            e['originPostTitle'] = crud.get_memory(db=db, post_id=i.post_id).content
        except:
            try:
                e['originPostId'] = crud.get_comment(db=db, comment_id=i.comment_id).post_id
                e['originPostTitle'] = crud.get_memory(db=db, post_id=e['originPostId']).content
                
            except:
                e['originPostId'] = -1
            
        try:
            e['originCommentId'] = i.comment_id
            e['sendMessage'] += ': ' + crud.get_comment(db=db, comment_id=i.comment_id).content
        except:
            e['originCommentId'] = -1
        
        e['senderAvatar'] = db_user_add_info.avatar
        e['timeStamp'] = i.time
        e['noticeId'] = i.id
        
        data.append(e)

    return { "code": code, "msg": msg, "data": data }

def deleteNotice_handler(r: noticeIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if r.typ == "like":
        crud.delete_likenotice(db=db, id=r.noticeId)
    elif r.typ == "repo":
        crud.delete_reponotice(db=db, id=r.noticeId)
    elif r.typ == "comment":
        crud.delete_commentnotice(db=db, id=r.noticeId)
    elif r.typ == "follow":
        crud.delete_follownotice(db=db, id=r.noticeId)
    else:
        return { "code": 1, "msg": "type错误", "data": {} }

    return { "code": 0, "msg": "success", "data": {} }

def readNoticeByType_handler(typ: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 0
    msg = "success"

    if typ == "like":
        notice_list = crud.get_likenotice(db=db, stu_id=current_user.stu_id)
    elif typ == "comment":
        notice_list = crud.get_commentnotice(db=db, stu_id=current_user.stu_id)
    elif typ == "repo":
        notice_list = crud.get_reponotice(db=db, stu_id=current_user.stu_id)
    elif typ == "follow":
        notice_list = crud.get_follownotice(db=db, stu_id=current_user.stu_id)
    else:
        return { "code": 1, "msg": "type错误", "data": {} }

    for i in notice_list:
        if i.read == 0:
            if typ == "like":
                db_notice = crud.update_likenotice(db=db, id=i.id, read=1)
            elif typ == "comment":
                db_notice = crud.update_commentnotice(db=db, id=i.id, read=1)
            elif typ == "repo":
                db_notice = crud.update_reponotice(db=db, id=i.id, read=1)
            elif typ == "follow":
                db_notice = crud.update_follownotice(db=db, id=i.id, read=1)
    
    return { "code": 0, "msg": "success", "data": {} }

# -- memories --
def getMemories_handler(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 1
    msg = "没有动态"
    data = []
    memories_list = crud.get_memories(db=db)
    memories_list.reverse()
    if memories_list:
        code = 0
        msg = "返回成功"
        for memory in memories_list:
            if not canSeeThisMemory(db=db, current_user=current_user, memory=memory):
                continue
            e = {}

            try:
                e['userId'] = crud.get_user(db=db, stu_id=memory.stu_id).stu_id
                e['userName'] = crud.get_user(db=db, stu_id=memory.stu_id).user_name
            except:
                return { "code": 2, "msg": "动态对应用户出错", "data": data }

            db_user_add_info = crud.get_user_add_info(db=db, stu_id=memory.stu_id)
            if db_user_add_info:
                try:
                    e['userAvatar'] = db_user_add_info.avatar
                except:
                    e['userAvatar'] = ""
            else:
                e['userAvatar'] = ""
            
            if memory.photo_list:
                try:
                    e['postPhoto'] = crud.get_photo(db=db, photo_id=memory.photo_list.split(',')[0]).address
                except:
                    return { "code": 3, "msg": "动态对应照片出错", "data": data }
            else:
                e['postPhoto'] = ""

            e['postTime'] = memory.time
            e['postId'] = str(memory.post_id)
            e['likeNum'] = str(len(memory.like_list.split(','))) if memory.like_list else '0'
            e['commentNum'] = str(len(memory.comment_list.split(','))) if memory.comment_list else '0'
            e['repoNum'] = str(len(memory.repo_list.split(','))) if memory.repo_list else '0'
            e['isLiked'] = current_user.stu_id in memory.like_list.split(',')
            e['isAnonymous'] = bool(memory.is_anonymous)

            data.append(e)
    
    return { "code": code, "msg": msg, "data": data }

def getMemoryDetail_handler(postId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 1
    msg = "动态号错误"
    data = {}
    memory = crud.get_memory(db=db, post_id=postId)
    if memory:
        code = 0
        msg = "返回成功"
        
        data['likeNum'] = str(len(memory.like_list.split(','))) if memory.like_list != "" else '0'
        data['repoNum'] = str(len(memory.repo_list.split(','))) if memory.repo_list != "" else '0'
        data['postTime'] = memory.time
        data['postContent'] = memory.content
        data['postPhoto'] = []
        data['isAnonymous'] = bool(memory.is_anonymous)
        data['pms'] = memory.pms

        try:
            data['userId'] = crud.get_user(db=db, stu_id=memory.stu_id).stu_id
            data['userName'] = crud.get_user(db=db, stu_id=memory.stu_id).user_name
        except:
            return { "code": 2, "msg": "动态对应用户出错", "data": data }
        
        try:
            data['userAvatar'] = crud.get_user_add_info(db=db, stu_id=memory.stu_id).avatar
        except:
            data['userAvatar'] = ""

        if memory.photo_list:
            try:
                for photo_id in memory.photo_list.split(','):
                    data['postPhoto'].append(crud.get_photo(db=db, photo_id=photo_id).address)
            except:
                return { "code": 3, "msg": "动态对应照片出错", "data": data }

        data['isLiked'] = current_user.stu_id in memory.like_list.split(',')
        data['comments'] = []
        # 有评论才能查看
        for comment_id in memory.comment_list.split(','):
            if not comment_id:
                break
            e = {}
            try:
                comment = crud.get_comment(db=db, comment_id=comment_id)
            except:
                return { "code": 4, "msg": "动态对应评论出错", "data": data }
            e['commentId'] = comment.comment_id
            e['likeNum'] = 0 if comment.like_list == "" else len(comment.like_list.split(','))
            e['isLiked'] = current_user.stu_id in comment.like_list.split(',')
            e['postTime'] = comment.time
            e['commentContent'] = comment.content
            try:
                e['userId'] = crud.get_user(db=db, stu_id=comment.stu_id).stu_id
                e['userName'] = crud.get_user(db=db, stu_id=comment.stu_id).user_name
                e['userAvatar'] = crud.get_user_add_info(db=db, stu_id=comment.stu_id).avatar
            except:
                return { "code": 5, "msg": "评论对应用户出错", "data": data }
            data['comments'].append(e)

    return { "code": code, "msg": msg, "data": data }

def postMemory_handler(r: memoryIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    data = {}

    photo_list = []
    for i in r.photoUrl:
        db_photo = crud.get_photo_by_address(db=db, address=i)
        if db_photo:
            photo_list.append(db_photo.photo_id)
        else:
            db_photo = crud.create_photo(db=db, address=i)
            photo_list.append(db_photo.photo_id)

    crud.create_memory(db=db, stu_id=current_user.stu_id, content=r.postContent, photo_url=photo_list, pms=(1 if r.pms == None else r.pms), is_anonymous=r.isAnonymous)

    return { "code": 0, "msg": "success", "data": data }

def updateMemory_handler(postId: str, r: memoryIn, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 验证是否存在该动态
    db_memory = crud.get_memory(db=db, post_id=postId)
    if not db_memory:
        return { "code": 1, "msg": "该postId对应的动态不存在", "data": {} }

    # 验证权限
    if current_user.stu_id != db_memory.stu_id:
        return { "code": 2, "msg": "非该用户的动态，没有权限修改", "data": {} }

    photo_list = []
    for i in r.photoUrl:
        db_photo = crud.get_photo_by_address(db=db, address=i)
        if db_photo:
            photo_list.append(db_photo.photo_id)
        else:
            db_photo = crud.create_photo(db=db, address=i)
            photo_list.append(db_photo.photo_id)
    
    crud.update_memory(db=db, post_id=postId, content=r.postContent, photo_url=photo_list, pms=(1 if r.pms == None else r.pms))

    return { "code": 0, "msg": "success", "data": {} }

def deleteMemory_handler(postId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 验证是否存在该动态
    db_memory = crud.get_memory(db=db, post_id=postId)
    if not db_memory:
        return { "code": 1, "msg": "该postId对应的动态不存在", "data": {} }

    # 验证权限
    if current_user.stu_id != db_memory.stu_id and current_user.stu_id != AUTH_USERNAME:
        return { "code": 2, "msg": "非该用户的动态，没有权限删除", "data": {} }

    # 删除对应的评论
    for i in db_memory.comment_list.split(','):
        if crud.get_comment(db=db, comment_id=i):
            crud.delete_comment(db=db, comment_id=i)
    crud.delete_memory(db=db, post_id=postId)

    return {"code": 0, "msg": "success", "data": {}}

def updateLikeMemory_handler(postId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 验证是否存在该动态
    db_memory = crud.get_memory(db=db, post_id=postId)
    if not db_memory:
        return { "code": 1, "msg": "该postId对应的动态不存在", "data": {} }
    
    # 更新点赞状态
    new_like_list = db_memory.like_list

    if current_user.stu_id in db_memory.like_list.split(','):
        if db_memory.like_list != "" and current_user.stu_id == db_memory.like_list.split(',')[0]:
            if len(db_memory.like_list.split(',')) == 1:
                new_like_list = new_like_list.replace(current_user.stu_id, "")
            else:
                new_like_list = new_like_list.replace(current_user.stu_id + ",", "")
        else:
            new_like_list = db_memory.like_list.replace("," + current_user.stu_id, "")
        msg = "取消点赞"
    else:
        if db_memory.like_list != "":
            new_like_list += ("," + str(current_user.stu_id))
        else:
            new_like_list += (str(current_user.stu_id))
        msg = "点赞"

    crud.update_like_memory(db=db, post_id=postId, new_like_list=new_like_list)

    data = {}

    try:
        data['likeNum'] = 0 if db_memory.like_list == "" else len(db_memory.like_list.split(','))
    except:
        data['likeNum'] = 0
    
    data['isLiked'] = bool(current_user.stu_id in db_memory.like_list.split(','))

    # 产生点赞消息
    if msg == "点赞":
        db_notice = crud.create_likenotice(db=db, from_stu_id=current_user.stu_id, to_stu_id=db_memory.stu_id, post_id=postId, comment_id=-1)
    
    return { "code": 0, "msg": msg, "data": data }

# -- follow --
def follow_handler(info: follow_info, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 0
    msg = {}

    # 在建立数据库的时候就将自己加入关注列表中?
    # 不能对自己执行关注操作
    if info.stuid == current_user.stu_id:
        code = 1
        msg = {"不能对自己执行该操作"}
        return {
            "code": code,
            "msg": msg
        }

    # 如果已经关注, 不做操作
    flag = False
    followings_list = crud.get_followings(db=db, stu_id=current_user.stu_id)
    if followings_list:
        code = 0
        for i in followings_list:
            if info.stuid == i.followed: 
                flag = True
                break
    if flag:
        code = 2
        msg = {"已经关注该用户"}
        return {
            "code": code,
            "msg": msg
        }

    # 建立关注关系
    db_follow = crud.create_follow(db=db, followed_id=info.stuid, follower_id=current_user.stu_id)
    msg = {"关注成功"}

    # 产生关注消息
    db_notice = crud.create_follownotice(db=db, from_stu_id=current_user.stu_id, to_stu_id=info.stuid)

    return {
        "code": code,
        "msg": msg,
        "db_follow": db_follow
    }

def unfollow_handler(info: follow_info, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    code = 0
    msg = {}

    # 不能对自己执行取关操作
    if info.stuid == current_user.stu_id:
        code = 1
        msg = {"不能对自己执行该操作"}
        return {
            "code": code,
            "msg": msg
        }

    # 如果并未关注, 不做操作
    flag = False
    followings_list = crud.get_followings(db=db, stu_id=current_user.stu_id)
    if followings_list:
        code = 0
        for i in followings_list:
            if info.stuid == i.followed: 
                flag = True
                break
    if not flag:
        code = 2
        msg = {"并未关注该用户"}
        return {
            "code": code,
            "msg": msg
        }

    # 删除关注关系
    db_follow = crud.delete_follow(db=db, followed_id=info.stuid, follower_id=current_user.stu_id)
    msg = {"取关成功"}
    return {
        "code": code,
        "msg": msg,
        "db_follow": db_follow
    }

# -- draft --
def getDrafts_handler(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    data = []
    draft_list = crud.get_drafts_by_stu_id(db=db, stu_id=current_user.stu_id)
    for i in draft_list:
        if i.is_posted == 0:
            r = {}
            r["draftId"] = str(i.id)
            r["content"] = i.content
            r["time"] = i.time
            r["pms"] = i.pms
            r["isAnonymous"] = i.is_anonymous
            r["photoUrl"] = []
            photo_list = i.photo_list.split(',')
            for i in photo_list:
                try:
                    r["photoUrl"].append(crud.get_photo(db=db, photo_id=int(i)).address)
                except:
                    continue
            print(photo_list)
            data.append(r)
    return {"code": 0, "msg": "success", "data": data}

def createDraft_handler(r: draft, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    data = {}
    print(r.photoUrl)
    print(len(r.photoUrl))
    photo_encode_list = []
    for i in r.photoUrl:
        print(i)
        db_photo = crud.get_photo_by_address(db=db, address=i)
        if db_photo:
            photo_encode_list.append(db_photo.photo_id)
        else:
            db_photo = crud.create_photo(db=db, address=i)
            photo_encode_list.append(db_photo.photo_id)
        print(db_photo.photo_id)
    
    photo_list = ""
    for i in photo_encode_list:
        photo_list += str(i)
        photo_list += ","

    if len(photo_list) > 0:
        if photo_list[-1] == ",":
            photo_list = photo_list[0:-1]

    print(photo_list)

    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    db_draft = crud.create_draft(db=db, stu_id=current_user.stu_id, content=r.postContent, photo_list=photo_list, time=t, pms=r.pms, is_anonymous=r.isAnonymous, is_posted=0)

    data["draftId"] = db_draft.id

    return {"code": 0, "msg": "success", "data": data}
    
def updateDraft_handler(r: draft, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if r.draftId == None:
        return {"code": 1, "msg": "draft id 缺失", "data": {}}
    elif crud.get_draft_by_id(db=db, id=r.draftId) == None:
        return {"code": 2, "msg": "draft id 错误", "data": {}}
    elif crud.get_draft_by_id(db=db, id=r.draftId).stu_id != current_user.stu_id:
        return {"code": 3, "msg": "当前用户无编辑该草稿的权限", "data": {}}

    photo_encode_list = []
    for i in r.photoUrl:
        db_photo = crud.get_photo_by_address(db=db, address=i)
        if db_photo:
            photo_encode_list.append(db_photo.photo_id)
        else:
            db_photo = crud.create_photo(db=db, address=i)
            photo_encode_list.append(db_photo.photo_id)
    
    photo_list = ""
    for i in photo_encode_list:
        photo_list += str(i)
        photo_list += ","

    if len(photo_list) > 0:
        if photo_list[-1] == ",":
            photo_list = photo_list[0:-1]

    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    db_draft = crud.update_draft(db=db, id=r.draftId, stu_id=current_user.stu_id, content=r.postContent, photo_list=photo_list, time=t, pms=r.pms, is_anonymous=r.isAnonymous, is_posted=0)

    return {"code": 0, "msg": "success", "data": {}}

def postDraft_handler(r: DraftId, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_draft = crud.get_draft_by_id(db=db, id=r.draftId)

    if db_draft == None:
        return {"code": 1, "msg": "draft id 错误", "data": {}}
    elif db_draft.stu_id != current_user.stu_id:
        return {"code": 2, "msg": "当前用户无编辑该草稿的权限", "data": {}}
    
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    db_draft = crud.update_draft(db=db, id=db_draft.id, stu_id=current_user.stu_id, content=db_draft.content, photo_list=db_draft.photo_list, time=db_draft.time, pms=db_draft.pms, is_anonymous=db_draft.is_anonymous, is_posted=1)
    db_memory = crud.create_draft_memory(db=db, stu_id=current_user.stu_id, content=db_draft.content, photo_list=db_draft.photo_list, time=t, pms=db_draft.pms, is_anonymous=db_draft.is_anonymous)

    return {"code": 0, "msg": "success", "data": {}}

def getDraft_handler(draftId: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_draft = crud.get_draft_by_id(db=db, id=draftId)

    if db_draft == None:
        return {"code": 1, "msg": "draft id 错误", "data": {}}
    elif db_draft.stu_id != current_user.stu_id:
        return {"code": 2, "msg": "当前用户无查看该草稿的权限", "data": {}}
    
    data = {}
    data["content"] = db_draft.content
    
    
    data["time"] = db_draft.time
    data["pms"] = db_draft.pms
    data["isAnonymous"] = db_draft.is_anonymous
    data["photoUrl"] = []

    photo_list = db_draft.photo_list.split(',')
    try:
        for i in photo_list:
            data["photoUrl"].append(crud.get_photo(db=db, photo_id=i).address)
    except:
        return { "code": 0, "msg": "草稿对应照片出错", "data": data }

    return {"code": 0, "msg": "success", "data": data}

def deleteDraft_handler(r: DraftId, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    draftId = r.draftId
    
    db_draft = crud.get_draft_by_id(db=db, id = draftId)

    if db_draft:
        crud.delete_draft(db=db, id=draftId)
        return {"code": 0, "msg": "success", "data": {}}
    else:
        return {"code": 1, "msg": "该draftId对应的草稿不存在", "data": {}}