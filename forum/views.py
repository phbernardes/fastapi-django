from fastapi import APIRouter
from fastapi import APIRouter, Depends


from users.models import User
from utils.auth import UserAuthentified
from utils.page import PageRequest, PageResponse, paginate

from .models import Post
from .schemas import CreatePostSchema, PostSchema

router = APIRouter()


@router.post("/posts", response_model=PostSchema)
def list_user_posts(post: CreatePostSchema, user: User = UserAuthentified):
    posts = Post.objects.create(author=user, **post.dict())
    return PostSchema.from_django(posts)


@router.get("/posts/mine", response_model=PageResponse[PostSchema])
def list_user_posts(page: PageRequest = Depends(), user: User = UserAuthentified):
    posts = Post.objects.filter(author=user)
    return paginate(page, posts)


@router.get("/posts", response_model=PageResponse[PostSchema])
def list_posts(page: PageRequest = Depends(), user: User = UserAuthentified):
    posts = Post.objects.all()
    return paginate(page, posts)
