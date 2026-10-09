# YuiFlix V11 - Navigation

from common import *
from database import db

class NavigationBar(QWidget):

    home = Signal()
    movies = Signal()
    my_list = Signal()
    history = Signal()
    profile = Signal()
    admin = Signal()
    change_profile = Signal()
    logout = Signal()

    def __init__(self, user, profile):

        super().__init__()

        self.user = user
        self.profile_data = profile

        self.setFixedHeight(70)

        layout = QHBoxLayout(self)

        logo = QLabel("YuiFlix")

        logo.setStyleSheet(
            """
            color:#e50914;
            font-size:27px;
            font-weight:bold;
            """
        )

        layout.addWidget(logo)

        def add_button(text, signal):

            button = QPushButton(text)
            button.clicked.connect(
                signal.emit
            )

            layout.addWidget(button)

        add_button("Home", self.home)
        add_button("Movies", self.movies)
        add_button("My List", self.my_list)
        add_button("History", self.history)

        layout.addStretch()

        profile_button = QPushButton(
            f"👤 {profile.get('name','Profile')}"
        )

        profile_button.clicked.connect(
            self.change_profile.emit
        )

        layout.addWidget(profile_button)

        add_button(
            "Profile",
            self.profile
        )

        if safe_int(user.get("is_admin")) == 1:

            add_button(
                "Admin",
                self.admin
            )

        logout = QPushButton("Logout")

        logout.clicked.connect(
            self.logout.emit
        )

        layout.addWidget(logout)


# ==============================================================
# HOME PAGE
# ==============================================================
