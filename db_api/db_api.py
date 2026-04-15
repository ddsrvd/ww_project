import psycopg2
from config import db_config
from enum import Enum
import asyncio
from datetime import datetime, timedelta


class db_api:
    class FindBy(Enum):
        NAME = 'name'
        AUTHOR = 'author'
    
    @staticmethod
    async def get_song(song_id: str):
        conn = None
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            sql = "SELECT * FROM song WHERE song_id = %s"
            cursor.execute(sql, (song_id,))

            result = cursor.fetchall()
            cursor.close()
            return result[0] if result else []

        except Exception:
            return []

        finally:
            if conn:
                conn.close()

    @staticmethod
    async def get_all_song():
        conn = None
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
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
    async def song_in_db(song_name: str, author=None):
        conn = None
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            if not author:
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
                return r[0][0]

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
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            sql = "INSERT INTO song(name_song, author) VALUES(%s, %s)"
            cursor.execute(sql, (song_name, author))

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
    async def user_in_db(user_tg_id: str):
        conn = None
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

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
    async def create_user(username: str, user_tg_id=""):
        conn = None
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            sql = "INSERT INTO users(username, user_tg_id) VALUES(%s, %s)"
            cursor.execute(sql, (username, user_tg_id))

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
    def create_review(username: str, user_id: str, song_id: str, review: str):
        conn = None
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            
            sql = "INSERT INTO review(review_author, review) VALUES(%s, %s) RETURNING review_id;"
            cursor.execute(sql, (username, review))
            new_review = cursor.fetchone()
            
            if not new_review:
                return False
            review_id = new_review[0]

            # 2. Обновляем таблицу song
            sql = "SELECT review FROM song WHERE song_id = %s"
            cursor.execute(sql, (song_id,))
            song_result = cursor.fetchone()

            if not song_result:
                return False

            current_song_reviews = song_result[0]
            if current_song_reviews:
                updated_song_reviews = list(current_song_reviews)
                updated_song_reviews.append(str(review_id))
            else:
                updated_song_reviews = [str(review_id)]

            sql = "UPDATE song SET review = %s WHERE song_id = %s;"
            cursor.execute(sql, (updated_song_reviews, song_id))

            # 3. Пытаемся обновить users, но не прерываемся если не получилось
            try:
                user_id_int = int(user_id)  # Конвертируем в число
                sql = "SELECT user_review FROM users WHERE user_id = %s"
                cursor.execute(sql, (user_id_int,))
                user_result = cursor.fetchone()

                if user_result:
                    current_user_reviews = user_result[0]
                    if current_user_reviews:
                        updated_user_reviews = list(current_user_reviews)
                        updated_user_reviews.append(str(review_id))
                    else:
                        updated_user_reviews = [str(review_id)]

                    sql = "UPDATE users SET user_review = %s WHERE user_id = %s;"
                    cursor.execute(sql, (updated_user_reviews, user_id_int))
            except (ValueError, psycopg2.Error) as e:
                print(f"Warning: Could not update user reviews: {e}")
                # Если user_id не число или пользователя нет - игнорируем
                pass

            conn.commit()
            cursor.close()
            return True

        except psycopg2.Error as e:
            print(f"Database error in create_review: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    async def get_song_review(song_id: str):
        conn = None
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

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
    async def find_song(substraction, max_dist=5, number_of_results=5, type_search='name'):
        loop = asyncio.get_event_loop()

        def _sync_find_song():
            conn = None
            try:
                conn = psycopg2.connect(**db_config)
                cursor = conn.cursor()

                if type_search == 'name':
                    sql = """
                        SELECT 
                            *,
                            LEVENSHTEIN(LOWER(name_song), LOWER(%s)) as distance
                        FROM song 
                        WHERE LEVENSHTEIN(LOWER(name_song), LOWER(%s)) <= %s
                        ORDER BY distance
                        LIMIT %s
                        """

                    cursor.execute(sql, (
                    substraction, substraction, len(substraction) // 2 + len(substraction) // 5, number_of_results))
                    result = cursor.fetchall()

                elif type_search == 'author':
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

                    cursor.execute(sql, (
                    substraction, substraction, len(substraction) // 2 + len(substraction) // 5, number_of_results))
                    result = cursor.fetchall()

                cursor.close()
                return [list(row) for row in result]

            except psycopg2.Error:
                if conn:
                    conn.rollback()
                return []

            finally:
                if conn:
                    conn.close()

        return await loop.run_in_executor(None, _sync_find_song)
    
    @staticmethod
    def create_auth_code(user_tg_id: str, username: str, code: str, expires_minutes: int = 5):
        conn = None
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            
            # Используем параметризованный запрос с вычислением времени
            sql = """
            INSERT INTO auth_codes (code, user_tg_id, username, expires_at) 
            VALUES (%s, %s, %s, NOW() + INTERVAL %s)
            ON CONFLICT (code) DO UPDATE 
            SET user_tg_id = EXCLUDED.user_tg_id,
                username = EXCLUDED.username,
                expires_at = EXCLUDED.expires_at,
                used = FALSE
            """
            interval_str = f"{expires_minutes} minutes"
            cursor.execute(sql, (code, user_tg_id, username, interval_str))
            
            conn.commit()
            cursor.close()
            return True
            
        except psycopg2.Error as e:
            print(f"Database error in create_auth_code: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    #после проверки на соответствие она удаляет код
    @staticmethod
    def verify_auth_code(code: str):
        
        conn = None
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
        
            sql = """
            SELECT user_tg_id, username 
            FROM auth_codes 
            WHERE code = %s 
            AND expires_at > NOW()
            """
            cursor.execute(sql, (code,))
            result = cursor.fetchone()
        
            if result:
                user_tg_id, username = result
                # УДАЛЯЕМ код после успешной проверки
                delete_sql = "DELETE FROM auth_codes WHERE code = %s"
                cursor.execute(delete_sql, (code,))
                conn.commit()
            
                cursor.close()
                return user_tg_id, username
            else:
                cursor.close()
                return None, None
            
        except psycopg2.Error as e:
            print(f"Database error in verify_auth_code: {e}")
            if conn:
                conn.rollback()
            return None, None
        finally:
            if conn:
                conn.close()