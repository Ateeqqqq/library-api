from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management API",
    description="A small REST API to manage a library's book collection.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {"message": "Library API is running. Visit /docs to try it."}


@app.get("/books", response_model=List[schemas.BookOut])
def get_books(available: Optional[bool] = None, db: Session = Depends(get_db)):
    query = db.query(models.Book)
    if available is not None:
        query = query.filter(models.Book.available == available)
    return query.all()


@app.get("/books/{book_id}", response_model=schemas.BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books", response_model=schemas.BookOut, status_code=201)
def add_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if existing:
        raise HTTPException(status_code=400, detail="A book with this ISBN already exists")

    new_book = models.Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        genre=book.genre,
        available=True,
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@app.put("/books/{book_id}", response_model=schemas.BookOut)
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Book).filter(models.Book.id == book_id).first()
    if existing is None:
        raise HTTPException(status_code=404, detail="Book not found")

    existing.title = book.title
    existing.author = book.author
    existing.isbn = book.isbn
    existing.genre = book.genre

    db.commit()
    db.refresh(existing)
    return existing


@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.available:
        raise HTTPException(status_code=400, detail="Cannot delete a book that is currently borrowed")

    db.delete(book)
    db.commit()
    return {"message": f"Book {book_id} deleted"}


@app.post("/books/{book_id}/borrow", response_model=schemas.BookOut)
def borrow_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.available:
        raise HTTPException(status_code=400, detail="Book is already borrowed")

    book.available = False
    db.commit()
    db.refresh(book)
    return book


@app.post("/books/{book_id}/return", response_model=schemas.BookOut)
def return_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.available:
        raise HTTPException(status_code=400, detail="Book is not currently borrowed")

    book.available = True
    db.commit()
    db.refresh(book)
    return book