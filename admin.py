# YuiFlix V11 - Admin

from common import *
from database import db

class MovieDialog(QDialog):

    def __init__(
        self,
        movie=None,
        parent=None
    ):

        super().__init__(parent)

        self.movie = movie or {}

        self.poster_file = ""
        self.video_file = ""

        self.setWindowTitle(
            "Edit Movie"
            if movie
            else "Add Movie"
        )

        self.resize(
            650,
            600
        )

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.title = QLineEdit(
            self.movie.get("title", "")
        )

        self.genre = QLineEdit(
            self.movie.get("genre", "")
        )

        self.year = QSpinBox()

        self.year.setRange(
            1900,
            2200
        )

        self.year.setValue(
            safe_int(
                self.movie.get(
                    "year",
                    datetime.now().year
                )
            )
        )

        self.rating = QDoubleSpinBox()

        self.rating.setRange(
            0,
            10
        )

        self.rating.setSingleStep(
            0.1
        )

        self.rating.setValue(
            safe_float(
                self.movie.get(
                    "rating",
                    0
                )
            )
        )

        self.description = QTextEdit(
            self.movie.get(
                "description",
                ""
            )
        )

        form.addRow(
            "Title:",
            self.title
        )

        form.addRow(
            "Genre:",
            self.genre
        )

        form.addRow(
            "Year:",
            self.year
        )

        form.addRow(
            "Rating:",
            self.rating
        )

        form.addRow(
            "Description:",
            self.description
        )

        layout.addLayout(form)

        poster_row = QHBoxLayout()

        self.poster_label = QLabel(
            self.movie.get(
                "poster",
                "No poster selected"
            )
        )

        poster = QPushButton(
            "Choose Poster"
        )

        poster.clicked.connect(
            self.choose_poster
        )

        poster_row.addWidget(
            self.poster_label,
            1
        )

        poster_row.addWidget(
            poster
        )

        layout.addLayout(
            poster_row
        )

        video_row = QHBoxLayout()

        self.video_label = QLabel(
            self.movie.get(
                "video",
                "No video selected"
            )
        )

        video = QPushButton(
            "Choose Video"
        )

        video.clicked.connect(
            self.choose_video
        )

        video_row.addWidget(
            self.video_label,
            1
        )

        video_row.addWidget(
            video
        )

        layout.addLayout(
            video_row
        )

        buttons = QHBoxLayout()

        cancel = QPushButton(
            "Cancel"
        )

        cancel.clicked.connect(
            self.reject
        )

        save = QPushButton(
            "Save"
        )

        save.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            cancel
        )

        buttons.addWidget(
            save
        )

        layout.addLayout(
            buttons
        )

    def choose_poster(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Poster",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)"
        )

        if not path:
            return

        filename = copy_asset(
            path,
            POSTER_DIR
        )

        if filename:

            self.poster_file = filename

            self.poster_label.setText(
                filename
            )

    def choose_video(self):

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Video",
            "",
            "Videos (*.mp4 *.mkv *.avi *.mov)"
        )

        if not path:
            return

        filename = copy_asset(
            path,
            VIDEO_DIR
        )

        if filename:

            self.video_file = filename

            self.video_label.setText(
                filename
            )

    def data(self):

        poster = self.poster_file

        if not poster:

            poster = self.movie.get(
                "poster",
                ""
            )

        video = self.video_file

        if not video:

            video = self.movie.get(
                "video",
                ""
            )

        return {
            "title":
                self.title.text().strip(),

            "genre":
                self.genre.text().strip(),

            "year":
                self.year.value(),

            "rating":
                self.rating.value(),

            "description":
                self.description.toPlainText().strip(),

            "poster":
                poster,

            "video":
                video,
        }


# ==============================================================
# ADMIN PAGE
# ==============================================================

class AdminPage(QWidget):

    def __init__(
        self,
        callback
    ):

        super().__init__()

        self.callback = callback

        self.build()

    def build(self):

        layout = QVBoxLayout(self)

        title = QLabel(
            "Admin Dashboard"
        )

        title.setStyleSheet(
            """
            font-size:30px;
            font-weight:bold;
            """
        )

        layout.addWidget(
            title
        )

        stats_layout = QHBoxLayout()

        stats = db.admin_stats()

        self.add_stat_card(
            stats_layout,
            "Users",
            stats["users"]
        )

        self.add_stat_card(
            stats_layout,
            "Profiles",
            stats["profiles"]
        )

        self.add_stat_card(
            stats_layout,
            "Movies",
            stats["movies"]
        )

        self.add_stat_card(
            stats_layout,
            "Views",
            stats["views"]
        )

        layout.addLayout(
            stats_layout
        )

        buttons = QHBoxLayout()

        add = QPushButton(
            "+ Add Movie"
        )

        add.setStyleSheet(
            "background:#e50914;font-weight:bold;"
        )

        add.clicked.connect(
            self.add_movie
        )

        buttons.addWidget(add)

        refresh = QPushButton(
            "Refresh"
        )

        refresh.clicked.connect(
            self.refresh
        )

        buttons.addWidget(
            refresh
        )

        layout.addLayout(
            buttons
        )

        self.movie_list = QListWidget()

        layout.addWidget(
            self.movie_list
        )

        self.load_movies()

        layout.addWidget(
            QLabel("Most Watched")
        )

        watched = QListWidget()

        for row in db.most_watched():

            watched.addItem(
                f'{row["title"]} — '
                f'{row["views"]} views'
            )

        watched.setMaximumHeight(
            180
        )

        layout.addWidget(
            watched
        )

        layout.addWidget(
            QLabel("Popular Genres")
        )

        genres = QListWidget()

        for row in db.popular_genres():

            genres.addItem(
                f'{row["genre"]} — '
                f'{row["views"]} views'
            )

        genres.setMaximumHeight(
            150
        )

        layout.addWidget(
            genres
        )

    def add_stat_card(
        self,
        layout,
        title,
        value
    ):

        card = QFrame()

        card.setObjectName(
            "adminCard"
        )

        card.setMinimumHeight(
            100
        )

        box = QVBoxLayout(card)

        label = QLabel(title)

        label.setStyleSheet(
            "color:#999999;"
        )

        number = QLabel(
            str(value)
        )

        number.setStyleSheet(
            """
            font-size:30px;
            font-weight:bold;
            """
        )

        box.addWidget(label)
        box.addWidget(number)

        layout.addWidget(
            card
        )

    def load_movies(self):

        self.movie_list.clear()

        for movie in db.get_movies():

            item = QListWidgetItem(
                f'{movie["title"]} '
                f'({movie["year"]}) '
                f'• {movie["genre"]} '
                f'• ★ {movie["rating"]}'
            )

            item.setData(
                Qt.UserRole,
                movie["id"]
            )

            self.movie_list.addItem(
                item
            )

        self.movie_list.itemDoubleClicked.connect(
            self.edit_movie
        )

        self.movie_list.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.movie_list.customContextMenuRequested.connect(
            self.movie_menu
        )

    def add_movie(self):

        dialog = MovieDialog(
            parent=self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        data = dialog.data()

        if not data["title"]:

            QMessageBox.warning(
                self,
                "Movie",
                "Movie title is required."
            )

            return

        db.save_movie(
            None,
            data
        )

        self.refresh()

    def edit_movie(self, item):

        movie_id = item.data(
            Qt.UserRole
        )

        movie = db.get_movie(
            movie_id
        )

        if not movie:
            return

        dialog = MovieDialog(
            movie,
            self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        db.save_movie(
            movie_id,
            dialog.data()
        )

        self.refresh()

    def movie_menu(self, position):

        item = self.movie_list.itemAt(
            position
        )

        if not item:
            return

        movie_id = item.data(
            Qt.UserRole
        )

        movie = db.get_movie(
            movie_id
        )

        if not movie:
            return

        menu = QMessageBox(
            self
        )

        menu.setWindowTitle(
            movie["title"]
        )

        menu.setText(
            "What would you like to do?"
        )

        edit = menu.addButton(
            "Edit",
            QMessageBox.AcceptRole
        )

        delete = menu.addButton(
            "Delete",
            QMessageBox.DestructiveRole
        )

        cancel = menu.addButton(
            "Cancel",
            QMessageBox.RejectRole
        )

        menu.exec()

        clicked = menu.clickedButton()

        if clicked == edit:

            self.edit_movie(item)

        elif clicked == delete:

            answer = QMessageBox.question(
                self,
                "Delete Movie",
                f'Delete "{movie["title"]}"?'
            )

            if answer == QMessageBox.Yes:

                db.delete_movie(
                    movie_id
                )

                self.refresh()

    def refresh(self):

        self.load_movies()


# ==============================================================
# MAIN WINDOW
# ==============================================================
