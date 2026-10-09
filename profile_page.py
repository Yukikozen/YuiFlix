# YuiFlix V11 - Profile Page

from common import *
from database import db

class ProfilePage(QWidget):

    changed = Signal()

    def __init__(
        self,
        user,
        profile,
        parent=None
    ):

        super().__init__(parent)

        self.user = user
        self.profile = profile

        layout = QVBoxLayout(self)

        title = QLabel(
            "Profile"
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

        info = QFrame()

        info.setObjectName(
            "adminCard"
        )

        form = QFormLayout(info)

        self.name = QLineEdit(
            profile.get("name", "")
        )

        form.addRow(
            "Profile Name:",
            self.name
        )

        layout.addWidget(
            info
        )

        save = QPushButton(
            "Save Profile"
        )

        save.clicked.connect(
            self.save_profile
        )

        layout.addWidget(
            save
        )

        rename = QPushButton(
            "Rename Profile"
        )

        rename.clicked.connect(
            self.rename
        )

        layout.addWidget(
            rename
        )

        delete = QPushButton(
            "Delete Profile"
        )

        delete.clicked.connect(
            self.delete
        )

        layout.addWidget(
            delete
        )

        layout.addStretch()

    def save_profile(self):

        name = self.name.text().strip()

        if not name:

            QMessageBox.warning(
                self,
                "Profile",
                "Profile name cannot be empty."
            )

            return

        db.rename_profile(
            self.profile["id"],
            name
        )

        self.profile["name"] = name

        QMessageBox.information(
            self,
            "Profile",
            "Profile saved."
        )

        self.changed.emit()

    def rename(self):

        name, ok = QInputDialog.getText(
            self,
            "Rename Profile",
            "New profile name:",
            text=self.profile.get(
                "name",
                ""
            )
        )

        if not ok:
            return

        name = name.strip()

        if not name:
            return

        db.rename_profile(
            self.profile["id"],
            name
        )

        self.profile["name"] = name

        self.name.setText(name)

        self.changed.emit()

    def delete(self):

        profiles = db.get_profiles(
            self.user["id"]
        )

        if len(profiles) <= 1:

            QMessageBox.warning(
                self,
                "Profile",
                "You must keep at least one profile."
            )

            return

        answer = QMessageBox.question(
            self,
            "Delete Profile",
            "Delete this profile and its personal data?"
        )

        if answer != QMessageBox.Yes:
            return

        db.delete_profile(
            self.profile["id"]
        )

        QMessageBox.information(
            self,
            "Profile",
            "Profile deleted."
        )

        self.changed.emit()


# ==============================================================
# MOVIE DIALOG
# ==============================================================
