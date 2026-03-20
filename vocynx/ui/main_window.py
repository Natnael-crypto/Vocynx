from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
    QApplication, QToolTip, QStackedWidget, QGraphicsDropShadowEffect,
    QToolButton, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QSize, Signal, QPoint, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont, QIcon, QColor, QCursor, QPixmap, QPainter, QPainterPath
import os
import sys
from datetime import datetime

def get_asset_path(filename):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'vocynx', 'assets', filename)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", filename)

from vocynx.config import config
from vocynx.ui.settings_view import SettingsView
from vocynx.ui.licenses_view import LicensesView
from vocynx.ui.about_view import AboutView


# ─── Light Theme Colors (from NewUI index.css :root) ─────────────────────────
C_BG         = "#F8F9FC"   # cool light background
C_FG         = "#221F1C"   # dark brown foreground
C_CARD       = "#FFFFFF"   # white cards
C_CARD_FG    = "#221F1C"
C_PRIMARY    = "#221F1C"   # dark brown primary (buttons, active nav)
C_PRIMARY_FG = "#FAF8F5"   # light text on primary
C_SECONDARY  = "#F5EDCF"   # warm yellow (banner, highlights)
C_SEC_FG     = "#221F1C"
C_MUTED      = "#F2EFE9"   # light muted background
C_MUTED_FG   = "#857F79"   # muted text / secondary text
C_BORDER     = "#E9E4DD"   # subtle warm border
C_ACCENT     = "#F5EDCF"   # warm yellow accent
C_INPUT      = "#E9E4DD"   # input borders


STYLESHEET = f"""
QMainWindow {{
    background-color: {C_BG};
}}
QWidget#centralwidget {{
    background-color: {C_BG};
}}
QWidget {{
    color: {C_FG};
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}}
QFrame#card {{
    background-color: {C_CARD};
    border-radius: 12px;
    border: 1px solid {C_BORDER};
}}
QPushButton {{
    background-color: {C_MUTED};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    color: {C_FG};
    font-family: 'Inter', 'Segoe UI', sans-serif;
}}
QPushButton:hover {{
    background-color: {C_BORDER};
}}
QPushButton#action_btn {{
    background-color: {C_PRIMARY};
    color: {C_PRIMARY_FG};
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 13px;
}}
QPushButton#action_btn:hover {{
    background-color: #3A3630;
}}
QLabel#h1 {{
    font-size: 22px;
    font-weight: 700;
    color: {C_FG};
}}
QLabel#h2 {{
    font-size: 12px;
    color: {C_MUTED_FG};
    font-weight: 600;
    letter-spacing: 1px;
}}
QScrollArea {{
    border: none;
    background-color: transparent;
}}
QScrollBar:vertical {{
    border: none;
    background: {C_BG};
    width: 6px;
    border-radius: 3px;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: {C_BORDER};
    min-height: 30px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical:hover {{
    background: {C_MUTED_FG};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

class ToastNotification(QWidget):
    """A premium toast notification that fades in and out."""
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(message)
        self.label.setStyleSheet(f"""
            QLabel {{
                color: {C_PRIMARY_FG};
                background-color: {C_PRIMARY};
                border-radius: 20px;
                padding: 10px 24px;
                font-size: 13px;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
            }}
        """)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(400)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_toast)
        
    def show_toast(self):
        self.show()
        self.animation.stop()
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        self.timer.start(3000)
        
    def hide_toast(self):
        self.animation.stop()
        self.animation.setStartValue(self.opacity_effect.opacity())
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.deleteLater)
        self.animation.start()


class ActivityItemWidget(QFrame):
    """Single activity item matching the NewUI design."""
    clicked = Signal(str)
    
    def __init__(self, time_str, text, is_audio_note=False, parent=None):
        super().__init__(parent)
        self.text_content = text
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: none;
                border-bottom: 1px solid {C_BORDER};
                padding: 0px;
            }}
            QFrame:hover {{
                background-color: {C_MUTED};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 14, 0, 14)
        layout.setSpacing(14)
        
        # Time label
        lbl_time = QLabel(time_str)
        lbl_time.setStyleSheet(f"color: {C_MUTED_FG}; font-size: 12px; font-weight: 500; border: none;")
        lbl_time.setFixedWidth(65)
        layout.addWidget(lbl_time)
        
        # Text
        if is_audio_note:
            lbl_text = QLabel("🔇 Audio is silence")
            lbl_text.setStyleSheet(f"color: {C_MUTED_FG}; font-size: 13px; font-style: italic; border: none;")
        else:
            lbl_text = QLabel(text)
            lbl_text.setStyleSheet(f"color: {C_FG}; font-size: 13px; border: none;")
        lbl_text.setWordWrap(True)
        layout.addWidget(lbl_text, 1)

        # Copied Badge
        self.lbl_copied = QLabel("Copied!")
        self.lbl_copied.setStyleSheet(f"""
            QLabel {{
                background-color: {C_SECONDARY};
                color: {C_FG};
                font-size: 10px;
                font-weight: 700;
                padding: 2px 8px;
                border-radius: 10px;
                border: none;
            }}
        """)
        self.lbl_copied.hide()
        layout.addWidget(self.lbl_copied)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.show_feedback()
            self.clicked.emit(self.text_content)

    def show_feedback(self):
        self.lbl_copied.show()
        QTimer.singleShot(1200, self.lbl_copied.hide)


class StatPill(QFrame):
    """Compact stat pill for the stats bar (matching screenshot: icon + value + label in a row)."""
    def __init__(self, value, label, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {C_MUTED};
                border-radius: 16px;
                border: none;
                padding: 0px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(4)
        
        self.lbl_value = QLabel(str(value))
        self.lbl_value.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {C_FG}; border: none;")
        layout.addWidget(self.lbl_value)
    
    def set_value(self, val):
        self.lbl_value.setText(str(val))


class MainWindow(QMainWindow):
    dictation_toggled = Signal()
    settings_saved = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vocynx")
        self.setFixedSize(420, 720)
        self.setStyleSheet(STYLESHEET)
        
        self.recent_transcriptions = []
        self.transcription_count = 0
        self.session_count = 0
        
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralwidget")
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Stacked Widget ---
        self.stacked_widget = QStackedWidget()
        
        # 1. Home View
        self.home_view = QWidget()
        self.setup_home_view()
        self.stacked_widget.addWidget(self.home_view)
        
        # 2. Settings View
        self.settings_view = SettingsView()
        self.settings_view.settings_saved.connect(self.on_settings_saved)
        self.stacked_widget.addWidget(self.settings_view)
        
        # 3. Licenses View
        self.licenses_view = LicensesView()
        self.stacked_widget.addWidget(self.licenses_view)
        
        # 4. About View
        self.about_view = AboutView()
        self.stacked_widget.addWidget(self.about_view)
        
        main_layout.addWidget(self.stacked_widget)
        self.setCentralWidget(central_widget)
        
        # --- Bottom Navigation Bar ---
        self.floating_nav = QFrame(self)
        self.floating_nav.setObjectName("floating_nav")
        self.floating_nav.setStyleSheet(f"""
            QFrame#floating_nav {{
                background-color: {C_CARD};
                border: 1px solid {C_BORDER};
                border-radius: 32px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(self.floating_nav)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, -2)
        self.floating_nav.setGraphicsEffect(shadow)
        
        nav_layout = QHBoxLayout(self.floating_nav)
        nav_layout.setContentsMargins(12, 12, 12, 12)
        nav_layout.setSpacing(4)
        
        self.nav_buttons = []
        nav_items = [
            (get_asset_path("ic_home.svg"), "Home"),
            (get_asset_path("ic_settings.svg"), "Settings"),
            (get_asset_path("ic_licenses.svg"), "License"),
            (get_asset_path("ic_about.svg"), "About"),
        ]
        
        for i, (icon_path, label) in enumerate(nav_items):
            btn = self._create_nav_button(icon_path, label, active=(i == 0))
            btn.clicked.connect(lambda checked, idx=i: self.switch_view(idx))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        self.floating_nav.show()
        self.update_config_display()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        nav_width = 340
        nav_height = 68
        x = (self.width() - nav_width) // 2
        y = self.height() - nav_height - 16
        self.floating_nav.setGeometry(x, y, nav_width, nav_height)
        self.floating_nav.raise_()

    def _create_nav_button(self, icon_path, label, active=False):
        btn = QToolButton()
        btn.setText(label)
        btn.setIcon(QIcon(icon_path))
        btn.setIconSize(QSize(22, 22))
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._apply_nav_style(btn, active)
        return btn
    
    def _apply_nav_style(self, btn, active):
        if active:
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: {C_PRIMARY};
                    color: {C_PRIMARY_FG};
                    border: none;
                    border-radius: 16px;
                    padding: 4px 16px;
                    font-size: 10px;
                    font-weight: 700;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                }}
                QToolButton:hover {{
                    background-color: #3A3630;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QToolButton {{
                    background-color: transparent;
                    color: {C_MUTED_FG};
                    border: none;
                    border-radius: 16px;
                    padding: 4px 12px;
                    font-size: 10px;
                    font-weight: 500;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                }}
                QToolButton:hover {{
                    background-color: {C_MUTED};
                }}
            """)
        
    def switch_view(self, index):
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            active = (i == index)
            btn.setChecked(active)
            self._apply_nav_style(btn, active)
            
    def show_settings_view(self):
        self.switch_view(1)
        
    def on_settings_saved(self):
        self.update_config_display()
        self.settings_saved.emit()
        self.switch_view(0)
        
    # ─── Home View ────────────────────────────────────────────────────────
    def setup_home_view(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        container = QWidget()
        container.setObjectName("homeContainer")
        container.setStyleSheet(f"#homeContainer {{ background-color: {C_BG}; }}")
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(20, 40, 20, 100)
        content_layout.setSpacing(0)
        
        # ── Logo Image ──
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        logo_path = get_asset_path("logo.png")
        lbl_logo = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled = pixmap.scaledToHeight(48, Qt.SmoothTransformation)
            lbl_logo.setPixmap(scaled)
        else:
            lbl_logo.setText("Vocynx")
            lbl_logo.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {C_FG};")
        
        logo_layout.addWidget(lbl_logo)
        logo_layout.addStretch()
        content_layout.addLayout(logo_layout)
        content_layout.addSpacing(16)
        
        # ── Welcome Heading ──
        lbl_welcome = QLabel("Welcome back")
        lbl_welcome.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {C_FG}; font-family: 'Inter', sans-serif;")
        content_layout.addWidget(lbl_welcome)
        content_layout.addSpacing(16)
        
        # ── Stats Pills Bar ──
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(8)
        
        self.stat_sessions = StatPill( "1 week", "")
        self.stat_words = StatPill( "0 words", "")
        
        stats_layout.addWidget(self.stat_sessions)
        stats_layout.addWidget(self.stat_words)
        stats_layout.addStretch()
        content_layout.addLayout(stats_layout)
        content_layout.addSpacing(20)
        
        # ── Welcome Banner ──
        banner = QFrame()
        banner.setObjectName("banner")
        banner.setStyleSheet(f"""
            QFrame#banner {{
                background-color: {C_SECONDARY};
                border-radius: 16px;
                border: none;
            }}
        """)
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(20, 20, 20, 20)
        banner_layout.setSpacing(8)
        
        # Status title in banner
        self.lbl_status_title = QLabel("Engine Idle")
        self.lbl_status_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {C_FG}; font-style: italic;")
        banner_layout.addWidget(self.lbl_status_title)
        
        self.lbl_status_desc = QLabel(
            f"Vocynx adapts to how you speak. "
            f"Ready on {config.get('audio_device', 'Default Microphone')}. "
            f"Hotkey: {config.get('hotkey', 'ctrl+alt+space').upper()}"
        )
        self.lbl_status_desc.setWordWrap(True)
        self.lbl_status_desc.setStyleSheet(f"font-size: 12px; color: {C_FG}; line-height: 1.5;")
        banner_layout.addWidget(self.lbl_status_desc)
        
        banner_layout.addSpacing(8)
        
        self.btn_toggle = QPushButton("✨  Start now")
        self.btn_toggle.setObjectName("action_btn")
        self.btn_toggle.setFixedHeight(38)
        self.btn_toggle.setFixedWidth(130)
        self.btn_toggle.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_toggle.clicked.connect(self.dictation_toggled.emit)
        banner_layout.addWidget(self.btn_toggle)
        
        content_layout.addWidget(banner)
        content_layout.addSpacing(28)
        
        # ── Activity / Recent Transcriptions ──
        lbl_today = QLabel("TODAY")
        lbl_today.setObjectName("h2")
        content_layout.addWidget(lbl_today)
        content_layout.addSpacing(8)
        
        self.activity_card = QFrame()
        self.activity_card.setObjectName("card")
        self.activity_layout = QVBoxLayout(self.activity_card)
        self.activity_layout.setContentsMargins(16, 4, 16, 4)
        self.activity_layout.setSpacing(0)
        
        # Empty state
        self.lbl_empty = QLabel("No transcriptions yet.\nStart dictation to see your activity here.")
        self.lbl_empty.setStyleSheet(f"color: {C_MUTED_FG}; font-size: 13px; padding: 24px 0px;")
        self.lbl_empty.setAlignment(Qt.AlignCenter)
        self.lbl_empty.setWordWrap(True)
        self.activity_layout.addWidget(self.lbl_empty)
        
        content_layout.addWidget(self.activity_card)
        content_layout.addStretch()
        
        scroll.setWidget(container)
        
        home_layout = QVBoxLayout(self.home_view)
        home_layout.setContentsMargins(0, 0, 0, 0)
        home_layout.setSpacing(0)
        home_layout.addWidget(scroll)

    def update_config_display(self):
        device = config.get("audio_device", "Default")
        hotkey = config.get("hotkey", "ctrl+alt+space").upper()
        model = config.get("model", "tiny").capitalize()
        
        self.lbl_status_desc.setText(
            f"Vocynx adapts to how you speak. "
            f"Ready on {device}. Hotkey: {hotkey}"
        )
        
    def set_status(self, status):
        """Update UI based on dictation service status."""
        self.lbl_status_title.setText(f"Engine {status}")
        
        if status == "Listening":
            self.btn_toggle.setText(" Stop")
            self.session_count += 1
            self.stat_sessions.set_value(f"{self.session_count} sessions")
        elif status == "Processing":
            self.btn_toggle.setText("Stop")
        else:
            self.btn_toggle.setText("Start now")
            
        if "Loading" in status:
            pass

    def add_transcription(self, text):
        if not text or not text.strip():
            return
        self.recent_transcriptions.insert(0, text)
        if len(self.recent_transcriptions) > 20:
            self.recent_transcriptions = self.recent_transcriptions[:20]
        
        self.transcription_count += len(text.split())
        self.stat_words.set_value(f"{self.transcription_count} words")
        self.refresh_history_ui()

    def refresh_history_ui(self):
        while self.activity_layout.count():
            item = self.activity_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.recent_transcriptions:
            self.lbl_empty = QLabel("No transcriptions yet.\nStart dictation to see your activity here.")
            self.lbl_empty.setStyleSheet(f"color: {C_MUTED_FG}; font-size: 13px; padding: 24px 0px;")
            self.lbl_empty.setAlignment(Qt.AlignCenter)
            self.lbl_empty.setWordWrap(True)
            self.activity_layout.addWidget(self.lbl_empty)
            return
                
        now = datetime.now()
        for t in self.recent_transcriptions:
            time_str = now.strftime("%I:%M %p")
            is_silence = t.strip().lower() in ["", "audio is silence", "silence"]
            item = ActivityItemWidget(time_str, t, is_audio_note=is_silence)
            item.clicked.connect(self.copy_to_clipboard)
            self.activity_layout.addWidget(item)

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.show_toast("✓  Copied to clipboard")

    def show_toast(self, message):
        # Position toast in bottom center of the window
        toast = ToastNotification(message, self)
        toast.adjustSize()
        
        # Calculate position relative to MainWindow
        x = (self.width() - toast.width()) // 2
        y = self.height() - 110 # Above the floating nav
        
        global_pos = self.mapToGlobal(QPoint(x, y))
        toast.move(global_pos)
        toast.show_toast()

    def clear_transcriptions(self):
        self.recent_transcriptions = []
        self.refresh_history_ui()
