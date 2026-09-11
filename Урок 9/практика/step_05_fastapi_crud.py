"""Крок 5: той самий CRUD, але через HTTP — FastAPI з уроку 7 + SQLAlchemy.

Три шари, які не змішуємо:
    Pydantic-схеми  — що приходить і що віддаємо назовні (контракт API);
    моделі SQLAlchemy — як лежить у базі;
    обробники       — беруть сесію через Depends і з'єднують перше з другим.

Запуск (після step_02, порт 8000 на цій машині зайнятий):
    uvicorn step_05_fastapi_crud:app --reload --port 8011
    відкрити http://127.0.0.1:8011/docs
"""

from decimal import Decimal
from typing import Annotated, Iterator

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from db import SessionLocal
from models import Author, Book

app = FastAPI(title="Книгарня на SQLAlchemy")


def get_session() -> Iterator[Session]:
    """Одна сесія на один запит: відкрили, віддали обробнику, закрили."""
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class BookIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(ge=0, default=0)
    author_id: int


class BookPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    price: Decimal
    stock: int
    author: AuthorOut


def get_book_or_404(session: Session, book_id: int) -> Book:
    """Спільний шматок для GET/PATCH/DELETE одного запису."""
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Книги немає")
    return book


@app.get("/books", response_model=list[BookOut])
def list_books(session: SessionDep, limit: int = 20) -> list[Book]:
    statement = (
        select(Book).options(selectinload(Book.author))
        .order_by(Book.id).limit(limit)
    )
    return list(session.scalars(statement))


@app.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int, session: SessionDep) -> Book:
    return get_book_or_404(session, book_id)


@app.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(data: BookIn, session: SessionDep) -> Book:
    if session.get(Author, data.author_id) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT,
                            "Такого автора немає")
    book = Book(**data.model_dump())
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@app.patch("/books/{book_id}", response_model=BookOut)
def patch_book(book_id: int, data: BookPatch, session: SessionDep) -> Book:
    book = get_book_or_404(session, book_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)
    session.commit()
    session.refresh(book)
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, session: SessionDep) -> None:
    book = get_book_or_404(session, book_id)
    session.delete(book)
    session.commit()
