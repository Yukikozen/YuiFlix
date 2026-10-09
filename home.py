# YuiFlix V11 - Home Page

from common import *
from database import db

from ui_cards import MovieRow, Top10Row

class HomePage(QWidget):

    def __init__(self, profile, callback):

        super().__init__()

        self.profile = profile
        self.callback = callback

        self.hero_movies = []
        self.hero_index = 0

        self.hero_timer = QTimer(self)

        self.hero_timer.timeout.connect(
            self.rotate_hero
        )

        self.build()

    def build(self):

        outer = QVBoxLayout(self)

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        content = QWidget()

        self.content_layout = QVBoxLayout(
            content
        )

        self.content_layout.setContentsMargins(
            25,
            15,
            25,
            30
        )

        self.hero_movies = db.fetchall(
            """
            SELECT *
            FROM movies
            ORDER BY rating DESC
            LIMIT 5
            """
        )

        if self.hero_movies:

            self.create_hero(
                self.hero_movies[0]
            )

        self.add_home_sections()

        self.content_layout.addStretch()

        scroll.setWidget(content)

        outer.addWidget(scroll)

        if len(self.hero_movies) > 1:

            self.hero_timer.start(6000)

    # ----------------------------------------------------------

    def create_hero(self, movie):

        hero = QFrame()

        hero.setObjectName("hero")

        hero.setMinimumHeight(360)

        layout = QHBoxLayout(hero)

        layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        poster = QLabel()

        poster.setFixedWidth(270)

        poster_path = asset_path(
            POSTER_DIR,
            movie.get("poster", "")
        )

        if poster_path:

            pixmap = QPixmap(poster_path)

            poster.setPixmap(
                pixmap.scaled(
                    250,
                    330,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )

        layout.addWidget(poster)

        details = QVBoxLayout()

        title = QLabel(
            movie.get("title", "Featured")
        )

        title.setStyleSheet(
            """
            font-size:40px;
            font-weight:bold;
            """
        )

        title.setWordWrap(True)

        details.addWidget(title)

        meta = QLabel(
            f'{movie.get("year","")}   '
            f'•   {movie.get("genre","")}   '
            f'•   ★ {safe_float(movie.get("rating")):.1f}'
        )

        meta.setStyleSheet(
            "color:#bbbbbb;font-size:15px;"
        )

        details.addWidget(meta)

        description = QLabel(
            movie.get(
                "description",
                ""
            )
        )

        description.setWordWrap(True)

        description.setMaximumWidth(650)

        description.setStyleSheet(
            "font-size:15px;color:#dddddd;"
        )

        details.addWidget(description)

        details.addStretch()

        buttons = QHBoxLayout()

        play = QPushButton(
            "▶ Play"
        )

        play.setStyleSheet(
            """
            background:white;
            color:black;
            font-weight:bold;
            padding:12px 25px;
            """
        )

        play.clicked.connect(
            lambda checked=False,
            m=movie:
            self.callback(m)
        )

        info = QPushButton(
            "More Info"
        )

        info.clicked.connect(
            lambda checked=False,
            m=movie:
            self.callback(m)
        )

        buttons.addWidget(play)
        buttons.addWidget(info)
        buttons.addStretch()

        details.addLayout(buttons)

        layout.addLayout(details)

        self.hero_frame = hero

        self.content_layout.insertWidget(
            0,
            hero
        )

    # ----------------------------------------------------------

    def rotate_hero(self):

        if not self.hero_movies:
            return

        self.hero_index += 1

        if self.hero_index >= len(
            self.hero_movies
        ):
            self.hero_index = 0

        old = self.hero_frame

        new_movie = self.hero_movies[
            self.hero_index
        ]

        self.content_layout.removeWidget(
            old
        )

        old.deleteLater()

        self.create_hero(
            new_movie
        )

    # ----------------------------------------------------------

    def add_home_sections(self):

        continue_watching = db.fetchall(
            """
            SELECT
                m.*,
                h.progress,
                h.duration
            FROM watch_history h
            INNER JOIN movies m
                ON m.id=h.movie_id
            WHERE h.profile_id=?
            AND h.progress>0
            AND (
                h.duration=0
                OR h.progress<h.duration*0.95
            )
            ORDER BY h.watched_at DESC
            LIMIT 10
            """,
            (self.profile["id"],)
        )

        self.add_section(
            "Continue Watching",
            continue_watching
        )

        trending = db.fetchall(
            """
            SELECT
                m.*,
                COUNT(v.id) AS view_count
            FROM movies m
            LEFT JOIN movie_views v
                ON v.movie_id=m.id
            GROUP BY m.id
            ORDER BY view_count DESC,
                     m.rating DESC
            LIMIT 10
            """
        )

        self.add_section(
            "Trending Now",
            trending
        )

        top10 = db.fetchall(
            """
            SELECT *
            FROM movies
            ORDER BY rating DESC
            LIMIT 10
            """
        )

        self.add_top10(
            "Top 10 Movies",
            top10
        )

        recommended = db.recommended(
            self.profile["id"]
        )

        self.add_section(
            "Recommended For You",
            recommended
        )

        because = db.because_you_watched(
            self.profile["id"]
        )

        if because:

            self.add_section(
                "Because You Watched",
                because
            )

        top_rated = db.fetchall(
            """
            SELECT *
            FROM movies
            ORDER BY rating DESC
            LIMIT 10
            """
        )

        self.add_section(
            "Top Rated",
            top_rated
        )

        recent = db.fetchall(
            """
            SELECT *
            FROM movies
            ORDER BY created_at DESC
            LIMIT 10
            """
        )

        self.add_section(
            "Recently Added",
            recent
        )

        my_list = db.get_watchlist(
            self.profile["id"]
        )

        self.add_section(
            "My List",
            my_list
        )

    # ----------------------------------------------------------

    def add_section(self, title, movies):

        row = MovieRow(
            title,
            movies,
            self.callback
        )

        self.content_layout.addWidget(row)

    # ----------------------------------------------------------

    def add_top10(self, title, movies):

        row = MovieRow(
            title,
            movies,
            self.callback,
            top10=True
        )

        self.content_layout.addWidget(row)


# ==============================================================
# MOVIES PAGE
# ==============================================================
