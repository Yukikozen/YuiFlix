# YuiFlix V11 - Profiles

from common import *
from database import db

class ProfileSelector(QDialog):

    def __init__(self, user, parent=None):

        super().__init__(parent)

        self.user = user
        self.selected_profile = None

        self.setWindowTitle(
            "Who's Watching?"
        )

        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        title = QLabel(
            "Who's watching?"
        )

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet(
            """
            font-size:28px;
            font-weight:bold;
            """
        )

        layout.addWidget(title)

        self.profile_layout = QHBoxLayout()

        self.profile_layout.setAlignment(
            Qt.AlignCenter
        )

        layout.addLayout(
            self.profile_layout
        )

        add = QPushButton(
            "+ Add Profile"
        )

        add.clicked.connect(
            self.add_profile
        )

        layout.addWidget(
            add,
            alignment=Qt.AlignCenter
        )

        self.load_profiles()

    def clear_layout(self, layout):

        while layout.count():

            item = layout.takeAt(0)

            widget = item.widget()

            if widget:

                widget.deleteLater()

    def load_profiles(self):

        self.clear_layout(
            self.profile_layout
        )

        profiles = db.get_profiles(
            self.user["id"]
        )

        for profile in profiles:

            profile_data = dict(profile)

            button = QPushButton()

            button.setFixedSize(150, 190)

            text = profile_data.get(
                "name",
                "Profile"
            )

            button.setText(
                f"👤\n\n{text}"
            )

            button.setStyleSheet(
                """
                QPushButton {
                    background:#242424;
                    border:2px solid #333333;
                    font-size:17px;
                    border-radius:8px;
                }

                QPushButton:hover {
                    border:2px solid white;
                }
                """
            )

            button.clicked.connect(
                lambda checked=False,
                p=profile_data:
                self.select_profile(p)
            )

            self.profile_layout.addWidget(
                button
            )

    def select_profile(self, profile):

        self.selected_profile = profile

        self.accept()

    def add_profile(self):

        name, ok = QInputDialog.getText(
            self,
            "Add Profile",
            "Profile name:"
        )

        if not ok:
            return

        name = name.strip()

        if not name:
            return

        profile = db.add_profile(
            self.user["id"],
            name
        )

        if profile:

            self.selected_profile = dict(
                profile
            )

            self.accept()


# ==============================================================
# NAVIGATION
# ==============================================================
