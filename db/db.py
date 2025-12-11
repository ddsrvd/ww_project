import psycopg2
from psycopg2.extras import DictCursor
from config import db_config
from enum import Enum


class db_api:
    class FindBy(Enum):
        NAME = 'name'
        AUTHOR = 'author'
    @staticmethod
    def get_song(song_id: str):
        conn = None
        try:
            conn = psycopg2.connect(
                host=db_config["host"],
                user=db_config["user"],
                password=db_config["password"],
                port=db_config["port"],
                dbname=db_config["dbname"]
            )

            cursor = conn.cursor(cursor_factory=DictCursor)

            sql = "SELECT * FROM song WHERE song_id = %s"
            cursor.execute(sql, (song_id,))

            result = cursor.fetchall()
            cursor.close()
            return result[0]

        except Exception:
            return []

        finally:
            if conn:
                conn.close()


    @staticmethod
    def get_all_song():
        conn = None
        try:
            conn = psycopg2.connect(
                host=db_config["host"],
                user=db_config["user"],
                password=db_config["password"],
                port=db_config["port"],
                dbname=db_config["dbname"]
            )

            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.execute("SELECT * FROM song")

            result = cursor.fetchall()
            cursor.close()
            return result

        except Exception:
            return []

        finally:
            if conn:
                conn.close()

    @staticmethod
    def create_song(song_name: str, author=None):
        conn = None
        try:
            conn = psycopg2.connect(
                host=db_config["host"],
                user=db_config["user"],
                password=db_config["password"],
                port=db_config["port"],
                dbname=db_config["dbname"]
            )

            cursor = conn.cursor(cursor_factory=DictCursor)

            sql = "INSERT INTO song(name_song, author) VALUES(%s, %s)"
            cursor.execute(sql, (song_name, author))

            conn.commit()
            cursor.close()
            return True

        except psycopg2.Error:
            if conn:
                conn.rollback()  # Откатываем транзакцию при ошибке
            return False

        finally:
            if conn:
                conn.close()


    @staticmethod
    def create_review(song_id: str, new_review: str):
        conn = None
        try:
            conn = psycopg2.connect(
                host=db_config["host"],
                user=db_config["user"],
                password=db_config["password"],
                port=db_config["port"],
                dbname=db_config["dbname"]
            )

            cursor = conn.cursor(cursor_factory=DictCursor)
            sql = "SELECT review FROM song WHERE song_id = %s"
            cursor.execute(sql, (song_id,))
            r = cursor.fetchall()

            if not r:
                return False

            if r[0]['review']:
                r[0]['review'].append(new_review)
                result = r[0]['review']
            else:
                result = [new_review]

            sql = "UPDATE song SET review = %s WHERE song_id = %s;"
            cursor.execute(sql, (result, song_id))

            conn.commit()
            cursor.close()
            return True

        except psycopg2.Error:
            if conn:
                conn.rollback()
            return False

        finally:
            if conn:
                conn.close()

    @staticmethod
    def find_song(substraction, max_dist=5, number_of_results=5, type_search=FindBy.NAME):
        conn = None
        try:
            conn = psycopg2.connect(
                host=db_config["host"],
                user=db_config["user"],
                password=db_config["password"],
                port=db_config["port"],
                dbname=db_config["dbname"]
            )

            cursor = conn.cursor(cursor_factory=DictCursor)

            if type_search == db_api.FindBy.NAME:
                sql = """
                    SELECT 
                        *,
                        LEVENSHTEIN(LOWER(name_song), LOWER(%s)) as distance
                    FROM song 
                    WHERE LEVENSHTEIN(LOWER(name_song), LOWER(%s)) <= %s
                    ORDER BY distance
                    LIMIT %s
                    """

                cursor.execute(sql, (substraction, substraction, max(max_dist, len(substraction)//2), number_of_results))
                result = cursor.fetchall()

            elif type_search == db_api.FindBy.AUTHOR:
                sql = """
                                    SELECT 
                                        *,
                                        LEVENSHTEIN(LOWER(author), LOWER(%s)) as distance
                                    FROM song 
                                    WHERE LEVENSHTEIN(LOWER(author), LOWER(%s)) <= %s
                                    AND author IS NOT NULL
                                    ORDER BY distance
                                    LIMIT %s
                                    """

                cursor.execute(sql, (substraction, substraction, max(max_dist, len(substraction) // 2), number_of_results))
                result = cursor.fetchall()

            cursor.close()
            return result

        except psycopg2.Error:
            if conn:
                conn.rollback()
            return []

        finally:
            if conn:
                conn.close()
