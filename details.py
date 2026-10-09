# YuiFlix V11 - Movie Details

from common import *
from database import db

from ui_cards import MovieCard

class MovieDetails(QDialog):

    def __init__(
        self,
        movie,
        profile,
        user,
        play_callback,
        parent=None
    ):

        super().__init__(parent)

        self.movie = movie
        self.profile = profile
        self.user = user
        self.play_callback = play_callback

        self.setWindowTitle(
            movie.get("title", "Movie")
        )

        self.resize(
            850,
            600
        )

        layout = QVBoxLayout(self)

        top = QHBoxLayout()

        poster = QLabel()

        poster_path = asset_path(
            POSTER_DIR,
            movie.get("poster", "")
        )

        if poster_path:

            pixmap = QPixmap(poster_path)

            poster.setPixmap(
                pixmap.scaled(
                    260,
                    360,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )

        else:

            poster.setText(
                "NO POSTER"
            )

        top.addWidget(poster)

        info = QVBoxLayout()

        title = QLabel(
            movie.get("title", "")
        )

        title.setStyleSheet(
            """
            font-size:30px;
            font-weight:bold;
            """
        )

        title.setWordWrap(True)

        info.addWidget(title)

        meta = QLabel(
            f'{movie.get("year","")} • '
            f'{movie.get("genre","")} • '
            f'★ {safe_float(movie.get("rating")):.1f}'
        )

        meta.setStyleSheet(
            "color:#bbbbbb;"
        )

        info.addWidget(meta)

        views = QLabel(
            f'Views: {db.view_count(movie["id"])}'
        )

        views.setStyleSheet(
            "color:#888888;"
        )

        info.addWidget(views)

        description = QLabel(
            movie.get(
                "description",
                ""
            )
        )

        description.setWordWrap(True)

        description.setStyleSheet(
            "font-size:15px;"
        )

        info.addWidget(
            description
        )

        info.addStretch()

        buttons = QHBoxLayout()

        play = QPushButton(
            "▶ Play"
        )

        play.setStyleSheet(
            "background:#e50914;font-weight:bold;"
        )

        play.clicked.connect(
            self.play
        )

        buttons.addWidget(play)

        in_list = db.is_in_watchlist(
            self.profile["id"],
            self.movie["id"]
        )

        self.list_button = QPushButton(
            "✓ My List"
            if in_list
            else "+ My List"
        )

        self.list_button.clicked.connect(
            self.toggle_list
        )

        buttons.addWidget(
            self.list_button
        )

        like = QPushButton("👍")
        dislike = QPushButton("👎")

        like.clicked.connect(
            lambda:
            self.set_like(1)
        )

        dislike.clicked.connect(
            lambda:
            self.set_like(-1)
        )

        buttons.addWidget(like)
        buttons.addWidget(dislike)

        info.addLayout(buttons)

        rating_row = QHBoxLayout()

        rating_row.addWidget(
            QLabel("Your Rating:")
        )

        self.rating_combo = QComboBox()

        self.rating_combo.addItems(
            [
                "Not Rated",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
            ]
        )

        current_rating = db.get_user_rating(
            self.profile["id"],
            self.movie["id"]
        )

        if current_rating:

            value = safe_int(
                current_rating["rating"]
            )

            self.rating_combo.setCurrentText(
                str(value)
            )

        self.rating_combo.currentTextChanged.connect(
            self.rating_changed
        )

        rating_row.addWidget(
            self.rating_combo
        )

        info.addLayout(
            rating_row
        )

        top.addLayout(info)

        layout.addLayout(top)

        similar = db.similar_movies(
            movie["id"]
        )

        if similar:

            label = QLabel(
                "More Like This"
            )

            label.setStyleSheet(
                """
                font-size:20px;
                font-weight:bold;
                margin-top:15px;
                """
            )

            layout.addWidget(label)

            row = QHBoxLayout()

            for similar_movie in similar[:5]:

                card = MovieCard(
                    similar_movie
                )

                card.clicked.connect(
                    self.open_similar
                )

                row.addWidget(card)

            scroll_widget = QWidget()

            scroll_widget.setLayout(
                row
            )

            scroll = QScrollArea()

            scroll.setWidgetResizable(True)
            scroll.setFixedHeight(330)
            scroll.setWidget(
                scroll_widget
            )

            layout.addWidget(
                scroll
            )

    def play(self):

        self.play_callback(
            self.movie
        )

        self.accept()

    def toggle_list(self):

        added = db.toggle_watchlist(
            self.profile["id"],
            self.user["id"],
            self.movie["id"]
        )

        self.list_button.setText(
            "✓ My List"
            if added
            else "+ My List"
        )

    def set_like(self, value):

        db.set_like(
            self.profile["id"],
            self.user["id"],
            self.movie["id"],
            value
        )

    def rating_changed(self, value):

        if value == "Not Rated":
            return

        db.set_rating(
            self.profile["id"],
            self.user["id"],
            self.movie["id"],
            safe_float(value)
        )

    def open_similar(self, movie):

        self.movie = movie

        self.accept()

        QTimer.singleShot(
            100,
            lambda:
            self.play_callback(movie)
        )


# ==============================================================
# CLICKABLE VIDEO WIDGET
# ==============================================================
