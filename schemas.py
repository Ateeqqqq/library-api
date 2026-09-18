from typing import Optional
from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    genre: Optional[str] = "General"


class BookCreate(BookBase):
    pass


class BookOut(BookBase):
    id: int
    available: bool

    class Config:
        from_attributes = True