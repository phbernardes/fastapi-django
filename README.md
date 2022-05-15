---
layout: django-pydantic
title: Django, Pydantic and FastAPI
tags:
  - python
  - django
  - fastapi
  - pydantic
  - djantic
date: 2022-05-01 11:03:48
---

# Django

## Advantages

Django provides a great toolbox to quickly develop a web application, as from their logo: `"The web framework for perfectionists with deadlines"`.

Django's ORM is simple, allow us to easily write clean code, is powerful to translate different types of queries without use of raw SQL and has a great migration control system.

Django's admin is great tool to manage data with minimum development effort.

## Disadvantages

Django Rest Framework (DRF) serializers are way slower than Pydantic validators/serializer. 

Django is built based in metaclasses, this results in missing type hints in several objects you manipulate.

Django ORM is not able to operate safely in an async environment. But discussions about supporting async are active and hopefully Psycopg3 implementation will enable this support. Use of [asgiref library](https://docs.djangoproject.com/en/4.0/topics/async/#async-views) solves this problem until this is implemented.


# FastAPI

FastAPI is based in Starlette and Pydantic.

Starlette is a lightweight ASGI framework, it has a [impressive performance](https://www.techempower.com/benchmarks/#section=data-r20&hw=ph&test=fortune&l=zijzen-sf), supports async and its simplicity allow us to easily write scalable web systems.

Pydantic provides data validation and serialization using python type annotations, it enforces type hints at runtime, provides user friendly errors when data is invalid, is fast (it [claims to be 12x faster than DRF](https://pydantic-docs.helpmanual.io/benchmarks/), I benchmarked it 6x faster for payloads validation and serialization).

The union of Starlette and Pydantic added to automatic OpenAPI schemas generation and swagger gives us a great toolset to quickly develop a (Fast) API. Type annotations enforcement leads to an amazing developer experience.

FastAPI is database agnostic and easily integrable with any Python ORM (here enters Django ORM in this example).

# Uniting forces

Starlette will provide a light weight ASGI framework to server our API endpoints.

Pydantic will provide a toolset to validate and serialize our payloads, while enforcing type hints in our code base.

FastAPI's OpenAPI support will provide a toolset to generate a nice API documentation.

Django will provide a powerful ORM, migration control system and the admin page to manage our data.

Djantic will be the bridge between Pydantic schemas and Django models.

# Requirements

This tutorial expects you to have some familiarity of:
- Python
- Django (part 1 and 2 of the [official tutorial](https://docs.djangoproject.com/en/4.0/intro/tutorial01/) are enough)
- FastAPI ([official first steps](https://fastapi.tiangolo.com/tutorial/first-steps/) guide are enough)

# Packages installation

Install the following dependencies. Fell free to use your favorite package/environment manager instead of pip.

```
pip install fastapi uvicorn django djantic django-extensions djangorestframework-simplejwt python-multipart
```

# Django project

Start a new Django project. We could start as well from a cookiecutter template for FastAPI and add Django models and admin endpoint.

```
django-admin startproject fastdjango .
```

Here is our directory tree:

```
├── fastdjango
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

We are able to run the Django project:

```
uvicorn fastdjango.asgi:application --reload
```

# Defining the ASGI module (Django + FastAPI)

Refactoring the ASGI module to integrate FastAPI application.

```
mkdir fastdjango/asgi; mv fastdjango/asgi.py fastdjango/asgi/django.py; touch fastdjango/asgi/__init__.py fastdjango/asgi/fastapi.py
```

Directory tree:

```
├── fastdjango
│   ├── __init__.py
│   ├── asgi
│   │   ├── __init__.py
│   │   ├── django.py
│   │   └── fastapi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

Editing the new ASGI files:

```python
# fastdjango/asgi/fastapi.py 
from fastapi import FastAPI

app = FastAPI()
```

```python
# fastdjango/asgi/__init__.py 
from fastapi.staticfiles import StaticFiles

from .django import application
from .fastapi import app

__all__ = ["app"]

app.mount("/django/static", StaticFiles(directory="static"), name="static")
app.mount("/django", application)
```

Add this to settings files:

```python
# fastdjango/settings.py
...

import os
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
```

And then run collectstatic to generate Django's static files and migrate to create our database:
```
./manage.py collectstatic; ./manage.py migrate
```

Running our application now will serve both Django and FastAPI:

```
uvicorn fastdjango.asgi:app --reload
```

FastAPI docs (no endpoint for now):
- http://127.0.0.1:8000/docs

Django Admin and Django (no endpoint neither):
- http://127.0.0.1:8000/django/admin/
- http://127.0.0.1:8000/django

# User stories

For this example we will create an API for a forum where people can create and read posts.

- As a anonymous user I want to be able to create a new User account.
- As a anonymous user I want to be able to login.
- As an authentified User I want to list all the posts.
- As an authentified User I want to post a new post.
- As an authentified User I want to list my posts.

# Models

## Users

Start the users app:

```
./manage.py startapp users
```

File tree:

```
├── fastdjango
├── manage.py
└── users
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations
    │   └── __init__.py
    ├── models.py
    ├── tests.py
    └── views.py
```

Settings:

Add users.apps.UsersConfig to INSTALLED_APPS:

```python
# fastdjango/settings.py
...
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
]
...
```

User model:

```python
# users/models.py
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pubkey = models.UUIDField(
        default=uuid.uuid4, db_index=True, editable=False, unique=True
    )

    EMAIL_FIELD = "username"
    USERNAME_FIELD = "username"

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"
```

Settings:

```python
# fastdjango/settings.py
USER_MODEL = "users.User"
AUTH_USER_MODEL = "users.User"
```

## Forum

Start the forum app:

```
./manage.py startapp forum
```

Settings:

```python
# fastdjango/settings.py
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users.apps.UsersConfig",
    "forum.apps.ForumConfig",
]
```

File tree:

```
.
├── fastdjango
├── forum
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── manage.py
└── users
```

Forum models:

```python
# forum/models.py
import uuid

from django.conf import settings
from django.db import models


class Post(models.Model):
    pubkey = models.UUIDField(
        default=uuid.uuid4, db_index=True, editable=False, unique=True
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        get_latest_by = "-created_at"
```

Migrate:

```
./manage.py makemigrations; ./manage.py migrate
```

# FastAPI endpoints

We will now create the FastAPI endpoints.

## User registration

There will be endpoints for registration and authentication:
- /register
- /login

### Schemas:

We will use Djantic to automatically generate the Pydantic schemas basing in our User model.
We will also define the JWTPairSchema to serialize the JWT in the /login endpoint. Let's keep it simple and not define the JWT refresh endpoint for now.

```python
# users/schemas.py
from djantic import ModelSchema
from pydantic import BaseModel

from users.models import User

__all__ = ["JWTPairSchema"]


class JWTPairSchema(BaseModel):
    refresh_token: str
    access_token: str
    token_type: str = "bearer"


class CreateUserSchema(ModelSchema):
    class Config:
        model = User
        include = (
            "username",
            "password",
            "first_name",
            "last_name",
        )
```

### Views:

We will use Django's authentication system and DRF Simple JWT for the authentication.

```python:

```python
# users/views.py
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
```

### ASGI:

Include the user views in the ASGI application:

```python
# fastdjango/asgi/fastapi.py
from fastapi import FastAPI

from users.views import router as users_router

app = FastAPI()

app.include_router(users_router, tags=["auth"], prefix="")
```

Now you can run the server:

```
uvicorn fastdjango.asgi:app --reload
```

And access the swagger at http://127.0.0.1:8000/docs. You can register an account and then login with the same credentials.


## User authentification

We will now create an util to authenticate the user:

```
mkdir -p utils/auth; touch utils/__init__.py utils/auth/__init__.py utils/auth/user.py
```

We will use FastAPI OAuth2 package and DRF Simple JWT for the authentication:

```python
# utils/auth/user.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import User

__all__ = ["UserAuthentified"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_authentified_user(token: str = Depends(oauth2_scheme)) -> User:
    jwt_authenticator = JWTAuthentication()
    validated_token = jwt_authenticator.get_validated_token(token)

    user = jwt_authenticator.get_user(validated_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


UserAuthentified: User = Depends(get_authentified_user)
```

```python
# utils/auth/__init__.py
from .user import UserAuthentified

__all__ = ["UserAuthentified"]
```

Now we can use UserAuthentified to ensure the user is authenticated and get the user instance in our views.

## Pagination

We will also define the pagination util using Django paginator so we can limit the number of items in the response.

```
mkdir -p utils/page; touch utils/page/__init__.py utils/page/paginator.py utils/page/schemas.py
```

```python
# utils/page/schemas.py
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, conint
from pydantic.generics import GenericModel

from django.conf import settings


class Link(BaseModel):
    first: conint(ge=1)
    last: conint(ge=1)
    current: conint(ge=1)
    next: conint(ge=1) | None
    prev: conint(ge=1) | None


DataT = TypeVar("DataT")


class PageResponse(GenericModel, Generic[DataT]):
    data: Optional[list[DataT]]
    pages: Link


class PageRequest(BaseModel):
    page: conint(ge=1) = 1
    size: conint(ge=1, le=settings.PAGINATION["max_size"]) = settings.PAGINATION[
        "default_size"
    ]
```

```python
# utils/page/paginator.py
from typing import Any

from django.core.paginator import EmptyPage, Paginator
from django.db.models import QuerySet

from .schemas import Link, PageRequest, PageResponse


def next_page_number(page):
    try:
        return page.next_page_number()
    except EmptyPage:
        return None


def previous_page_number(page):
    try:
        return page.previous_page_number()
    except EmptyPage:
        return None


def paginate(page_request: PageRequest, data: QuerySet | list) -> dict[str, Any]:
    paginator = Paginator(data, page_request.size)
    page = paginator.get_page(page_request.page)

    return PageResponse(
        data=list(page.object_list),
        pages=Link(
            current=page.number,
            first=1,
            last=paginator.num_pages,
            next=next_page_number(page),
            prev=previous_page_number(page),
        ),
    )
```

```python
# utils/page/__init__.py
from .paginator import paginate
from .schemas import PageRequest, PageResponse

__all__ = ["paginate", "PageRequest", "PageResponse"]
```

## Forum

### Schemas:

```python
# forum/schemas.py
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
```

### Views:

```python
# forum/views.py
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
```

### ASGI:

Add forum router to FastAPI ASGI:

```python
# fastdjango/asgi/fastapi.py
from fastapi import FastAPI

from forum.views import router as forum_router
from users.views import router as users_router

app = FastAPI()

app.include_router(users_router, tags=["auth"], prefix="")
app.include_router(forum_router, tags=["forum"], prefix="/forum")
```


## Django Admin

We can register our models to Django's admin:

```python
# users/admin.py
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
```


```python
# forum/admin.py
from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass
```

Now you can go to http://127.0.0.1:8000/django/admin to manage users and forum posts.


# Conclusion

The objective of this tutorial is to show you how to use FastAPI with Django. FastAPI provides better performance than Django REST Framework, enforces type hints in the code and has minimal boilerplate code. Django ORM is a great choice for abstracting database operations and managing database migrations.

## Async

We didn't cover the use of async in this tutorial, Django ORM doesn't safely support async yet. But we can [use the asgiref library](https://docs.djangoproject.com/en/4.0/topics/async/#async-views) to await Django DB transactions until support for async is released. FastAPI is fully compatible with async views.

## Out of the shell solutions

Instead of combining FastAPI and Django in a project like in this example, there are other options like [Django Ninja](https://github.com/vitalik/django-ninja) that has almost 3k stars in Github (as of May 2022). But I recomend directly using FastAPI because most of the [code for the ASGI framework of Django Ninja](https://github.com/vitalik/django-ninja/blob/master/ninja/main.py) is an adaptation of [FastAPI's code](https://github.com/tiangolo/fastapi/blob/master/fastapi/applications.py). FastAPI is wider adapted and will probably provide more comunity support and maintenability.

## Source code

You can find the source code of this project at:
https://github.com/phbernardes/fastapi-django
