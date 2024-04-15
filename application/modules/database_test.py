import json
from mysql.connector.errors import ProgrammingError
from mysql.connector.errors import Error
from ..config.db_2 import init_db, close_db
from flask import Blueprint, jsonify

bp = Blueprint("Database Test", __name__, url_prefix="/database")


@bp.route("/")
def test():
    conn = init_db()
    result = None

    with conn.cursor() as cursor:
        # result = cursor.execute("")
        try:
            cursor.execute("DROP TABLE IF EXISTS user;")
            cursor.execute(
                "CREATE TABLE user ("
                + "id INTEGER AUTO_INCREMENT NOT NULL,"
                + "username TEXT UNIQUE NOT NULL,"
                + "password TEXT NOT NULL,"
                + "PRIMARY KEY(id)"
                + ");"
            )
            cursor.execute(
                "CREATE TABLE post ("
                + "author_id INTEGER NOT NULL,"
                + "created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                + "title TEXT NOT NULL,"
                + "body TEXT NOT NULL,"
                + "FOREIGN KEY (author_id) REFERENCES user (id)"
                + ");"
            )

            rows = cursor.fetchall()

            for row in rows:
                result = row
                print(row)

            # Insert values
            insert_sql = (
                "INSERT INTO peoples (first_name,last_name,midle_name) "
                + "VALUES (%s, %s, %s);"
            )
            insert_values = ("Pereira", "Afonso", "Camilo")

            cursor.execute(insert_sql, insert_values)
            conn.commit()
            result = cursor.execute("SHOW TABLES;")

            c = conn.close()
            return f"Response. {result} - {c}"
        except ProgrammingError as e:
            return f"Error: {e}"
        return None


@bp.route("/all", methods=['GET'])
def getall():
    conn = init_db()
    result = None
    try:
        # cursor = conn.cursor(dictionary=True)
        # tables = cursor.execute('SHOW TABLES;')
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM peoples;")
            obj = cursor.fetchall()
            data = jsonify(obj)
            return obj
    except AttributeError as e:
        return f" Database connection failed with the error: {e}"
    finally:
        conn.close()
