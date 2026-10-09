# YuiFlix V11 - Database layer

from common import *
import sqlite3

class Database:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

        self.create_tables()
        self.migrate()
        self.seed_movies()
        self.create_default_users()

    # ----------------------------------------------------------

    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    # ----------------------------------------------------------

    def fetchone(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)

        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    # ----------------------------------------------------------

    def fetchall(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    # ----------------------------------------------------------

    def table_columns(self, table):
        rows = self.fetchall(f"PRAGMA table_info({table})")
        return [row["name"] for row in rows]

    # ----------------------------------------------------------

    def ensure_column(self, table, column, definition):
        columns = self.table_columns(table)

        if column not in columns:
            self.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
            )

    # ----------------------------------------------------------

    def create_tables(self):

        self.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                avatar TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                genre TEXT,
                year INTEGER,
                rating REAL DEFAULT 0,
                description TEXT,
                poster TEXT,
                video TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                user_id INTEGER,
                movie_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS watch_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                user_id INTEGER,
                movie_id INTEGER,
                progress REAL DEFAULT 0,
                duration REAL DEFAULT 0,
                watched_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                user_id INTEGER,
                movie_id INTEGER,
                rating REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                user_id INTEGER,
                movie_id INTEGER,
                value INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS movie_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER,
                user_id INTEGER,
                movie_id INTEGER,
                viewed_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

    # ----------------------------------------------------------

    def migrate(self):

        self.ensure_column(
            "users",
            "is_admin",
            "INTEGER DEFAULT 0"
        )

        self.ensure_column(
            "users",
            "created_at",
            "TEXT"
        )

        self.ensure_column(
            "profiles",
            "avatar",
            "TEXT"
        )

        self.ensure_column(
            "profiles",
            "created_at",
            "TEXT"
        )

        self.ensure_column(
            "movies",
            "created_at",
            "TEXT"
        )

        for table in [
            "watchlist",
            "watch_history",
            "ratings",
            "likes",
            "movie_views",
        ]:
            self.ensure_column(
                table,
                "profile_id",
                "INTEGER"
            )

            self.ensure_column(
                table,
                "user_id",
                "INTEGER"
            )

        self.ensure_column(
            "watch_history",
            "progress",
            "REAL DEFAULT 0"
        )

        self.ensure_column(
            "watch_history",
            "duration",
            "REAL DEFAULT 0"
        )

        self.ensure_column(
            "watch_history",
            "watched_at",
            "TEXT"
        )

        self.ensure_column(
            "ratings",
            "rating",
            "REAL DEFAULT 0"
        )

        self.ensure_column(
            "likes",
            "value",
            "INTEGER DEFAULT 0"
        )

        self.fix_dates()

        self.migrate_old_profiles()

        self.create_indexes()

    # ----------------------------------------------------------

    def fix_dates(self):

        for table in [
            "users",
            "profiles",
            "movies",
            "watchlist",
            "watch_history",
            "ratings",
            "likes",
            "movie_views",
        ]:

            columns = self.table_columns(table)

            date_column = None

            if "created_at" in columns:
                date_column = "created_at"
            elif "watched_at" in columns:
                date_column = "watched_at"
            elif "viewed_at" in columns:
                date_column = "viewed_at"

            if date_column:
                self.execute(
                    f"""
                    UPDATE {table}
                    SET {date_column}=?
                    WHERE {date_column} IS NULL
                    """,
                    (now(),)
                )

    # ----------------------------------------------------------

    def create_indexes(self):

        try:
            self.execute("""
                CREATE INDEX IF NOT EXISTS idx_profiles_user
                ON profiles(user_id)
            """)

            self.execute("""
                CREATE INDEX IF NOT EXISTS idx_watchlist_profile_movie
                ON watchlist(profile_id,movie_id)
            """)

            self.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_profile_movie
                ON watch_history(profile_id,movie_id)
            """)

            self.execute("""
                CREATE INDEX IF NOT EXISTS idx_ratings_profile_movie
                ON ratings(profile_id,movie_id)
            """)

            self.execute("""
                CREATE INDEX IF NOT EXISTS idx_likes_profile_movie
                ON likes(profile_id,movie_id)
            """)

            self.execute("""
                CREATE INDEX IF NOT EXISTS idx_views_movie
                ON movie_views(movie_id)
            """)

        except Exception:
            pass

    # ----------------------------------------------------------

    def migrate_old_profiles(self):

        users = self.fetchall(
            "SELECT id FROM users"
        )

        for user in users:

            profile = self.fetchone(
                """
                SELECT id
                FROM profiles
                WHERE user_id=?
                ORDER BY id
                LIMIT 1
                """,
                (user["id"],)
            )

            if not profile:
                cursor = self.execute(
                    """
                    INSERT INTO profiles
                    (user_id,name,avatar,created_at)
                    VALUES (?,?,?,?,?)
                    """,
                    (
                        user["id"],
                        "Main Profile",
                        "",
                        now(),
                    )
                )

                profile_id = cursor.lastrowid

            else:
                profile_id = profile["id"]

            for table in [
                "watchlist",
                "watch_history",
                "ratings",
                "likes",
                "movie_views",
            ]:

                try:
                    self.execute(
                        f"""
                        UPDATE {table}
                        SET profile_id=?
                        WHERE user_id=?
                        AND profile_id IS NULL
                        """,
                        (
                            profile_id,
                            user["id"],
                        )
                    )
                except Exception:
                    pass

    # ----------------------------------------------------------

    def create_default_users(self):

        demo = self.fetchone(
            "SELECT id FROM users WHERE username=?",
            ("demo",)
        )

        if not demo:

            cursor = self.execute(
                """
                INSERT INTO users
                (username,password,is_admin,created_at)
                VALUES (?,?,?,?)
                """,
                (
                    "demo",
                    hash_password("demo123"),
                    0,
                    now(),
                )
            )

            self.execute(
                """
                INSERT INTO profiles
                (user_id,name,avatar,created_at)
                VALUES (?,?,?,?)
                """,
                (
                    cursor.lastrowid,
                    "Demo",
                    "",
                    now(),
                )
            )

        admin = self.fetchone(
            "SELECT id FROM users WHERE username=?",
            ("admin",)
        )

        if not admin:

            cursor = self.execute(
                """
                INSERT INTO users
                (username,password,is_admin,created_at)
                VALUES (?,?,?,?)
                """,
                (
                    "admin",
                    hash_password("admin123"),
                    1,
                    now(),
                )
            )

            self.execute(
                """
                INSERT INTO profiles
                (user_id,name,avatar,created_at)
                VALUES (?,?,?,?)
                """,
                (
                    cursor.lastrowid,
                    "Admin",
                    "",
                    now(),
                )
            )

    # ----------------------------------------------------------

    def seed_movies(self):

        count = self.fetchone(
            "SELECT COUNT(*) AS count FROM movies"
        )

        if count and count["count"] > 0:
            return

        movies = [

            (
                "The Last Survivor",
                "Horror",
                2026,
                8.7,
                "A lone survivor discovers that the abandoned city is not as empty as it seems.",
                "movie1.jpg",
                "movie1.mp4",
            ),

            (
                "Cyber Horizon",
                "Sci-Fi",
                2025,
                8.2,
                "A programmer discovers a hidden artificial intelligence controlling a futuristic city.",
                "movie2.jpg",
                "movie2.mp4",
            ),

            (
                "Midnight Chase",
                "Action",
                2026,
                8.5,
                "A mysterious package sends an ordinary courier into a dangerous midnight chase.",
                "movie3.jpg",
                "movie3.mp4",
            ),

            (
                "Lost Memories",
                "Drama",
                2024,
                7.9,
                "A young woman tries to reconstruct her forgotten past through fragments of memories.",
                "movie4.jpg",
                "movie4.mp4",
            ),

            (
                "Dark Forest",
                "Horror",
                2025,
                8.4,
                "A group of explorers enter a forest where strange events begin after sunset.",
                "movie1.jpg",
                "movie1.mp4",
            ),

            (
                "Future World",
                "Sci-Fi",
                2026,
                8.8,
                "Humanity builds a new world beyond Earth, but something unexpected arrives.",
                "movie2.jpg",
                "movie2.mp4",
            ),

            (
                "Final Mission",
                "Action",
                2025,
                8.1,
                "An elite team is given one final mission before the program is shut down.",
                "movie3.jpg",
                "movie3.mp4",
            ),

            (
                "The Unknown",
                "Mystery",
                2026,
                8.6,
                "A detective receives a message from someone who officially does not exist.",
                "movie4.jpg",
                "movie4.mp4",
            ),
        ]

        for movie in movies:

            self.execute(
                """
                INSERT INTO movies
                (
                    title,
                    genre,
                    year,
                    rating,
                    description,
                    poster,
                    video,
                    created_at
                )
                VALUES (?,?,?,?,?,?,?,?)
                """,
                movie + (now(),)
            )

    # ==========================================================
    # AUTH
    # ==========================================================

    def authenticate(self, username, password):

        return self.fetchone(
            """
            SELECT *
            FROM users
            WHERE username=?
            AND password=?
            """,
            (
                username,
                hash_password(password),
            )
        )

    # ==========================================================
    # PROFILES
    # ==========================================================

    def get_profiles(self, user_id):

        return self.fetchall(
            """
            SELECT *
            FROM profiles
            WHERE user_id=?
            ORDER BY id
            """,
            (user_id,)
        )

    def add_profile(self, user_id, name):

        cursor = self.execute(
            """
            INSERT INTO profiles
            (user_id,name,avatar,created_at)
            VALUES (?,?,?,?)
            """,
            (
                user_id,
                name,
                "",
                now(),
            )
        )

        return self.fetchone(
            """
            SELECT *
            FROM profiles
            WHERE id=?
            """,
            (cursor.lastrowid,)
        )

    def rename_profile(self, profile_id, name):

        self.execute(
            """
            UPDATE profiles
            SET name=?
            WHERE id=?
            """,
            (
                name,
                profile_id,
            )
        )

    def delete_profile(self, profile_id):

        for table in [
            "watchlist",
            "watch_history",
            "ratings",
            "likes",
            "movie_views",
        ]:

            try:
                self.execute(
                    f"""
                    DELETE FROM {table}
                    WHERE profile_id=?
                    """,
                    (profile_id,)
                )
            except Exception:
                pass

        self.execute(
            """
            DELETE FROM profiles
            WHERE id=?
            """,
            (profile_id,)
        )

    # ==========================================================
    # MOVIES
    # ==========================================================

    def get_movies(self):

        return self.fetchall(
            """
            SELECT *
            FROM movies
            ORDER BY title COLLATE NOCASE
            """
        )

    def get_movie(self, movie_id):

        return self.fetchone(
            """
            SELECT *
            FROM movies
            WHERE id=?
            """,
            (movie_id,)
        )

    def search_movies(
        self,
        search="",
        genre="All",
        year=None,
        min_rating=0,
        sort="A-Z"
    ):

        query = """
            SELECT *
            FROM movies
            WHERE 1=1
        """

        params = []

        if search.strip():

            query += """
                AND (
                    title LIKE ?
                    OR genre LIKE ?
                    OR description LIKE ?
                )
            """

            term = f"%{search.strip()}%"

            params.extend([
                term,
                term,
                term,
            ])

        if genre and genre != "All":

            query += " AND genre=?"

            params.append(genre)

        if year and year > 0:

            query += " AND year=?"

            params.append(year)

        if min_rating > 0:

            query += " AND rating>=?"

            params.append(min_rating)

        if sort == "Popularity":

            query += """
                ORDER BY
                (
                    SELECT COUNT(*)
                    FROM movie_views v
                    WHERE v.movie_id=movies.id
                ) DESC,
                rating DESC
            """

        elif sort == "Newest":

            query += """
                ORDER BY
                created_at DESC
            """

        elif sort == "Rating":

            query += """
                ORDER BY
                rating DESC
            """

        else:

            query += """
                ORDER BY
                title COLLATE NOCASE
            """

        return self.fetchall(
            query,
            params
        )

    # ==========================================================
    # WATCHLIST
    # ==========================================================

    def is_in_watchlist(self, profile_id, movie_id):

        row = self.fetchone(
            """
            SELECT id
            FROM watchlist
            WHERE profile_id=?
            AND movie_id=?
            LIMIT 1
            """,
            (
                profile_id,
                movie_id,
            )
        )

        return row is not None

    def toggle_watchlist(self, profile_id, user_id, movie_id):

        existing = self.fetchone(
            """
            SELECT id
            FROM watchlist
            WHERE profile_id=?
            AND movie_id=?
            LIMIT 1
            """,
            (
                profile_id,
                movie_id,
            )
        )

        if existing:

            self.execute(
                """
                DELETE FROM watchlist
                WHERE id=?
                """,
                (existing["id"],)
            )

            return False

        self.execute(
            """
            INSERT INTO watchlist
            (
                profile_id,
                user_id,
                movie_id,
                created_at
            )
            VALUES (?,?,?,?)
            """,
            (
                profile_id,
                user_id,
                movie_id,
                now(),
            )
        )

        return True

    def get_watchlist(self, profile_id):

        return self.fetchall(
            """
            SELECT m.*
            FROM movies m
            INNER JOIN watchlist w
                ON w.movie_id=m.id
            WHERE w.profile_id=?
            ORDER BY w.created_at DESC
            """,
            (profile_id,)
        )

    # ==========================================================
    # HISTORY
    # ==========================================================

    def get_history(self, profile_id):

        return self.fetchall(
            """
            SELECT
                m.*,
                h.progress,
                h.duration,
                h.watched_at
            FROM watch_history h
            INNER JOIN movies m
                ON m.id=h.movie_id
            WHERE h.profile_id=?
            ORDER BY h.watched_at DESC
            """,
            (profile_id,)
        )

    def get_history_movie(self, profile_id, movie_id):

        return self.fetchone(
            """
            SELECT *
            FROM watch_history
            WHERE profile_id=?
            AND movie_id=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                profile_id,
                movie_id,
            )
        )

    def save_progress(
        self,
        profile_id,
        user_id,
        movie_id,
        progress,
        duration
    ):

        existing = self.fetchone(
            """
            SELECT id
            FROM watch_history
            WHERE profile_id=?
            AND movie_id=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                profile_id,
                movie_id,
            )
        )

        if existing:

            self.execute(
                """
                UPDATE watch_history
                SET progress=?,
                    duration=?,
                    watched_at=?
                WHERE id=?
                """,
                (
                    progress,
                    duration,
                    now(),
                    existing["id"],
                )
            )

        else:

            self.execute(
                """
                INSERT INTO watch_history
                (
                    profile_id,
                    user_id,
                    movie_id,
                    progress,
                    duration,
                    watched_at
                )
                VALUES (?,?,?,?,?,?)
                """,
                (
                    profile_id,
                    user_id,
                    movie_id,
                    progress,
                    duration,
                    now(),
                )
            )

    # ==========================================================
    # RATINGS
    # ==========================================================

    def get_user_rating(self, profile_id, movie_id):

        return self.fetchone(
            """
            SELECT rating
            FROM ratings
            WHERE profile_id=?
            AND movie_id=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                profile_id,
                movie_id,
            )
        )

    def set_rating(
        self,
        profile_id,
        user_id,
        movie_id,
        rating
    ):

        existing = self.fetchone(
            """
            SELECT id
            FROM ratings
            WHERE profile_id=?
            AND movie_id=?
            LIMIT 1
            """,
            (
                profile_id,
                movie_id,
            )
        )

        if existing:

            self.execute(
                """
                UPDATE ratings
                SET rating=?,
                    created_at=?
                WHERE id=?
                """,
                (
                    rating,
                    now(),
                    existing["id"],
                )
            )

        else:

            self.execute(
                """
                INSERT INTO ratings
                (
                    profile_id,
                    user_id,
                    movie_id,
                    rating,
                    created_at
                )
                VALUES (?,?,?,?,?)
                """,
                (
                    profile_id,
                    user_id,
                    movie_id,
                    rating,
                    now(),
                )
            )

    # ==========================================================
    # LIKES
    # ==========================================================

    def get_like(self, profile_id, movie_id):

        return self.fetchone(
            """
            SELECT value
            FROM likes
            WHERE profile_id=?
            AND movie_id=?
            LIMIT 1
            """,
            (
                profile_id,
                movie_id,
            )
        )

    def set_like(
        self,
        profile_id,
        user_id,
        movie_id,
        value
    ):

        existing = self.fetchone(
            """
            SELECT id
            FROM likes
            WHERE profile_id=?
            AND movie_id=?
            LIMIT 1
            """,
            (
                profile_id,
                movie_id,
            )
        )

        if existing:

            self.execute(
                """
                UPDATE likes
                SET value=?,
                    created_at=?
                WHERE id=?
                """,
                (
                    value,
                    now(),
                    existing["id"],
                )
            )

        else:

            self.execute(
                """
                INSERT INTO likes
                (
                    profile_id,
                    user_id,
                    movie_id,
                    value,
                    created_at
                )
                VALUES (?,?,?,?,?)
                """,
                (
                    profile_id,
                    user_id,
                    movie_id,
                    value,
                    now(),
                )
            )

    # ==========================================================
    # VIEWS
    # ==========================================================

    def add_view(
        self,
        profile_id,
        user_id,
        movie_id
    ):

        self.execute(
            """
            INSERT INTO movie_views
            (
                profile_id,
                user_id,
                movie_id,
                viewed_at
            )
            VALUES (?,?,?,?)
            """,
            (
                profile_id,
                user_id,
                movie_id,
                now(),
            )
        )

    def view_count(self, movie_id):

        row = self.fetchone(
            """
            SELECT COUNT(*) AS count
            FROM movie_views
            WHERE movie_id=?
            """,
            (movie_id,)
        )

        return row["count"] if row else 0

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    def recommended(self, profile_id):

        history = self.fetchone(
            """
            SELECT m.genre
            FROM watch_history h
            INNER JOIN movies m
                ON m.id=h.movie_id
            WHERE h.profile_id=?
            ORDER BY h.watched_at DESC
            LIMIT 1
            """,
            (profile_id,)
        )

        if history and history["genre"]:

            rows = self.fetchall(
                """
                SELECT m.*
                FROM movies m
                WHERE m.genre=?
                AND m.id NOT IN (
                    SELECT movie_id
                    FROM watch_history
                    WHERE profile_id=?
                )
                ORDER BY m.rating DESC
                LIMIT 10
                """,
                (
                    history["genre"],
                    profile_id,
                )
            )

            if rows:
                return rows

        return self.fetchall(
            """
            SELECT *
            FROM movies
            ORDER BY rating DESC
            LIMIT 10
            """
        )

    def because_you_watched(self, profile_id):

        watched = self.fetchone(
            """
            SELECT m.*
            FROM watch_history h
            INNER JOIN movies m
                ON m.id=h.movie_id
            WHERE h.profile_id=?
            ORDER BY h.watched_at DESC
            LIMIT 1
            """,
            (profile_id,)
        )

        if not watched:
            return []

        return self.fetchall(
            """
            SELECT *
            FROM movies
            WHERE genre=?
            AND id!=?
            ORDER BY rating DESC
            LIMIT 10
            """,
            (
                watched["genre"],
                watched["id"],
            )
        )

    def similar_movies(self, movie_id):

        movie = self.get_movie(movie_id)

        if not movie:
            return []

        return self.fetchall(
            """
            SELECT *
            FROM movies
            WHERE genre=?
            AND id!=?
            ORDER BY rating DESC
            LIMIT 10
            """,
            (
                movie["genre"],
                movie_id,
            )
        )

    # ==========================================================
    # ADMIN
    # ==========================================================

    def admin_stats(self):

        users = self.fetchone(
            "SELECT COUNT(*) AS count FROM users"
        )["count"]

        profiles = self.fetchone(
            "SELECT COUNT(*) AS count FROM profiles"
        )["count"]

        movies = self.fetchone(
            "SELECT COUNT(*) AS count FROM movies"
        )["count"]

        views = self.fetchone(
            "SELECT COUNT(*) AS count FROM movie_views"
        )["count"]

        return {
            "users": users,
            "profiles": profiles,
            "movies": movies,
            "views": views,
        }

    def most_watched(self):

        return self.fetchall(
            """
            SELECT
                m.title,
                m.genre,
                COUNT(v.id) AS views
            FROM movies m
            LEFT JOIN movie_views v
                ON v.movie_id=m.id
            GROUP BY m.id
            ORDER BY views DESC
            LIMIT 10
            """
        )

    def popular_genres(self):

        return self.fetchall(
            """
            SELECT
                m.genre,
                COUNT(v.id) AS views
            FROM movies m
            LEFT JOIN movie_views v
                ON v.movie_id=m.id
            GROUP BY m.genre
            ORDER BY views DESC
            """
        )

    def save_movie(self, movie_id, data):

        if movie_id:

            self.execute(
                """
                UPDATE movies
                SET title=?,
                    genre=?,
                    year=?,
                    rating=?,
                    description=?,
                    poster=?,
                    video=?
                WHERE id=?
                """,
                (
                    data["title"],
                    data["genre"],
                    data["year"],
                    data["rating"],
                    data["description"],
                    data["poster"],
                    data["video"],
                    movie_id,
                )
            )

        else:

            self.execute(
                """
                INSERT INTO movies
                (
                    title,
                    genre,
                    year,
                    rating,
                    description,
                    poster,
                    video,
                    created_at
                )
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    data["title"],
                    data["genre"],
                    data["year"],
                    data["rating"],
                    data["description"],
                    data["poster"],
                    data["video"],
                    now(),
                )
            )

    def delete_movie(self, movie_id):

        for table in [
            "watchlist",
            "watch_history",
            "ratings",
            "likes",
            "movie_views",
        ]:

            self.execute(
                f"""
                DELETE FROM {table}
                WHERE movie_id=?
                """,
                (movie_id,)
            )

        self.execute(
            """
            DELETE FROM movies
            WHERE id=?
            """,
            (movie_id,)
        )

    # ==========================================================

    def close(self):

        try:
            self.conn.close()
        except Exception:
            pass


db = Database()


# ==============================================================
# MOVIE CARD
# ==============================================================


db = Database()
