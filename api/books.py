from flask import request, jsonify
from database import get_db
import sqlite3
import nanoid


def get_all_books():
    try:
        db = get_db()
        c = db.cursor()
        c.execute(
            """
            SELECT b.title AS title, b._id AS _id, count(c.text) AS commentcount
            FROM book AS b LEFT JOIN comment AS c ON b._id = c.book_id
            GROUP BY title, _id
            ORDER BY title
            """
        )

        return jsonify(c.fetchall())

    except:
        return "Database error"


def add_new_book():
    title = request.form.get("title")
    if not title:
        return "No title given"
    book_id = nanoid.generate()

    try:
        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO book(title, _id) VALUES(?, ?)", (title, book_id))
        db.commit()

        return {"title": title, "_id": book_id}

    except:
        return "Database error"


def delete_all_books():
    try:
        db = get_db()
        c = db.cursor()
        c.execute("DELETE FROM book")
        db.commit()
        return "Delete successful"
    except:
        return "Database error"


def get_one_book(book_id):
    try:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT title, _id FROM book WHERE _id == ?", (book_id,))
        book = c.fetchone()
        if book is None:
            return "No book exists"

        c.execute("SELECT text FROM comment WHERE book_id == ?", (book_id,))
        book["comments"] = []
        for row in c.fetchall():
            book["comments"].append(row["text"])

        return book

    except:
        return "Database error"


def add_comment(book_id):
    comment = request.form.get("comment")
    if not comment:
        return "No comment provided"

    try:
        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO comment(book_id, text) VALUES(?, ?)", (book_id, comment))
        db.commit()

        return get_one_book(book_id)

    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY constraint failed" in e.args[0]:
            return "No book exists"

    except:
        return "Database error"


def delete_one_book(book_id):
    try:
        db = get_db()
        c = db.cursor()
        c.execute("DELETE FROM book WHERE _id == ?", (book_id,))
        db.commit()

        c.execute("SELECT changes() AS rows_deleted")
        if c.fetchone()["rows_deleted"] > 0:
            return "Delete successful"
        else:
            return "No book exists"

    except:
        return "Database error"
