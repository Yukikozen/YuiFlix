# YuiFlix V11 - Video Player

from common import *
from database import db

class ClickableVideoWidget(QVideoWidget):

    doubleClicked = Signal()

    def mouseDoubleClickEvent(self, event):

        self.doubleClicked.emit()

        super().mouseDoubleClickEvent(
            event
        )


# ==============================================================
# VIDEO PLAYER
# ==============================================================

class VideoPlayer(QMainWindow):

    closed = Signal()

    def __init__(
        self,
        movie,
        profile,
        user,
        movies,
        parent=None
    ):

        super().__init__(parent)

        self.movie = movie
        self.profile = profile
        self.user = user
        self.movies = movies

        self.current_index = 0

        for index, item in enumerate(
            movies
        ):

            if item["id"] == movie["id"]:

                self.current_index = index
                break

        self.manual_close = False
        self.up_next_cancelled = False
        self.view_recorded = False

        self.setWindowTitle(
            f'YuiFlix - {movie.get("title","")}'
        )

        self.showMaximized()

        self.media_player = QMediaPlayer(
            self
        )

        self.audio_output = QAudioOutput(
            self
        )

        self.audio_output.setVolume(
            0.8
        )

        self.media_player.setAudioOutput(
            self.audio_output
        )

        self.video_widget = ClickableVideoWidget()

        self.media_player.setVideoOutput(
            self.video_widget
        )

        self.video_widget.doubleClicked.connect(
            self.toggle_fullscreen
        )

        central = QWidget()

        self.central = central

        root = QVBoxLayout(central)

        root.setContentsMargins(
            0,
            0,
            0,
            0
        )

        root.setSpacing(0)

        root.addWidget(
            self.video_widget,
            1
        )

        self.controls = QFrame()

        controls_layout = QVBoxLayout(
            self.controls
        )

        controls_layout.setContentsMargins(
            10,
            5,
            10,
            8
        )

        self.progress = QSlider(
            Qt.Horizontal
        )

        self.progress.sliderMoved.connect(
            self.seek
        )

        controls_layout.addWidget(
            self.progress
        )

        row = QHBoxLayout()

        self.play_button = QPushButton(
            "▶"
        )

        self.play_button.clicked.connect(
            self.toggle_play
        )

        row.addWidget(
            self.play_button
        )

        back = QPushButton(
            "↶ 10s"
        )

        back.clicked.connect(
            lambda:
            self.seek_relative(-10)
        )

        row.addWidget(back)

        forward = QPushButton(
            "10s ↷"
        )

        forward.clicked.connect(
            lambda:
            self.seek_relative(10)
        )

        row.addWidget(forward)

        self.time_label = QLabel(
            "0:00 / 0:00"
        )

        row.addWidget(
            self.time_label
        )

        row.addStretch()

        self.speed = QComboBox()

        self.speed.addItems([
            "0.5x",
            "0.75x",
            "1.0x",
            "1.25x",
            "1.5x",
            "2.0x",
        ])

        self.speed.setCurrentText(
            "1.0x"
        )

        self.speed.currentTextChanged.connect(
            self.change_speed
        )

        row.addWidget(
            self.speed
        )

        self.volume = QSlider(
            Qt.Horizontal
        )

        self.volume.setRange(
            0,
            100
        )

        self.volume.setValue(
            80
        )

        self.volume.setFixedWidth(
            100
        )

        self.volume.valueChanged.connect(
            self.change_volume
        )

        row.addWidget(
            self.volume
        )

        mute = QPushButton(
            "🔊"
        )

        mute.clicked.connect(
            self.toggle_mute
        )

        self.mute_button = mute

        row.addWidget(mute)

        full = QPushButton(
            "⛶"
        )

        full.clicked.connect(
            self.toggle_fullscreen
        )

        row.addWidget(full)

        close = QPushButton(
            "✕"
        )

        close.clicked.connect(
            self.close
        )

        row.addWidget(close)

        controls_layout.addLayout(
            row
        )

        root.addWidget(
            self.controls
        )

        self.setCentralWidget(
            central
        )

        # ------------------------------------------------------
        # TITLE OVERLAY
        # ------------------------------------------------------

        self.title_label = QLabel(
            movie.get("title", "")
        )

        self.title_label.setStyleSheet(
            """
            background:rgba(0,0,0,170);
            padding:12px 20px;
            font-size:22px;
            font-weight:bold;
            """
        )

        self.title_label.setParent(
            central
        )

        self.title_label.move(
            25,
            25
        )

        self.title_label.adjustSize()

        # ------------------------------------------------------
        # UP NEXT OVERLAY
        # ------------------------------------------------------

        self.up_next = QFrame(
            central
        )

        self.up_next.setObjectName(
            "upNext"
        )

        self.up_next.setFixedSize(
            400,
            210
        )

        up_layout = QVBoxLayout(
            self.up_next
        )

        label = QLabel(
            "Up Next"
        )

        label.setStyleSheet(
            "font-size:20px;font-weight:bold;"
        )

        label.setAlignment(
            Qt.AlignCenter
        )

        up_layout.addWidget(label)

        self.next_title = QLabel()

        self.next_title.setAlignment(
            Qt.AlignCenter
        )

        self.next_title.setWordWrap(True)

        self.next_title.setStyleSheet(
            "font-size:17px;"
        )

        up_layout.addWidget(
            self.next_title
        )

        self.countdown_label = QLabel()

        self.countdown_label.setAlignment(
            Qt.AlignCenter
        )

        self.countdown_label.setStyleSheet(
            """
            color:#e50914;
            font-size:30px;
            font-weight:bold;
            """
        )

        up_layout.addWidget(
            self.countdown_label
        )

        buttons = QHBoxLayout()

        play_now = QPushButton(
            "Play Now"
        )

        play_now.clicked.connect(
            self.play_next_now
        )

        cancel = QPushButton(
            "Cancel"
        )

        cancel.clicked.connect(
            self.cancel_up_next
        )

        buttons.addWidget(
            play_now
        )

        buttons.addWidget(
            cancel
        )

        up_layout.addLayout(
            buttons
        )

        self.up_next.hide()

        # ------------------------------------------------------

        self.progress_timer = QTimer(self)

        self.progress_timer.timeout.connect(
            self.update_progress
        )

        self.progress_timer.start(
            1000
        )

        self.save_timer = QTimer(self)

        self.save_timer.timeout.connect(
            self.save_current_progress
        )

        self.save_timer.start(
            5000
        )

        self.up_next_timer = QTimer(self)

        self.up_next_timer.timeout.connect(
            self.countdown_tick
        )

        self.countdown = 10

        self.media_player.durationChanged.connect(
            self.duration_changed
        )

        self.media_player.positionChanged.connect(
            self.position_changed
        )

        self.media_player.playbackStateChanged.connect(
            self.state_changed
        )

        self.media_player.mediaStatusChanged.connect(
            self.media_status_changed
        )

        self.play_movie(
            movie
        )

        # ------------------------------------------------------
        # SHORTCUTS
        # ------------------------------------------------------

        QShortcut(
            QKeySequence("Space"),
            self,
            activated=self.toggle_play
        )

        QShortcut(
            QKeySequence("Left"),
            self,
            activated=lambda:
            self.seek_relative(-10)
        )

        QShortcut(
            QKeySequence("Right"),
            self,
            activated=lambda:
            self.seek_relative(10)
        )

        QShortcut(
            QKeySequence("N"),
            self,
            activated=self.play_next
        )

        QShortcut(
            QKeySequence("P"),
            self,
            activated=self.play_previous
        )

        QShortcut(
            QKeySequence("F"),
            self,
            activated=self.toggle_fullscreen
        )

        QShortcut(
            QKeySequence("M"),
            self,
            activated=self.toggle_mute
        )

        QShortcut(
            QKeySequence("Escape"),
            self,
            activated=self.handle_escape
        )

    # ----------------------------------------------------------

    def play_movie(self, movie):

        self.movie = movie

        self.title_label.setText(
            movie.get("title", "")
        )

        self.title_label.adjustSize()

        self.setWindowTitle(
            f'YuiFlix - {movie.get("title","")}'
        )

        self.current_index = 0

        for index, item in enumerate(
            self.movies
        ):

            if item["id"] == movie["id"]:

                self.current_index = index
                break

        video_path = asset_path(
            VIDEO_DIR,
            movie.get("video", "")
        )

        if not video_path:

            QMessageBox.warning(
                self,
                "Video Missing",
                "The video file could not be found."
            )

            self.close()

            return

        history = db.get_history_movie(
            self.profile["id"],
            movie["id"]
        )

        self.media_player.setSource(
            QUrl.fromLocalFile(
                video_path
            )
        )

        self.media_player.play()

        if history:

            duration = safe_float(
                history.get("duration")
            )

            progress = safe_float(
                history.get("progress")
            )

            if duration > 0 and progress > 5:

                QTimer.singleShot(
                    500,
                    lambda:
                    self.media_player.setPosition(
                        int(progress * 1000)
                    )
                )

        if not self.view_recorded:

            db.add_view(
                self.profile["id"],
                self.user["id"],
                movie["id"]
            )

            self.view_recorded = True

        self.hide_up_next()

    # ----------------------------------------------------------

    def duration_changed(self, duration):

        self.progress.setRange(
            0,
            max(0, duration)
        )

    # ----------------------------------------------------------

    def position_changed(self, position):

        if not self.progress.isSliderDown():

            self.progress.setValue(
                position
            )

        duration = self.media_player.duration()

        self.time_label.setText(
            f"{format_time(position / 1000)} / "
            f"{format_time(duration / 1000)}"
        )

    # ----------------------------------------------------------

    def update_progress(self):

        duration = self.media_player.duration()
        position = self.media_player.position()

        if duration <= 0:
            return

        remaining = duration - position

        if (
            remaining <= 15000
            and remaining > 0
            and not self.up_next_cancelled
        ):

            self.show_up_next()

    # ----------------------------------------------------------

    def show_up_next(self):

        next_movie = self.get_next_movie()

        if not next_movie:
            return

        if self.up_next.isVisible():
            return

        self.countdown = 10

        self.next_title.setText(
            next_movie.get(
                "title",
                "Next Movie"
            )
        )

        self.countdown_label.setText(
            f"Playing in {self.countdown}"
        )

        self.position_up_next()

        self.up_next.show()

        self.up_next.raise_()

        self.up_next_timer.start(
            1000
        )

    # ----------------------------------------------------------

    def position_up_next(self):

        x = (
            self.width()
            - self.up_next.width()
            - 30
        )

        y = (
            self.height()
            - self.up_next.height()
            - self.controls.height()
            - 30
        )

        self.up_next.move(
            max(10, x),
            max(10, y)
        )

    # ----------------------------------------------------------

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self.title_label.move(
            25,
            25
        )

        self.position_up_next()

    # ----------------------------------------------------------

    def countdown_tick(self):

        if not self.up_next.isVisible():

            self.up_next_timer.stop()

            return

        self.countdown -= 1

        self.countdown_label.setText(
            f"Playing in {self.countdown}"
        )

        if self.countdown <= 0:

            self.up_next_timer.stop()

            self.play_next_now()

    # ----------------------------------------------------------

    def play_next_now(self):

        self.up_next_timer.stop()

        self.hide_up_next()

        self.up_next_cancelled = False

        self.play_next()

    # ----------------------------------------------------------

    def cancel_up_next(self):

        self.up_next_cancelled = True

        self.hide_up_next()

    # ----------------------------------------------------------

    def hide_up_next(self):

        self.up_next_timer.stop()

        self.up_next.hide()

    # ----------------------------------------------------------

    def get_next_movie(self):

        if (
            self.current_index + 1
            >= len(self.movies)
        ):

            return None

        return self.movies[
            self.current_index + 1
        ]

    # ----------------------------------------------------------

    def get_previous_movie(self):

        if self.current_index <= 0:

            return None

        return self.movies[
            self.current_index - 1
        ]

    # ----------------------------------------------------------

    def play_next(self):

        movie = self.get_next_movie()

        if not movie:

            return

        self.up_next_cancelled = False

        self.play_movie(
            movie
        )

    # ----------------------------------------------------------

    def play_previous(self):

        movie = self.get_previous_movie()

        if not movie:

            return

        self.play_movie(
            movie
        )

    # ----------------------------------------------------------

    def toggle_play(self):

        if (
            self.media_player.playbackState()
            == QMediaPlayer.PlayingState
        ):

            self.media_player.pause()

        else:

            self.media_player.play()

    # ----------------------------------------------------------

    def state_changed(self, state):

        if state == QMediaPlayer.PlayingState:

            self.play_button.setText(
                "⏸"
            )

        else:

            self.play_button.setText(
                "▶"
            )

    # ----------------------------------------------------------

    def seek(self, position):

        self.media_player.setPosition(
            position
        )

    # ----------------------------------------------------------

    def seek_relative(self, seconds):

        position = self.media_player.position()

        self.media_player.setPosition(
            max(
                0,
                position + seconds * 1000
            )
        )

    # ----------------------------------------------------------

    def change_speed(self, text):

        speed = safe_float(
            text.replace("x", "")
        )

        if speed <= 0:
            speed = 1.0

        self.media_player.setPlaybackRate(
            speed
        )

    # ----------------------------------------------------------

    def change_volume(self, value):

        self.audio_output.setVolume(
            value / 100
        )

    # ----------------------------------------------------------

    def toggle_mute(self):

        muted = self.audio_output.isMuted()

        self.audio_output.setMuted(
            not muted
        )

        self.mute_button.setText(
            "🔇"
            if not muted
            else "🔊"
        )

    # ----------------------------------------------------------

    def toggle_fullscreen(self):

        if self.isFullScreen():

            self.showMaximized()

        else:

            self.showFullScreen()

    # ----------------------------------------------------------

    def handle_escape(self):

        if self.isFullScreen():

            self.showMaximized()

        else:

            self.close()

    # ----------------------------------------------------------

    def media_status_changed(self, status):

        if status == QMediaPlayer.EndOfMedia:

            if (
                not self.up_next_cancelled
                and self.get_next_movie()
            ):

                self.play_next()

    # ----------------------------------------------------------

    def save_current_progress(self):

        if not self.movie:
            return

        duration = self.media_player.duration()

        position = self.media_player.position()

        if duration <= 0:
            return

        db.save_progress(
            self.profile["id"],
            self.user["id"],
            self.movie["id"],
            position / 1000,
            duration / 1000
        )

    # ----------------------------------------------------------

    def closeEvent(self, event):

        self.save_current_progress()

        self.progress_timer.stop()
        self.save_timer.stop()
        self.up_next_timer.stop()

        self.media_player.stop()

        self.manual_close = True

        self.closed.emit()

        event.accept()


# ==============================================================
# PROFILE PAGE
# ==============================================================
