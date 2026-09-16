import sqlite3
import os


DATABASE_FILE = os.path.join(
    "data",
    "university.db"
)


def get_connection():

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.row_factory = sqlite3.Row

    return connection


def create_database():

    os.makedirs(
        "data",
        exist_ok=True
    )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            unit_type TEXT,

            unit TEXT,

            department TEXT,

            post_title TEXT,

            person_name TEXT,

            status TEXT

        )
    """)

    connection.commit()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            unit_type TEXT,

            unit TEXT,

            department TEXT,

            post_title TEXT,

            person_name TEXT,

            status TEXT

        )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        full_name TEXT,

        position TEXT,

        role TEXT DEFAULT 'user'

    )
""")

    connection.commit()
    connection.close()