from djantic import ModelSchema

from .models import Post

__all__ = ["CreatePostSchema", "PostSchema"]


class PostSchema(ModelSchema):
    class Config:
        model = Post
        exclude = ("id",)


class CreatePostSchema(ModelSchema):
    class Config:
        model = Post
        include = (
            "title",
            "content",
        )
