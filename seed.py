from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

sample_books = [
    models.Book(title="Clean Code", author="Robert C. Martin", isbn="9780132350884", genre="Software"),
    models.Book(title="The Pragmatic Programmer", author="Andrew Hunt", isbn="9780201616224", genre="Software"),
    models.Book(title="Fluent Python", author="Luciano Ramalho", isbn="9781491946008", genre="Software"),
    models.Book(title="Sapiens", author="Yuval Noah Harari", isbn="9780062316097", genre="History"),
    models.Book(title="Dune", author="Frank Herbert", isbn="9780441013593", genre="Science Fiction"),
]

db = SessionLocal()
db.add_all(sample_books)
db.commit()
db.close()

print("Sample books added.")