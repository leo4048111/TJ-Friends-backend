from fastapi import APIRouter, Depends
from database import models
from dependencies import IMAGE_DIR, get_current_user

from routers.social.social_models import ImageRequest
from routers.social.social_handler import upload_file_handler, show_image_handler

router = APIRouter()

# 定义一个上传文件的接口，返回一个链接
@router.post("/uploadImage")
async def upload_file(r: ImageRequest, current_user: models.User = Depends(get_current_user)):
    return upload_file_handler(r=r, current_user=current_user)

# 定义一个显示图片的接口，根据文件名返回图片内容
@router.get("/images/{filename}")
async def show_image(filename: str):
    return show_image_handler(filename=filename)