"""
Fetch and seed Audible library entries into the Book Alchemy database.
"""

import getpass
from audible import Authenticator, Client as AudibleClient
from app import app
from data_models import db, Author, Book


def login_client():
    """
    Prompt for Audible credentials (including CVF if required) and return an authenticated client.
    """
    username = input("Audible username: ")
    password = getpass.getpass("Audible password: ")
    locale = input("Locale (e.g. US): ") or "US"
    try:
        # Try login without CVF code
        auth = Authenticator.from_login(username, password, locale)
    except TypeError:
        # If CVF code is required, prompt and retry
        cvf_code = getpass.getpass("Audible CVF code (check your email/SMS): ")
        auth = Authenticator.from_login(username, password, locale, cvf_code)
    return AudibleClient(auth=auth)


def seed_audible_library(client):
    """
    Retrieve the user's Audible library and insert entries into the database.
    """
    entries = client.get("library")["entries"]
    for entry in entries:
        raw_authors = entry.get("authors", [])
        author_name = raw_authors[0] if raw_authors else "Unknown"
        author = Author.query.filter_by(name=author_name).first()
        if author is None:
            author = Author(name=author_name)
            db.session.add(author)
            db.session.commit()

        isbn = entry.get("isbn") or entry.get("asin")
        pub_year = None
        publish_date = entry.get("publish_date")
        if publish_date:
            pub_year = int(publish_date.split("-")[0])

        book = Book(
            isbn=isbn,
            title=entry.get("title"),
            publication_year=pub_year,
            author_id=author.id,
        )
        db.session.add(book)

    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        client = login_client()
        seed_audible_library(client)
