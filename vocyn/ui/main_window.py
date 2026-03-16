from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
    QApplication, QToolTip
)
from PySide6.QtCore import Qt, QSize, Signal, QPoint
from PySide6.QtGui import QFont, QIcon, QColor, QCursor

from vocyn.config import config


# Dark theme palette based on screenshots
STYLESHEET = """
QMainWindow {
    background-color: #121212;
}
QWidget {
    background-color: transparent;
    color: #E0E0E0;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QFrame#card {
    background-color: #1E1E1E;
    border-radius: 8px;
    border: 1px solid #2C2C2C;
}
QPushButton {
    background-color: #2C2C2C;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #383838;
}
QPushButton#action_btn {
    background-color: #E0E0E0;
    color: #121212;
}
QPushButton#action_btn:hover {
    background-color: #FFFFFF;
}
QLabel#h1 {
    font-size: 18px;
    font-weight: bold;
    color: #FFFFFF;
}
QLabel#h2 {
    font-size: 14px;
    color: #A0A0A0;
    margin-bottom: 8px;
}
QLabel#metric_val {
    font-size: 16px;
    font-weight: bold;
}
QLabel#metric_lbl {
    font-size: 11px;
    color: #808080;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #121212;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #383838;
    min-height: 20px;
    border-radius: 4px;
}
"""

class ClickableLabel(QLabel):
    clicked = Signal(str)

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setWordWrap(True)
        self.setStyleSheet("""
            QLabel {
                color: #E0E0E0; 
                font-size: 13px; 
                margin: 4px 0px;
                padding: 4px;
                border-radius: 4px;
            }
            QLabel:hover {
                background-color: #2C2C2C;
                color: #FFFFFF;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.text())

class MainWindow(QMainWindow):
    dictation_toggled = Signal()
    settings_requested = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vocyn")
        self.setMinimumSize(800, 500)
        self.setStyleSheet(STYLESHEET)
        
        self.recent_transcriptions = []
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Sidebar ---
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #0A0A0A; border-right: 1px solid #2C2C2C;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # Sidebar branding
        title_lbl = QLabel("Vocyn")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; padding-left: 10px; color: #FFFFFF;")
        sidebar_layout.addWidget(title_lbl)
        
        sidebar_layout.addSpacing(20)
        
        # Sidebar buttons
        self.btn_dashboard = self.create_nav_button("Dashboard", active=True)
        self.btn_settings = self.create_nav_button("Settings")
        self.btn_settings.clicked.connect(self.settings_requested.emit)
        
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addStretch()
        
        # --- Main Content Area ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Header
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        lbl_h1 = QLabel("System Status")
        lbl_h1.setObjectName("h1")
        lbl_h2 = QLabel("Monitor and control the transcription engine.")
        lbl_h2.setObjectName("h2")
        
        header_layout.addWidget(lbl_h1)
        header_layout.addWidget(lbl_h2)
        content_layout.addWidget(header_widget)
        
        # Control Card (Status & Stop/Start)
        self.card_control = QFrame()
        self.card_control.setObjectName("card")
        self.card_control.setFixedHeight(80)
        card_control_layout = QHBoxLayout(self.card_control)
        card_control_layout.setContentsMargins(20, 20, 20, 20)
        
        self.lbl_status_dot = QLabel("●")
        self.lbl_status_dot.setStyleSheet("color: #4CAF50; font-size: 18px;")
        
        status_text_layout = QVBoxLayout()
        self.lbl_status_title = QLabel("Engine Idle")
        self.lbl_status_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.lbl_status_desc = QLabel(f"Ready on {config.get('audio_device')}")
        self.lbl_status_desc.setStyleSheet("color: #808080; font-size: 12px;")
        status_text_layout.addWidget(self.lbl_status_title)
        status_text_layout.addWidget(self.lbl_status_desc)
        
        self.btn_toggle = QPushButton("Start Dictation")
        self.btn_toggle.setObjectName("action_btn")
        self.btn_toggle.setFixedWidth(120)
        self.btn_toggle.clicked.connect(self.dictation_toggled.emit)
        
        card_control_layout.addWidget(self.lbl_status_dot)
        card_control_layout.addSpacing(10)
        card_control_layout.addLayout(status_text_layout)
        card_control_layout.addStretch()
        card_control_layout.addWidget(self.btn_toggle)
        
        content_layout.addWidget(self.card_control)
        
        # Metrics Cards
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)
        
        self.card_lang = self.create_metric_card("Language", "Auto / English")
        self.card_mode = self.create_metric_card("Transcription Mode", "Loading...")
        self.card_device = self.create_metric_card("Audio Device", "Initializing...")
        
        metrics_layout.addWidget(self.card_lang)
        metrics_layout.addWidget(self.card_mode)
        metrics_layout.addWidget(self.card_device)
        content_layout.addLayout(metrics_layout)
        
        # Recent Transcriptions
        self.card_history = QFrame()
        self.card_history.setObjectName("card")
        history_layout = QVBoxLayout(self.card_history)
        history_layout.setContentsMargins(20, 20, 20, 20)
        
        header_history_layout = QHBoxLayout()
        header_history_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_history_title = QLabel("RECENT TRANSCRIPTIONS")
        lbl_history_title.setStyleSheet("color: #606060; font-size: 10px; font-weight: bold;")
        
        self.btn_clear_history = QPushButton("Clear")
        self.btn_clear_history.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #808080;
                font-size: 11px;
                padding: 2px 8px;
            }
            QPushButton:hover {
                color: #E0E0E0;
                background-color: #2C2C2C;
            }
        """)
        self.btn_clear_history.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_clear_history.clicked.connect(self.clear_transcriptions)
        
        header_history_layout.addWidget(lbl_history_title)
        header_history_layout.addStretch()
        header_history_layout.addWidget(self.btn_clear_history)
        
        history_layout.addLayout(header_history_layout)
        history_layout.addSpacing(10)
        
        self.history_list_layout = QVBoxLayout()
        self.history_list_layout.setAlignment(Qt.AlignTop)
        self.history_list_layout.setSpacing(15)
        
        history_widget = QWidget()
        history_widget.setLayout(self.history_list_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(history_widget)
        
        history_layout.addWidget(scroll)
        
        content_layout.addWidget(self.card_history)
        
        # Combine Sidebar and Content
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area, 1) # stretch factor 1
        
        self.setCentralWidget(central_widget)
        self.update_config_display()

    def create_nav_button(self, text, active=False):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 10px 15px;
                background-color: {'#1A1A1A' if active else 'transparent'};
                border-radius: 6px;
                color: {'#FFFFFF' if active else '#A0A0A0'};
                font-weight: {'bold' if active else 'normal'};
            }}
            QPushButton:hover {{
                background-color: #2C2C2C;
                color: #FFFFFF;
            }}
            QPushButton:checked {{
                background-color: #262626;
                color: #FFFFFF;
            }}
        """)
        return btn
        
    def create_metric_card(self, title, initial_value):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(80)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("metric_lbl")
        
        lbl_value = QLabel(initial_value)
        lbl_value.setObjectName("metric_val")
        
        layout.addWidget(lbl_title)
        layout.addStretch()
        layout.addWidget(lbl_value)
        
        # Store a dynamic property to easily update it later
        card.val_label = lbl_value 
        return card

    def update_config_display(self):
        lang = config.get("language", "auto").capitalize()
        if config.get("translate"):
            lang += " (Translated)"
        self.card_lang.val_label.setText(lang)
        
        mode = config.get("model", "tiny").capitalize()
        self.card_mode.val_label.setText(mode)
        
        device = config.get("audio_device", "Default")
        self.card_device.val_label.setText(device)
        
        self.lbl_status_desc.setText(f"Listening on {config.get('audio_device')} • Hotkey: {config.get('hotkey').upper()}")
        
    def set_status(self, status):
        """Update UI based on dictation service status."""
        self.lbl_status_title.setText(f"Engine {status}")
        
        if status == "Listening":
            self.lbl_status_dot.setStyleSheet("color: #F44336; font-size: 18px;") # Red
            self.btn_toggle.setText("Stop Dictation")
        elif status == "Processing":
            self.lbl_status_dot.setStyleSheet("color: #2196F3; font-size: 18px;") # Blue
            self.btn_toggle.setText("Stop Dictation")
        else: # Idle / Loading Error
            self.lbl_status_dot.setStyleSheet("color: #4CAF50; font-size: 18px;") # Green
            self.btn_toggle.setText("Start Dictation")
            
        if "Loading" in status:
            self.lbl_status_dot.setStyleSheet("color: #FFC107; font-size: 18px;") # Yellow

    def add_transcription(self, text):
        """Adds a phrase to the recent transcriptions list."""
        if not text or not text.strip():
            return
            
        self.recent_transcriptions.insert(0, text)
        # Keep only the last 20 transcriptions to save memory
        if len(self.recent_transcriptions) > 20:
            self.recent_transcriptions = self.recent_transcriptions[:20]
            
        self.refresh_history_ui()

    def refresh_history_ui(self):
        """Rebuilds the history list UI."""
        # Clear existing items
        while self.history_list_layout.count():
            item = self.history_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for t in self.recent_transcriptions:
            lbl = ClickableLabel(t)
            lbl.clicked.connect(self.copy_to_clipboard)
            self.history_list_layout.addWidget(lbl)
            
            # Add separation line
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet("border-top: 1px solid #2C2C2C;")
            self.history_list_layout.addWidget(line)

    def copy_to_clipboard(self, text):
        """Copies text to clipboard and shows feedback."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # Show a "Copied!" tooltip at the cursor position
        QToolTip.showText(QCursor.pos(), "Copied to clipboard!", msecShowTime=1500)

    def clear_transcriptions(self):
        """Clears all recent transcriptions."""
        self.recent_transcriptions = []
        self.refresh_history_ui()
