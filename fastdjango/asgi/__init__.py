from fastapi.staticfiles import StaticFiles

from .django import application
from .fastapi import app

__all__ = ["app"]

app.mount("/django/static", StaticFiles(directory="static"), name="static")
app.mount("/django", application)
