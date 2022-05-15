from fastapi import FastAPI

from forum.views import router as forum_router
from users.views import router as users_router

app = FastAPI()

app.include_router(users_router, tags=["auth"], prefix="")
app.include_router(forum_router, tags=["forum"], prefix="/forum")
