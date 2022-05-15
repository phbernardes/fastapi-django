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
