import sqlite3


def create_user_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute(
        """
    CREATE TABLE IF NOT EXISTS users(
        username TEXT,
        password TEXT
    )
    """
    )

    conn.commit()
    conn.close()
