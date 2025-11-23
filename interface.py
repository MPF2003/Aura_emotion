# interface.py — Aura Emotion Engine GUI with Aura effect
import sys
import time
from collections import Counter
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QTimer
import cv2

from webcam_manager import WebcamManager
from emotion_analysis import EmotionAnalyzer
from spotify_player import SpotifyPlayer

# ---------------------------
# CONFIG
# ---------------------------
CLIENT_ID = "ba3712c147094d3e8291abe866ceae2b"
CLIENT_SECRET = "9f2c96ee53c6439da9b4b7491cd4c84d"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

EMOTION_FRAMES = 5
EMOTION_DELAY = 0.5  # seconds between frames

# ---------------------------
# GLOBAL STATE
# ---------------------------
wm = WebcamManager()
ea = EmotionAnalyzer()
spotify = SpotifyPlayer(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

current_emotion = "None"
current_track = "None"

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------


def detect_dominant_emotion():
    """Capture multiple frames and return the most frequent emotion."""
    emotions = []
    for _ in range(EMOTION_FRAMES):
        ok, frame = wm.get_frame()
        if not ok:
            continue
        data = ea.analyze(frame)
        if data:
            emotions.append(data["emotion"])
        time.sleep(EMOTION_DELAY)
    if emotions:
        return Counter(emotions).most_common(1)[0][0]
    return None


def update_track_info():
    """Update current track info from Spotify."""
    global current_track
    try:
        current = spotify.sp.current_playback()
        if current and current.get("item"):
            track_name = current["item"]["name"]
            artist_name = ", ".join([a["name"]
                                    for a in current["item"]["artists"]])
            current_track = f"{track_name} - {artist_name}"
        else:
            current_track = "No track playing"
    except:
        current_track = "Error getting track info"

# ---------------------------
# GUI CLASS
# ---------------------------


class AuraInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aura Emotion Engine")
        self.resize(700, 600)

        # Widgets
        self.label_video = QLabel(self)
        self.label_emotion = QLabel("Emotion: None", self)
        self.label_track = QLabel("Track: None", self)

        self.btn_play_pause = QPushButton("Play / Pause", self)
        self.btn_prev = QPushButton("Previous", self)
        self.btn_next = QPushButton("Next (Emotion)", self)

        # Layouts
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_prev)
        button_layout.addWidget(self.btn_play_pause)
        button_layout.addWidget(self.btn_next)

        layout = QVBoxLayout()
        layout.addWidget(self.label_video)
        layout.addWidget(self.label_emotion)
        layout.addWidget(self.label_track)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Signals
        self.btn_play_pause.clicked.connect(self.toggle_play_pause)
        self.btn_prev.clicked.connect(self.previous_track)
        self.btn_next.clicked.connect(self.next_track_emotion)

        # Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~30 FPS

        self.track_timer = QTimer()
        self.track_timer.timeout.connect(self.update_track_label)
        self.track_timer.start(5000)  # Update every 5 sec

    # ---------------------------
    # Webcam feed with Aura overlay
    def update_frame(self):
        ok, frame = wm.get_frame()
        if ok:
            # Determine aura color based on current emotion
            color_map = {
                "happy": (0, 255, 255),       # yellow/cyan-ish
                "sad": (255, 0, 0),           # blue
                "angry": (0, 0, 255),         # red
                "surprise": (0, 255, 255),    # white/yellow
                "neutral": (128, 128, 128),   # gray
            }
            # default dark gray
            color = color_map.get(current_emotion, (50, 50, 50))

            # Create aura overlay
            overlay = frame.copy()
            alpha = 0.25  # transparency
            overlay[:] = color
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            # Convert to QImage and display
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            self.label_video.setPixmap(pixmap)

            # Update emotion label
            self.label_emotion.setText(f"Emotion: {current_emotion}")

    # Update Spotify track info
    def update_track_label(self):
        update_track_info()
        self.label_track.setText(f"Track: {current_track}")

    # ---------------------------
    # Spotify Controls
    def toggle_play_pause(self):
        try:
            current = spotify.sp.current_playback()
            if current and current.get("is_playing"):
                spotify.pause()
            else:
                spotify.sp.start_playback()
        except Exception as e:
            print("Play/Pause error:", e)

    def previous_track(self):
        try:
            spotify.sp.previous_track()
        except Exception as e:
            print("Previous track error:", e)

    def next_track_emotion(self):
        """Next track button triggers emotion detection first."""
        global current_emotion
        print("Next button pressed → detecting emotion...")
        emotion = detect_dominant_emotion()
        if emotion:
            print(f"Detected emotion: {emotion}")
            current_emotion = emotion
            spotify.play_for_emotion(emotion)
        else:
            print("No face/emotion detected → skip to next track")
            try:
                spotify.sp.next_track()
            except Exception as e:
                print("Next track error:", e)


# ---------------------------
# RUN GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AuraInterface()
    gui.show()
    sys.exit(app.exec())
