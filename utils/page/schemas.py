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
