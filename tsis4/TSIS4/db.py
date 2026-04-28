# Модуль работы с базой данных PostgreSQL для игры "Змейка"
# Использует библиотеку psycopg2

import psycopg2
import psycopg2.extras
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_connection():
    """Возвращает соединение с базой данных PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"[БД] Ошибка подключения: {e}")
        return None


def create_tables():
    """Создаёт таблицы players и game_sessions, если они не существуют."""
    conn = get_connection()
    if conn is None:
        return
    try:
        with conn.cursor() as cur:
            # Таблица игроков
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id       SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                );
            """)
            # Таблица игровых сессий
            cur.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id            SERIAL PRIMARY KEY,
                    player_id     INTEGER REFERENCES players(id),
                    score         INTEGER NOT NULL,
                    level_reached INTEGER NOT NULL,
                    played_at     TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()
        print("[БД] Таблицы успешно созданы (или уже существуют).")
    except Exception as e:
        print(f"[БД] Ошибка создания таблиц: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_or_create_player(username: str) -> int:
    """
    Возвращает player_id для указанного имени пользователя.
    Если игрок не найден — создаёт новую запись.
    """
    conn = get_connection()
    if conn is None:
        return -1
    try:
        with conn.cursor() as cur:
            # Попытка найти существующего игрока
            cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
            row = cur.fetchone()
            if row:
                return row[0]
            # Создаём нового игрока
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) RETURNING id;",
                (username,)
            )
            player_id = cur.fetchone()[0]
        conn.commit()
        return player_id
    except Exception as e:
        print(f"[БД] Ошибка получения/создания игрока: {e}")
        conn.rollback()
        return -1
    finally:
        conn.close()


def save_session(player_id: int, score: int, level_reached: int):
    """Сохраняет результат игровой сессии в таблицу game_sessions."""
    if player_id == -1:
        print("[БД] Некорректный player_id, сессия не сохранена.")
        return
    conn = get_connection()
    if conn is None:
        return
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO game_sessions (player_id, score, level_reached)
                VALUES (%s, %s, %s);
                """,
                (player_id, score, level_reached)
            )
        conn.commit()
        print(f"[БД] Сессия сохранена: игрок={player_id}, очки={score}, уровень={level_reached}")
    except Exception as e:
        print(f"[БД] Ошибка сохранения сессии: {e}")
        conn.rollback()
    finally:
        conn.close()


def get_leaderboard() -> list:
    """
    Возвращает топ-10 результатов из таблицы лидеров.
    Каждый элемент списка — словарь:
      rank, username, score, level_reached, played_at
    """
    conn = get_connection()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    ROW_NUMBER() OVER (ORDER BY gs.score DESC) AS rank,
                    p.username,
                    gs.score,
                    gs.level_reached,
                    gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT 10;
            """)
            rows = cur.fetchall()
        # Преобразуем RealDictRow в обычные словари
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[БД] Ошибка получения таблицы лидеров: {e}")
        return []
    finally:
        conn.close()


def get_personal_best(player_id: int) -> int:
    """
    Возвращает лучший результат (score) для данного игрока.
    Если записей нет — возвращает 0.
    """
    if player_id == -1:
        return 0
    conn = get_connection()
    if conn is None:
        return 0
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT MAX(score) FROM game_sessions WHERE player_id = %s;",
                (player_id,)
            )
            row = cur.fetchone()
            if row and row[0] is not None:
                return int(row[0])
            return 0
    except Exception as e:
        print(f"[БД] Ошибка получения личного рекорда: {e}")
        return 0
    finally:
        conn.close()
