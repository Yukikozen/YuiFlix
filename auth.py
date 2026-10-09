# YuiFlix V11 - Authentication

from common import *
from database import db

class LoginPage(QWidget):

    logged_in = Signal(dict)

    register_requested = Signal()

    def __init__(self):
        super().__init__()

        outer = QVBoxLayout(self)

        outer.addStretch()

        box = QFrame()

        box.setFixedWidth(400)

        layout = QVBoxLayout(box)

        title = QLabel("YuiFlix")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet(
            """
            color:#e50914;
            font-size:40px;
            font-weight:bold;
            """
        )

        layout.addWidget(title)

        subtitle = QLabel(
            "Sign in to continue"
        )

        subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(subtitle)

        self.username = QLineEdit()
        self.username.setPlaceholderText(
            "Username"
        )

        self.password = QLineEdit()
        self.password.setPlaceholderText(
            "Password"
        )
        self.password.setEchoMode(
            QLineEdit.Password
        )

        layout.addWidget(self.username)
        layout.addWidget(self.password)

        login = QPushButton("Sign In")

        login.setStyleSheet(
            """
            background:#e50914;
            font-weight:bold;
            """
        )

        login.clicked.connect(
            self.do_login
        )

        layout.addWidget(login)

        register = QPushButton(
            "Create Account"
        )

        register.clicked.connect(
            self.register_requested.emit
        )

        layout.addWidget(register)

        demo = QLabel(
            "Demo: demo / demo123\n"
            "Admin: admin / admin123"
        )

        demo.setAlignment(Qt.AlignCenter)

        demo.setStyleSheet(
            "color:#888888;"
        )

        layout.addWidget(demo)

        outer.addWidget(
            box,
            alignment=Qt.AlignCenter
        )

        outer.addStretch()

        self.password.returnPressed.connect(
            self.do_login
        )

    def do_login(self):

        username = self.username.text().strip()
        password = self.password.text()

        if not username or not password:

            QMessageBox.warning(
                self,
                "Login",
                "Please enter username and password."
            )

            return

        user = db.authenticate(
            username,
            password
        )

        if not user:

            QMessageBox.warning(
                self,
                "Login Failed",
                "Invalid username or password."
            )

            return

        self.logged_in.emit(user)


# ==============================================================
# REGISTER
# ==============================================================

class RegisterDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle(
            "Create Account"
        )

        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(
            QLineEdit.Password
        )

        self.confirm = QLineEdit()
        self.confirm.setEchoMode(
            QLineEdit.Password
        )

        self.profile = QLineEdit()
        self.profile.setText("My Profile")

        form.addRow(
            "Username:",
            self.username
        )

        form.addRow(
            "Password:",
            self.password
        )

        form.addRow(
            "Confirm:",
            self.confirm
        )

        form.addRow(
            "Profile:",
            self.profile
        )

        layout.addLayout(form)

        buttons = QHBoxLayout()

        cancel = QPushButton("Cancel")
        cancel.clicked.connect(
            self.reject
        )

        create = QPushButton("Create")
        create.clicked.connect(
            self.create
        )

        buttons.addWidget(cancel)
        buttons.addWidget(create)

        layout.addLayout(buttons)

    def create(self):

        username = self.username.text().strip()
        password = self.password.text()
        confirm = self.confirm.text()
        profile_name = self.profile.text().strip()

        if not username or not password:

            QMessageBox.warning(
                self,
                "Register",
                "Username and password are required."
            )

            return

        if password != confirm:

            QMessageBox.warning(
                self,
                "Register",
                "Passwords do not match."
            )

            return

        existing = db.fetchone(
            """
            SELECT id
            FROM users
            WHERE username=?
            """,
            (username,)
        )

        if existing:

            QMessageBox.warning(
                self,
                "Register",
                "Username already exists."
            )

            return

        cursor = db.execute(
            """
            INSERT INTO users
            (username,password,is_admin,created_at)
            VALUES (?,?,?,?)
            """,
            (
                username,
                hash_password(password),
                0,
                now(),
            )
        )

        db.add_profile(
            cursor.lastrowid,
            profile_name or "My Profile"
        )

        QMessageBox.information(
            self,
            "Register",
            "Account created successfully."
        )

        self.accept()


# ==============================================================
# PROFILE SELECTOR
# ==============================================================
