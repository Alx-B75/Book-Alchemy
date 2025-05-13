"""
Book Alchemy application factory and database initialization.
"""

from flask import Flask, render_template, request, flash
from data_models import db, Book, Author

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../data/library.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "a-very-secret-key"

db.init_app(app)

@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
    Render a form to add a new author on GET;
    on POST, create the Author and display a success message.
    """
    if request.method == "POST":
        name = request.form.get("name")
        birth_date = request.form.get("birth_date") or None
        date_of_death = request.form.get("date_of_death") or None

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death,
        )
        db.session.add(new_author)
        db.session.commit()
        flash("Author added successfully.")

    return render_template("add_author.html")

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """
    Render a form to add a new book on GET;
    on POST, create the Book and display a success message.
    """
    authors = Author.query.order_by(Author.name).all()
    if request.method == "POST":
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        publication_year = request.form.get("publication_year") or None
        author_id = request.form.get("author_id")
        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id
        )
        db.session.add(new_book)
        db.session.commit()
        flash("Book added successfully.")
    return render_template("add_book.html", authors=authors)

