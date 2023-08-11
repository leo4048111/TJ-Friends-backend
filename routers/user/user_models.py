from pydantic import BaseModel

class registerIn(BaseModel):
    username: str
    id: str
    password: str
    sessionid: str

class updatePwdIn(BaseModel):
    id: str
    password: str
    sessionid: str


class itemStr(BaseModel):
    info: str
    pms: bool

class itemList(BaseModel):
    info: list
    pms: bool

class itemInt(BaseModel):
    info: int
    pms: bool

class userIn(BaseModel):
    userId: itemStr
    userName: itemStr
    userNickName: itemStr
    userGender: itemStr
    userBirthDate: itemStr
    userStatus: itemStr
    userMajor: itemStr
    userPhone: itemStr
    userYear: itemStr
    userInterest: itemStr
    userLabel: itemList
    userAvatar: itemStr
    followerPms: bool
    followingPms: bool

class SocketId(BaseModel):
    socketId: str