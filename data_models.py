"""
Database and model definitions for Book Alchemy.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """
    Represents an author in the digital library.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    books = db.relationship("Book", backref="author", lazy=True)

    def __repr__(self):
        """
        Developer-friendly representation of an Author.
        """
        return f"<Author id={self.id} name={self.name!r}>"

    def __str__(self):
        """
        User-friendly string representation of an Author.
        """
        return self.name


class Book(db.Model):
    """
    Represents a book in the digital library.
    """
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    def __repr__(self):
        """
        Developer-friendly representation of a Book.
        """
        return f"<Book id={self.id} title={self.title!r}>"

    def __str__(self):
        """
        User-friendly string representation of a Book.
        """
        return self.title