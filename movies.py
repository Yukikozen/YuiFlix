# YuiFlix V11 - Movie Browsing

from common import *
from database import db

from ui_cards import MovieCard

class MoviesPage(QWidget):

    def __init__(self, callback):

        super().__init__()

        self.callback = callback

        self.debounce = QTimer(self)
        self.debounce.setSingleShot(True)
        self.debounce.setInterval(200)

        self.debounce.timeout.connect(
            self.apply_filters
        )

        self.build()

    def build(self):

        outer = QVBoxLayout(self)

        title = QLabel("Movies")

        title.setStyleSheet(
            """
            font-size:28px;
            font-weight:bold;
            """
        )

        outer.addWidget(title)

        controls = QHBoxLayout()

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Search movies..."
        )

        self.search.textChanged.connect(
            lambda: self.debounce.start()
        )

        controls.addWidget(
            self.search,
            3
        )

        self.genre = QComboBox()

        genres = ["All"]

        for row in db.fetchall(
            """
            SELECT DISTINCT genre
            FROM movies
            WHERE genre IS NOT NULL
            ORDER BY genre
            """
        ):

            if row["genre"]:

                genres.append(
                    row["genre"]
                )

        self.genre.addItems(genres)

        self.genre.currentTextChanged.connect(
            lambda: self.debounce.start()
        )

        controls.addWidget(
            self.genre
        )

        self.year = QComboBox()

        self.year.addItem(
            "All Years",
            0
        )

        years = db.fetchall(
            """
            SELECT DISTINCT year
            FROM movies
            WHERE year IS NOT NULL
            ORDER BY year DESC
            """
        )

        for row in years:

            self.year.addItem(
                str(row["year"]),
                row["year"]
            )

        self.year.currentIndexChanged.connect(
            lambda: self.debounce.start()
        )

        controls.addWidget(
            self.year
        )

        self.rating = QComboBox()

        self.rating.addItems([
            "Any Rating",
            "7+",
            "8+",
            "9+",
        ])

        self.rating.currentTextChanged.connect(
            lambda: self.debounce.start()
        )

        controls.addWidget(
            self.rating
        )

        self.sort = QComboBox()

        self.sort.addItems([
            "A-Z",
            "Popularity",
            "Newest",
            "Rating",
        ])

        self.sort.currentTextChanged.connect(
            lambda: self.debounce.start()
        )

        controls.addWidget(
            self.sort
        )

        outer.addLayout(controls)

        self.result_count = QLabel()

        self.result_count.setStyleSheet(
            "color:#888888;padding:5px;"
        )

        outer.addWidget(
            self.result_count
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        container = QWidget()

        self.grid = QGridLayout(
            container
        )

        self.grid.setSpacing(18)

        scroll.setWidget(container)

        outer.addWidget(scroll)

        self.apply_filters()

    def clear_grid(self):

        while self.grid.count():

            item = self.grid.takeAt(0)

            widget = item.widget()

            if widget:

                widget.deleteLater()

    def apply_filters(self):

        movies = db.search_movies(
            search=self.search.text(),
            genre=self.genre.currentText(),
            year=self.year.currentData(),
            min_rating=self.rating_value(),
            sort=self.sort.currentText()
        )

        self.clear_grid()

        for index, movie in enumerate(
            movies
        ):

            card = MovieCard(movie)

            card.clicked.connect(
                self.callback
            )

            row = index // 6
            column = index % 6

            self.grid.addWidget(
                card,
                row,
                column
            )

        self.result_count.setText(
            f"{len(movies)} movie(s) found"
        )

    def rating_value(self):

        value = self.rating.currentText()

        if value.startswith("7"):
            return 7

        if value.startswith("8"):
            return 8

        if value.startswith("9"):
            return 9

        return 0


# ==============================================================
# LIST PAGE
# ==============================================================

class ListPage(QWidget):

    def __init__(
        self,
        title,
        movies,
        callback
    ):

        super().__init__()

        layout = QVBoxLayout(self)

        heading = QLabel(title)

        heading.setStyleSheet(
            """
            font-size:28px;
            font-weight:bold;
            """
        )

        layout.addWidget(
            heading
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        container = QWidget()

        grid = QGridLayout(container)

        grid.setSpacing(18)

        for index, movie in enumerate(
            movies
        ):

            card = MovieCard(movie)

            card.clicked.connect(
                callback
            )

            grid.addWidget(
                card,
                index // 6,
                index % 6
            )

        scroll.setWidget(
            container
        )

        layout.addWidget(
            scroll
        )


# ==============================================================
# MOVIE DETAILS
# ==============================================================
