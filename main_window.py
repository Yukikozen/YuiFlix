# YuiFlix V11 - Main Window

from common import *
from database import db

from auth import LoginPage, RegisterDialog
from profiles import ProfileSelector
from navigation import NavigationBar
from home import HomePage
from movies import MoviesPage, ListPage
from details import MovieDetails
from player import VideoPlayer
from profile_page import ProfilePage
from admin import AdminPage


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            APP_NAME
        )

        self.resize(
            1400,
            850
        )

        self.user = None
        self.profile = None

        self.root = QStackedWidget()

        self.setCentralWidget(
            self.root
        )

        self.login_page = LoginPage()

        self.login_page.logged_in.connect(
            self.logged_in
        )

        self.login_page.register_requested.connect(
            self.register
        )

        self.root.addWidget(
            self.login_page
        )

        self.root.setCurrentWidget(
            self.login_page
        )

        self.main_root = None
        self.page_stack = None
        self.nav = None

        self.player = None

    # ----------------------------------------------------------

    def register(self):

        dialog = RegisterDialog(
            self
        )

        dialog.exec()

    # ----------------------------------------------------------

    def logged_in(self, user):

        self.user = dict(user)

        selector = ProfileSelector(
            self.user,
            self
        )

        result = selector.exec()

        if result != QDialog.Accepted:

            self.user = None
            self.profile = None

            return

        profile = selector.selected_profile

        if not profile:

            self.user = None
            self.profile = None

            return

        fresh_profile = db.fetchone(
            """
            SELECT *
            FROM profiles
            WHERE id=?
            """,
            (
                profile["id"],
            )
        )

        if not fresh_profile:

            QMessageBox.warning(
                self,
                "Profile",
                "Unable to load profile."
            )

            self.user = None
            self.profile = None

            return

        self.profile = fresh_profile

        global CURRENT_PROFILE_ID
        global CURRENT_USER_ID

        CURRENT_PROFILE_ID = self.profile["id"]
        CURRENT_USER_ID = self.user["id"]

        self.setup_main_ui()

    # ----------------------------------------------------------

    def setup_main_ui(self):

        # IMPORTANT:
        # V11 keeps exactly ONE root widget.
        # This prevents the V10 root accumulation problem.

        if self.main_root is None:

            self.main_root = QWidget()

            root_layout = QVBoxLayout(
                self.main_root
            )

            root_layout.setContentsMargins(
                0,
                0,
                0,
                0
            )

            self.nav = NavigationBar(
                self.user,
                self.profile
            )

            self.page_stack = QStackedWidget()

            root_layout.addWidget(
                self.nav
            )

            root_layout.addWidget(
                self.page_stack,
                1
            )

            self.root.addWidget(
                self.main_root
            )

            self.connect_navigation()

        else:

            # Replace navigation bar
            old_nav = self.nav

            self.nav = NavigationBar(
                self.user,
                self.profile
            )

            self.main_root.layout().replaceWidget(
                old_nav,
                self.nav
            )

            old_nav.deleteLater()

            self.connect_navigation()

        self.clear_page_stack()

        self.root.setCurrentWidget(
            self.main_root
        )

        self.show_home()

    # ----------------------------------------------------------

    def connect_navigation(self):

        self.nav.home.connect(
            self.show_home
        )

        self.nav.movies.connect(
            self.show_movies
        )

        self.nav.my_list.connect(
            self.show_my_list
        )

        self.nav.history.connect(
            self.show_history
        )

        self.nav.profile.connect(
            self.show_profile
        )

        self.nav.change_profile.connect(
            self.change_profile
        )

        self.nav.logout.connect(
            self.logout
        )

        if safe_int(
            self.user.get("is_admin")
        ) == 1:

            self.nav.admin.connect(
                self.show_admin
            )

    # ----------------------------------------------------------

    def clear_page_stack(self):

        if not self.page_stack:
            return

        while self.page_stack.count():

            widget = self.page_stack.widget(0)

            self.page_stack.removeWidget(
                widget
            )

            widget.deleteLater()

    # ----------------------------------------------------------

    def set_page(self, page):

        self.clear_page_stack()

        self.page_stack.addWidget(
            page
        )

        self.page_stack.setCurrentWidget(
            page
        )

    # ----------------------------------------------------------

    def show_home(self):

        self.set_page(
            HomePage(
                self.profile,
                self.open_movie
            )
        )

    # ----------------------------------------------------------

    def show_movies(self):

        self.set_page(
            MoviesPage(
                self.open_movie
            )
        )

    # ----------------------------------------------------------

    def show_my_list(self):

        movies = db.get_watchlist(
            self.profile["id"]
        )

        self.set_page(
            ListPage(
                "My List",
                movies,
                self.open_movie
            )
        )

    # ----------------------------------------------------------

    def show_history(self):

        movies = db.get_history(
            self.profile["id"]
        )

        self.set_page(
            ListPage(
                "Watch History",
                movies,
                self.open_movie
            )
        )

    # ----------------------------------------------------------

    def show_profile(self):

        page = ProfilePage(
            self.user,
            self.profile
        )

        page.changed.connect(
            self.profile_changed
        )

        self.set_page(
            page
        )

    # ----------------------------------------------------------

    def profile_changed(self):

        fresh = db.fetchone(
            """
            SELECT *
            FROM profiles
            WHERE id=?
            """,
            (
                self.profile["id"],
            )
        )

        if fresh:

            self.profile = fresh

            self.setup_main_ui()

    # ----------------------------------------------------------

    def show_admin(self):

        if safe_int(
            self.user.get("is_admin")
        ) != 1:

            return

        self.set_page(
            AdminPage(
                self.open_movie
            )
        )

    # ----------------------------------------------------------

    def open_movie(self, movie):

        dialog = MovieDetails(
            movie,
            self.profile,
            self.user,
            self.start_player,
            self
        )

        dialog.exec()

    # ----------------------------------------------------------

    def start_player(self, movie):

        movies = db.get_movies()

        if not movies:

            return

        if self.player:

            try:
                self.player.close()
            except Exception:
                pass

            self.player = None

        self.player = VideoPlayer(
            movie,
            self.profile,
            self.user,
            movies,
            self
        )

        self.player.closed.connect(
            self.player_closed
        )

        self.player.show()

    # ----------------------------------------------------------

    def player_closed(self):

        self.player = None

        if self.user and self.profile:

            self.show_home()

    # ----------------------------------------------------------

    def change_profile(self):

        selector = ProfileSelector(
            self.user,
            self
        )

        result = selector.exec()

        if result != QDialog.Accepted:
            return

        selected = selector.selected_profile

        if not selected:
            return

        fresh = db.fetchone(
            """
            SELECT *
            FROM profiles
            WHERE id=?
            AND user_id=?
            """,
            (
                selected["id"],
                self.user["id"],
            )
        )

        if not fresh:
            return

        self.profile = fresh

        global CURRENT_PROFILE_ID

        CURRENT_PROFILE_ID = self.profile["id"]

        self.setup_main_ui()

    # ----------------------------------------------------------

    def logout(self):

        if self.player:

            try:
                self.player.close()
            except Exception:
                pass

            self.player = None

        self.clear_page_stack()

        self.user = None
        self.profile = None

        global CURRENT_PROFILE_ID
        global CURRENT_USER_ID

        CURRENT_PROFILE_ID = None
        CURRENT_USER_ID = None

        self.root.setCurrentWidget(
            self.login_page
        )

    # ----------------------------------------------------------

    def closeEvent(self, event):

        if self.player:

            try:
                self.player.close()
            except Exception:
                pass

        db.close()

        event.accept()


# ==============================================================
# MAIN
# ==============================================================
