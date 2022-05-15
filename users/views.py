from django.contrib.auth import authenticate
from django.db import IntegrityError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .schemas import CreateUserSchema, JWTPairSchema

router = APIRouter()


def get_jwt(user: User) -> JWTPairSchema:
    refresh = RefreshToken.for_user(user)
    return JWTPairSchema(
        refresh_token=str(refresh),
        access_token=str(refresh.access_token),
    )


@router.post("/register", response_model=JWTPairSchema)
def register_user(new_user: CreateUserSchema):
    try:
        user = User.objects.create_user(**new_user.dict())
        return get_jwt(user)
    except IntegrityError:
        raise HTTPException(detail="Cannot create user.", status_code=400)


@router.post("/login", response_model=JWTPairSchema)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(username=form_data.username, password=form_data.password)
    if user is not None:
        return get_jwt(user)
    raise HTTPException(status_code=400, detail="Incorrect username or password.")
