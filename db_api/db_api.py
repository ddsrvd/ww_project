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
    def song_in_db(song_name: str, author=None):
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

            if not author:
                # Ищем песни, где автор НЕ указан (NULL или пустая строка)
                sql = """
                SELECT song_id FROM song 
                WHERE name_song = %s 
                AND (author IS NULL OR author = '')
                """
                cursor.execute(sql, (song_name,))
            else:
                sql = "SELECT song_id FROM song WHERE name_song = %s AND author = %s"
                cursor.execute(sql, (song_name, author))

            r = cursor.fetchall()
            cursor.close()

            if not r:
                return False
            else:
                return r[0]['song_id']

        except psycopg2.Error as e:
            print(f"Database error: {e}")
            if conn:
                conn.rollback()
            return False

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
    def user_in_db(user_tg_id: str):
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


            sql = "SELECT user_id, username FROM users WHERE user_tg_id = %s"
            cursor.execute(sql, (user_tg_id,))

            r = cursor.fetchall()
            cursor.close()

            if not r:
                return False
            else:
                return r[0]

        except psycopg2.Error as e:
            print(f"Database error: {e}")
            if conn:
                conn.rollback()
            return False

        finally:
            if conn:
                conn.close()


    @staticmethod
    def create_user(username: str, user_tg_id=""):
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

            sql = "INSERT INTO users(username, user_tg_id) VALUES(%s, %s)"
            cursor.execute(sql, (username, user_tg_id))

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
    def create_review(username: str, user_id: str,  song_id: str, review: str):
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

            sql = "INSERT INTO review(review_author, review) VALUES(%s, %s) RETURNING review_id;"
            cursor.execute(sql, (username, review))

            new_review = cursor.fetchone()
            if not new_review:
                return False
            review_id = new_review['review_id'] if new_review else None

            #Обновляем таблицу song
            sql = "SELECT review FROM song WHERE song_id = %s"
            cursor.execute(sql, (song_id,))
            song_result = cursor.fetchone()

            if not song_result:
                return False

            current_song_reviews = song_result['review']

            if current_song_reviews:
                updated_song_reviews = list(current_song_reviews)
                updated_song_reviews.append(str(review_id))
            else:
                updated_song_reviews = [str(review_id)]

            sql = "UPDATE song SET review = %s WHERE song_id = %s;"
            cursor.execute(sql, (updated_song_reviews, song_id))

            # Обновляем таблицу users
            sql = "SELECT user_review FROM users WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            user_result = cursor.fetchone()

            if not user_result:
                return False

            current_user_reviews = user_result['user_review']

            if current_user_reviews:
                updated_user_reviews = list(current_user_reviews)
                updated_user_reviews.append(str(review_id))
            else:
                updated_user_reviews = [str(review_id)]

            sql = "UPDATE users SET user_review = %s WHERE user_id = %s;"
            cursor.execute(sql, (updated_user_reviews, user_id))

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
    def get_song_review(song_id: str):
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

            sql = '''
            SELECT r.review_id, r.review_author, r.review FROM song s
            JOIN review r ON r.review_id::TEXT = ANY(s.review)
            WHERE s.song_id = %s;
            '''
            cursor.execute(sql, (song_id,))

            result = cursor.fetchall()
            cursor.close()
            return result

        except Exception:
            return []

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

                cursor.execute(sql, (substraction, substraction, len(substraction) // 2 + len(substraction) // 5, number_of_results))
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

                cursor.execute(sql, (substraction, substraction, len(substraction) // 2 + len(substraction) // 5, number_of_results))
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
