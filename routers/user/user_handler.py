import time
import requests

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from dependencies import canSeeThisMemory, ACCESS_TOKEN_EXPIRE_MINUTES
from database import crud, models

from routers.user.user_models import *
from routers.user.user_utils import *

# -- register --

def register_error_handler():
    code = 0
    msg = "Please use POST method to register."
    data = {}
    return {
        "code": code,
        "msg": msg,
        "data": data
    }

def register_valid_handler(r: registerIn, db: Session):
    # 定义返回变量
    code = 0
    msg = "注册成功"
    data = {}

    db_user = crud.get_user(db=db, stu_id=r.id)
    if db_user:
        return {
            "code": 1,
            "msg": "用户已存在",
            "data": data
        }
        
    try:
        url = "https://1.tongji.edu.cn/api/sessionservice/session/getSessionUser"
        cookies = {"sessionid": r.sessionid}
        response = requests.get(url=url, cookies=cookies).json()
        name = response['data']['user']['name']
        sex = response['data']['user']['sex']
        faculty = response['data']['user']['facultyName']
    except:
        return {
            "code": 2,
            "msg": "sessionid错误",
            "data": data
        }

    if r.id == response['data']['uid']:
        db_user = crud.create_user(db=db, user_id=r.id, password=get_password_hash(r.password), user_name=r.username, name=name, sex=sex, faculty=faculty)
        db_user_add_info = crud.create_user_add_info(db=db, stu_id=r.id)
        data['name'] = name
        data['sex'] = sex
        data['faculty'] = faculty
        db_user_add_info["avatar"] = "https://picsum.photos/700"
    else:
        code = 3
        msg = "sessionid不匹配"

    # 关注自己
    db_follow = crud.create_follow(db=db, followed_id=r.id, follower_id=r.id)
    
    return {
        "code": code,
        "msg": msg,
        "data": data
    }

def updatePassword_handler(r: updatePwdIn, db: Session):
     # 定义返回变量
    code = 0
    msg = "修改密码成功"
    data = {}

    db_user = crud.get_user(db=db, stu_id=r.id)
    if not db_user:
        return {
            "code": 1,
            "msg": "用户不存在",
            "data": data
        }
    
    try:
        url = "https://1.tongji.edu.cn/api/sessionservice/session/getSessionUser"
        cookies = {"sessionid": r.sessionid}
        response = requests.get(url=url, cookies=cookies).json()
    except:
        return {
            "code": 2,
            "msg": "sessionid错误",
            "data": data
        }

    if r.id == response['data']['uid']:
        crud.update_user_pwd(db=db, stu_id=r.id, password=get_password_hash(r.password))
    else:
        code = 3
        msg = "sessionid不匹配"
        
    
    return {
        "code": code,
        "msg": msg,
        "data": data
    }

# -- profile --
def followers_handler(stuid: str, db: Session, current_user: models.User):
    code = 0
    data = {}

    # 判断查看的是否是自己的粉丝列表
    # 当以下 2 项均为 False , 不可查看粉丝列表
    data['is_current_user'] = True
    data["get_others_followers"] = False
    if stuid != current_user.stu_id:
        data['is_current_user'] = False
        other_user = crud.get_user(db=db, stu_id=stuid)
        data['get_others_followers'] = bool(other_user.follower_perm)
    if not data["is_current_user"] and not data['get_others_followers']:
        code = 2
        msg = {"由于对方的隐私设置, 你不能查看ta的粉丝列表"}
        return {
            "code": code,
            "msg": msg
        }

    # isFollowed  表示这个用户是否关注了当前登录用户
    # isFollowing 表示当前登录用户是否关注了这个用户
    # 当 is_current_user 为真时, isFollowed 为真
    data['followers'] = []
    followers_list = crud.get_followers(db=db, stu_id=stuid)
    if followers_list:
        # 用 i 遍历粉丝列表
        for i in followers_list:
            if data['is_current_user'] and i.follower == current_user.stu_id:
                continue
            if not data['is_current_user'] and i.follower == stuid:
                continue
            e = {}
            e['userId'] = i.follower
            e['isFollowed'] = data["is_current_user"]
            e["isFollowing"] = False
            # 遍历 i 的粉丝, 查询当前登录用户是否关注了 i 
            for j in crud.get_followers(db=db, stu_id=i.follower):
                if current_user.stu_id == j.follower:
                    e["isFollowing"] = True
                    break
            # 如果 is_current_user 为假, 再去查询 i 的关注列表
            if not data["is_current_user"]:
                for j in crud.get_followings(db=db, stu_id=i.follower):
                    if current_user.stu_id == j.followed:
                        e["isFollowed"] = True
                        break
            data['followers'].append(e)

    return {
        "code": code,
        "data": data
    }

def followings_handler(stuid: str, db: Session, current_user: models.User):
    code = 0
    data = {}

    # 判断查看的是否是自己的粉丝列表
    # 当以下 2 项均为 False , 不可查看粉丝列表
    data['is_current_user'] = True
    data["get_others_followings"] = False
    if stuid != current_user.stu_id:
        data['is_current_user'] = False
        other_user = crud.get_user(db=db, stu_id=stuid)
        data['get_others_followings'] = bool(other_user.following_perm)
    if not data["is_current_user"] and not data['get_others_followings']:
        code = 2
        msg = {"由于对方的隐私设置, 你不能查看ta的关注列表"}
        return {
            "code": code,
            "msg": msg
        }

    # isFollowed  表示这个用户是否关注了当前登录用户
    # isFollowing 表示当前登录用户是否关注了这个用户
    # 当 is_current_user 为真时, isFollowing 为真
    data['followings'] = []
    followings_list = crud.get_followings(db=db, stu_id=stuid)
    if followings_list:
        # 用 i 遍历关注列表
        for i in followings_list:
            if data['is_current_user'] and i.followed == current_user.stu_id:
                continue
            if not data['is_current_user'] and i.followed == stuid:
                continue
            e = {}
            e['userId'] = i.followed
            e['isFollowed'] = False
            e["isFollowing"] = data["is_current_user"]
            # 遍历 i 的关注列表, 查询 i 是否关注了当前登录用户
            for j in crud.get_followings(db=db, stu_id=i.followed):
                if current_user.stu_id == j.followed:
                    e["isFollowed"] = True
                    break
            # 如果 is_current_user 为假, 再去查询 i 的粉丝列表
            if not data["is_current_user"]:
                for j in crud.get_followers(db=db, stu_id=i.followed):
                    if current_user.stu_id == j.follower:
                        e["isFollowing"] = True
                        break
            data['followings'].append(e)

    return {
        "code": code,
        "data": data
    }

def getUserInfo_handler(stuid: str, db: Session, current_user: models.User):
    code = 1
    data = {}

    # 取要查看的人的资料
    db_user = crud.get_user(db=db, stu_id=stuid)
    db_user_add_info = crud.get_user_add_info(db=db, stu_id=stuid)

    if not db_user or not db_user_add_info:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="对应的用户不存在",
            headers={}
        )

    # 判断是否为当前用户
    data["is_current_user"] = True
    if stuid != current_user.stu_id:
        data["is_current_user"] = False

    code = 0
    data['userId'] = { 
        "info": db_user.stu_id if data["is_current_user"] or 
                                bool(db_user.stu_id_perm) else "None",
        "pms": bool(db_user.stu_id_perm) 
    }
    data['userName'] = { 
        "info": db_user.name if data["is_current_user"] or 
                                bool(db_user.name_perm) else "None",
        "pms": bool(db_user.name_perm) 
    }
    data['userNickName'] = { 
        "info": db_user.user_name if data["is_current_user"] or 
                                bool(db_user.user_name_perm) else "None",
        "pms": bool(db_user.user_name_perm) 
    }
    data['userGender'] = { 
        "info": "None" if not data["is_current_user"] and 
                not bool(db_user.sex_perm)
                else ('男' if db_user.sex == 1 else '女'), 
        "pms": bool(db_user.sex_perm) 
    }
    data['userAvatar'] = { 
        "info": db_user_add_info.avatar 
                if data["is_current_user"] or bool(db_user_add_info.avatar_perm) 
                else "None",
        "pms": bool(db_user_add_info.avatar_perm) 
    }
    data['userBirthDate'] = { 
        "info": db_user_add_info.birth_date 
                if data["is_current_user"] or bool(db_user_add_info.birth_date_perm) 
                else "None",
        "pms": bool(db_user_add_info.birth_date_perm) 
    }
    data['userStatus'] = { 
        "info": db_user_add_info.status 
                if data["is_current_user"] or bool(db_user_add_info.status_perm) 
                else "None",
        "pms": bool(db_user_add_info.status_perm) 
    }
    data['userMajor'] = { 
        "info": db_user_add_info.major 
                if data["is_current_user"] or bool(db_user_add_info.major_perm) 
                else "None",
        "pms": bool(db_user_add_info.major_perm) 
    }
    data['userYear'] = { 
        "info": int(db_user_add_info.year) 
                if data["is_current_user"] or bool(db_user_add_info.year_perm) 
                else "None",
        "pms": bool(db_user_add_info.year_perm) 
    }
    data['userInterest'] = { 
        "info": db_user_add_info.interest 
                if data["is_current_user"] or bool(db_user_add_info.interest_perm) 
                else "None",
        "pms": bool(db_user_add_info.interest_perm) 
    }
    data['userLabel'] = { 
        "info": db_user_add_info.label.split(',') 
                if data["is_current_user"] or bool(db_user_add_info.label_perm) 
                else "None",
        "pms": bool(db_user_add_info.label_perm) 
    }
    data['userPhone'] = {
        "info": db_user_add_info.phone 
                if data["is_current_user"] or bool(db_user_add_info.phone_perm) 
                else "None",
        "pms": bool(db_user_add_info.phone_perm) 
    }
    data['followerPms'] = bool(db_user.follower_perm)
    f = crud.get_followers(db=db, stu_id=stuid)
    f_follower_list = []
    for i in f:
        f_follower_list.append(i.follower)
    data['isFollowing'] = bool(current_user.stu_id in f_follower_list)
    data['followerNum'] = len(str(f).split(',')) - 1 if f else 0
    data['followingPms'] = bool(db_user.following_perm)
    f = crud.get_followings(db=db, stu_id=stuid)
    data['followingNum'] = len(str(f).split(',')) - 1 if f else 0
    

    return {
        "code": code,
        "data": data
    }

def updateUserInfo_handler(r: userIn, db: Session, current_user: models.User):
    code = 0
    msg = "修改成功"

    # 是否有修改权限
    if current_user.stu_id != r.userId.info:
        return { "code": 1, "msg": "没有修改权限", "data": {} }
    
    db_user_add_info = crud.get_user_add_info(db=db, stu_id=current_user.stu_id)
    crud.update_user(
        db=db, 
        stu_id=current_user.stu_id, 
        stu_id_perm=r.userId.pms, 
        name=current_user.name, 
        name_perm=r.userName.pms, 
        user_name=r.userNickName.info, 
        user_name_perm=r.userNickName.pms, 
        sex=current_user.sex, 
        sex_perm=r.userGender.pms, 
        faculty=current_user.faculty, 
        follower_perm=r.followerPms, 
        following_perm=r.followingPms
    )
    try:
        y = int(r.userYear.info)
    except:
        code = 2
        msg = "年份非整数"
        y = db_user_add_info.year

    db_photo = crud.get_photo_by_address(db=db, address=r.userAvatar.info)
    if not db_photo:
        db_photo = crud.create_photo(db=db, address=r.userAvatar.info)

    crud.update_user_add_info(
        db=db, 
        stu_id=current_user.stu_id, 
        birth_date=r.userBirthDate.info, 
        birth_date_perm=r.userBirthDate.pms, 
        status=r.userStatus.info, 
        status_perm=r.userStatus.pms, 
        major=r.userMajor.info, 
        major_perm=r.userMajor.pms, 
        year=y, 
        year_perm=r.userYear.pms, 
        interest=r.userInterest.info, 
        interest_perm=r.userInterest.pms, 
        label=r.userLabel.info, 
        label_perm=r.userLabel.pms, 
        avatar=r.userAvatar.info, 
        avatar_perm=True, 
        phone=r.userPhone.info, 
        phone_perm=r.userPhone.pms
    )
    return { "code": code, "msg": msg, "data": {} }

def getLabels_handler(db: Session, current_user: models.User):
    data = {}
    data['labels'] = []
    label_list = crud.get_labels(db=db)
    for i in label_list:
        data['labels'].append(i.label)
    return { "code": 0, "msg": "success", "data": data }

def getUserMemories_handler(userId: str, db: Session, current_user: models.User):
    # 检查要查找的用户是否存在
    db_user = crud.get_user(db=db, stu_id=userId)
    if not db_user:
        return { "code": 1, "msg": "用户不存在", "data": {} }
    
    data = []
    db_user_memories = crud.get_memories_by_stu_id(db=db, stu_id=userId)
    for i in db_user_memories:
        e = {}
        # 不能看的情况：
        if not canSeeThisMemory(db=db, current_user=current_user, memory=i):
            continue
        #if userId != current_user.stu_id and i.pms == 0:
        #    continue

        e['userId'] = i.stu_id
        e['postId'] = i.post_id

        try:
            e['userName'] = crud.get_user(db=db, stu_id=i.stu_id).user_name
        except:
            return { "code": 2, "msg": "动态对应用户出错", "data": data }

        db_user_add_info = crud.get_user_add_info(db=db, stu_id=i.stu_id)
        if db_user_add_info:
            try:
                e['userAvatar'] = db_user_add_info.avatar
            except:
                e['userAvatar'] = ""
        else:
            e['userAvatar'] = ""

        e['postTime'] = i.time

        if i.photo_list and i.photo_list != "":
            try:
                e['postPhoto'] = crud.get_photo(db=db, photo_id=i.photo_list.split(',')[0]).address
            except:
                return { "code": 3, "msg": "动态对应照片出错", "data": data }
        
        e['likeNum'] = int(len(i.like_list.split(','))) if (i.like_list and i.like_list != "") else 0
        e['commentNum'] = int(len(i.comment_list.split(','))) if (i.comment_list and i.comment_list != "") else 0
        e['repoNum'] = int(len(i.repo_list.split(','))) if (i.repo_list and i.repo_list != "") else 0

        try:
            e['isLiked'] = current_user.stu_id in i.like_list.split(',')
        except:
            e['isLiked'] = False

        e['isAnonymous'] = bool(i.is_anonymous)

        data.append(e)
    
    return { "code": 0, "msg": "success", "data": data }

# -- match --
def endMatch_handler(db: Session, current_user: models.User):

    db_user = crud.get_wait_by_stuid(db=db, stu_id=current_user.stu_id)
    if db_user:
        crud.delete_wait(db=db, stu_id=current_user.stu_id)
        return {"code": 0, "msg": "success", "data": {}}
    else:
        return {"code": 0, "msg": "用户不在匹配列表", "data": {}}
    
def startMatch_handler(db: Session, current_user: models.User):
    db_user = crud.get_wait_by_stuid(db=db, stu_id=current_user.stu_id)
    if not db_user:
        db_wait = crud.create_wait(db=db, stu_id=current_user.stu_id)
        return {"code": 0, "msg": "success", "data": {}}
    else:
        return {"code": 0, "msg": "用户已经在匹配中", "data": {}}
    
def queryMatch_handler(db: Session, current_user: models.User):
    data = {}
    data["match"] = ""

    waiting_list = crud.get_all_waitings(db=db)
    if len(waiting_list) >= 2:
        for i in range(len(waiting_list)):
            if waiting_list[i].stu_id == current_user.stu_id:
                if i >= 1:
                    data["match"] = waiting_list[i - 1].stu_id
                else:
                    data["match"] = waiting_list[i + 1].stu_id

    if data["match"] != "":
        crud.delete_wait(db=db, stu_id=current_user.stu_id)
        crud.delete_wait(db=db, stu_id=data["match"])

        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db_match = crud.create_match(db=db, id0=current_user.stu_id, id1=data["match"], time=t, is_end=0)
        return {"code": 0, "msg": "success", "data": data}
    else:
        return {"code": 0, "msg": "匹配失败", "data": data}
    '''
        db_match = crud.get_match_by_id1(db=db, id1=current_user.stu_id)
        if db_match:
            data["match"] = db_match.id0
            return {"code": 0, "msg": "success", "data": data}
        else:
            return {"code": 0, "msg": "匹配失败", "data": data}
    '''

def uploadSocketId_handler(r: SocketId, db: Session, current_user: models.User):
    db_socket = crud.get_socket_by_stuid(db=db, stu_id=current_user.stu_id)

    if db_socket:
        crud.update_socket(db=db, stu_id=current_user.stu_id, socket_id=r.socketId)
    else:
        crud.create_socket(db=db, stu_id=current_user.stu_id, socket_id=r.socketId)

    return {"code": 0, "msg": "success", "data": {}}

def getSocketId_handler(userId: str, db: Session, current_user: models.User):
    db_socket = crud.get_socket_by_stuid(db=db, stu_id=userId)

    data = {}
    if db_socket:
        data["socketId"] = db_socket.socket_id
        return {"code": 0, "msg": "success", "data": data}
    else:
        data["socketId"] = ""
        return {"code": 1, "msg": "不存在", "data": data}
    
# -- login --
def login_error_handler():
    code = 0
    msg = "Please use POST method to login."
    data = {}
    return {
        "code": code,
        "msg": msg,
        "data": data
    }

def login_valid_handler(form_data: OAuth2PasswordRequestForm, db: Session):
    code = 0
    msg = "登录成功"
    data = {}

    db_user = crud.get_user(db=db, stu_id=form_data.username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.stu_id}, expires_delta=access_token_expires 
    )
    data['access_token'] = access_token
    data['token_type'] = 'bearer'
    return {
        "code": code,
        "msg": msg,
        "data": data
    }