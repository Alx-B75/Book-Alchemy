"""
Book Alchemy application factory and database initialization.
"""

from flask import Flask, render_template, request, flash, redirect, url_for
from sqlalchemy import delete
from sqlalchemy.pool import NullPool
from data_models import db, Book, Author
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../data/library.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "a-very-secret-key"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {"timeout": 30},
    "poolclass": NullPool,
}

db.init_app(app)

@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """
    Render a form to add a new author on GET;
    on POST, parse submitted dates, create the Author,
    and display a success message.
    """
    if request.method == "POST":
        name = request.form["name"]
        bd_str = request.form.get("birth_date")
        dod_str = request.form.get("date_of_death")

        birth_date = (
            datetime.strptime(bd_str, "%Y-%m-%d").date() if bd_str else None
        )
        date_of_death = (
            datetime.strptime(dod_str, "%Y-%m-%d").date() if dod_str else None
        )

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death,
        )
        db.session.add(new_author)
        db.session.commit()

        flash(f'Author "{new_author.name}" added successfully.')
        return redirect(url_for("home"))

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

@app.route("/", methods=["GET"])
def home():
    """
    Display the library home page, supporting optional sorting by title,
    author, or publication year, and keyword filtering via the 'q' parameter.
    """
    sort_key = request.args.get("sort", "title")
    q = request.args.get("q", "").strip()
    order_map = {
        "title": Book.title,
        "author": Author.name,
        "year": Book.publication_year,
    }
    order_column = order_map.get(sort_key, Book.title)
    query = Book.query.join(Author).order_by(order_column)
    if q:
        ilike_pattern = f"%{q}%"
        query = query.filter(
            Book.title.ilike(ilike_pattern) |
            Author.name.ilike(ilike_pattern)
        )
    books = query.all()
    return render_template("home.html", books=books, sort_key=sort_key)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    """
    Delete the specified book; if its author has no other books,
    also delete that author. Redirect to home with a flash message.
    """
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    # If author has no more books, delete them too
    if not Book.query.filter_by(author_id=author.id).first():
        db.session.delete(author)
        db.session.commit()
        flash(f'Book "{book.title}" and its author "{author.name}" deleted.')
    else:
        flash(f'Book "{book.title}" deleted.')

    return redirect(url_for("home"))

@app.route("/authors", methods=["GET"])
def list_authors():
    """
    Render a page listing all authors in the library.
    """
    authors = Author.query.order_by(Author.name).all()
    return render_template("authors.html", authors=authors)

@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    Book.query.filter_by(author_id=author.id).delete()
    db.session.delete(author)
    db.session.commit()
    flash(f'Author "{author.name}" and all their books have been deleted.')
    return redirect(url_for("list_authors"))




@app.teardown_appcontext
def shutdown_session(exception=None):
    """
    Remove the SQLAlchemy session at the end of each request or app context,
    so that connections are closed and returned to the pool immediately.
    """
    db.session.remove()

if __name__ == "__main__":
    # Run a single‐process development server (no extra reloader)
    app.run(debug=False, use_reloader=False, threaded=False)