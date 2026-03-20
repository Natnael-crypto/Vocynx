from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor, QPixmap
import os
import sys

def get_asset_path(filename):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'vocynx', 'assets', filename)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", filename)

# ─── Light Theme Colors ──────────────────────────────────────────────────────
C_BG         = "#F8F9FC"
C_FG         = "#221F1C"
C_CARD       = "#FFFFFF"
C_SECONDARY  = "#F5EDCF"
C_MUTED      = "#F2EFE9"
C_MUTED_FG   = "#857F79"
C_BORDER     = "#E9E4DD"


class InfoRow(QFrame):
    """Key-value row for tech info / details cards."""
    def __init__(self, key, value, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background-color: transparent; border: none; }")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(0)
        
        lbl_key = QLabel(key)
        lbl_key.setStyleSheet(f"font-size: 13px; color: {C_MUTED_FG}; border: none;")
        layout.addWidget(lbl_key)
        layout.addStretch()
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {C_FG}; border: none;")
        layout.addWidget(lbl_val)


class LinkButton(QFrame):
    """Clickable link row with external link arrow."""
    def __init__(self, label, url, parent=None):
        super().__init__(parent)
        self.url = url
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: none;
                border-bottom: 1px solid {C_BORDER};
            }}
            QFrame:hover {{
                background-color: {C_MUTED};
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        
        lbl_text = QLabel(label)
        lbl_text.setStyleSheet(f"font-size: 13px; color: {C_FG}; border: none;")
        layout.addWidget(lbl_text)
        
        layout.addStretch()
        
        lbl_arrow = QLabel("↗")
        lbl_arrow.setStyleSheet(f"font-size: 12px; color: {C_MUTED_FG}; border: none;")
        layout.addWidget(lbl_arrow)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.url.startswith("mailto:"):
                from PySide6.QtWidgets import QApplication, QToolTip
                from PySide6.QtGui import QCursor
                email = self.url.replace("mailto:", "")
                QApplication.clipboard().setText(email)
                QToolTip.showText(QCursor.pos(), "Email copied to clipboard!", msecShowTime=2000)
            else:
                from PySide6.QtGui import QDesktopServices
                from PySide6.QtCore import QUrl
                QDesktopServices.openUrl(QUrl(self.url))


class AboutView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("aboutView")
        self.setStyleSheet(f"""
            QWidget#aboutView {{ 
                background-color: {C_BG}; 
            }}
            QWidget {{
                color: {C_FG}; 
                font-family: 'Inter', 'Segoe UI', sans-serif; 
            }}
            QScrollBar:vertical {{
                border: none; background: {C_BG}; width: 6px;
                border-radius: 3px; margin: 4px 2px;
            }}
            QScrollBar::handle:vertical {{ 
                background: {C_BORDER}; min-height: 30px; border-radius: 3px; 
            }}
            QScrollBar::handle:vertical:hover {{ background: {C_MUTED_FG}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet(f"#container {{ background-color: {C_BG}; }}")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 40, 20, 100)
        layout.setSpacing(0)
        
        # ── Header ──
        header = QHBoxLayout()
        header.setSpacing(8)
        lbl_h1 = QLabel("About")
        lbl_h1.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {C_FG};")
        header.addWidget(lbl_h1)
        header.addStretch()
        layout.addLayout(header)
        layout.addSpacing(24)
        
        # ── App Info Card (centered) ──
        app_card = QFrame()
        app_card.setStyleSheet(f"""
            QFrame {{
                background-color: {C_CARD};
                border-radius: 16px;
                border: none;
            }}
        """)
        app_card_layout = QVBoxLayout(app_card)
        app_card_layout.setContentsMargins(24, 24, 24, 24)
        app_card_layout.setSpacing(8)
        app_card_layout.setAlignment(Qt.AlignCenter)
        
        # Logo image
        logo_path = get_asset_path("logo.png")
        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignCenter)
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled = pixmap.scaledToHeight(64, Qt.SmoothTransformation)
            lbl_logo.setPixmap(scaled)
        else:
            lbl_logo.setText("Vocynx")
            lbl_logo.setStyleSheet(f"font-size: 32px; font-weight: 700; color: {C_FG}; border: none;")
        app_card_layout.addWidget(lbl_logo)
        
        # Badge
        badge_container = QHBoxLayout()
        badge_container.setAlignment(Qt.AlignCenter)
        lbl_badge = QLabel("Open Source")
        lbl_badge.setStyleSheet(f"""
            font-size: 10px; font-weight: 700; 
            color: {C_MUTED_FG}; 
            background-color: {C_MUTED}; 
            padding: 3px 10px; 
            border-radius: 10px;
            border: none;
        """)
        badge_container.addWidget(lbl_badge)
        app_card_layout.addLayout(badge_container)
        
        lbl_version = QLabel("Version 2.4.0")
        lbl_version.setAlignment(Qt.AlignCenter)
        lbl_version.setStyleSheet(f"font-size: 12px; color: {C_MUTED_FG}; border: none;")
        app_card_layout.addWidget(lbl_version)
        
        layout.addWidget(app_card)
        layout.addSpacing(20)
        
        # ── Description Card ──
        desc_card = QFrame()
        desc_card.setStyleSheet(f"""
            QFrame {{
                background-color: {C_CARD};
                border-radius: 12px;
                border: 1px solid {C_BORDER};
            }}
        """)
        desc_layout = QVBoxLayout(desc_card)
        desc_layout.setContentsMargins(16, 16, 16, 16)
        
        lbl_desc = QLabel(
            "Vocynx is a free, open-source voice-to-text app powered by OpenAI Whisper. "
            "Transcribe speech in real-time with optional LLM refinement no subscription, no lock-in."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(f"font-size: 13px; color: {C_MUTED_FG}; border: none;")
        desc_layout.addWidget(lbl_desc)
        
        layout.addWidget(desc_card)
        layout.addSpacing(20)
        
        # ── Technology Card ──
        tech_card = QFrame()
        tech_card.setStyleSheet(f"""
            QFrame {{
                background-color: {C_CARD};
                border-radius: 12px;
                border: 1px solid {C_BORDER};
            }}
        """)
        tech_layout = QVBoxLayout(tech_card)
        tech_layout.setContentsMargins(16, 16, 16, 16)
        tech_layout.setSpacing(2)
        
        lbl_tech_title = QLabel("TECHNOLOGY")
        lbl_tech_title.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {C_MUTED_FG}; letter-spacing: 1.5px; border: none;")
        tech_layout.addWidget(lbl_tech_title)
        tech_layout.addSpacing(8)
        
        tech_layout.addWidget(InfoRow("Speech Engine", "OpenAI Whisper"))
        tech_layout.addWidget(InfoRow("LLM Support", "OpenAI, Groq"))
        tech_layout.addWidget(InfoRow("Framework", "PySide6 / Qt"))
        tech_layout.addWidget(InfoRow("Platform", "Cross-platform"))
        
        layout.addWidget(tech_card)
        layout.addSpacing(20)
        
        # ── Links Card ──
        links_card = QFrame()
        links_card.setStyleSheet(f"""
            QFrame {{
                background-color: {C_CARD};
                border-radius: 12px;
                border: 1px solid {C_BORDER};
            }}
        """)
        links_layout = QVBoxLayout(links_card)
        links_layout.setContentsMargins(0, 0, 0, 0)
        links_layout.setSpacing(0)
        
        links_layout.addWidget(LinkButton("Source Code", "https://github.com/Natnael-crypto/Vocynx/tree/master"))
        links_layout.addWidget(LinkButton("Contact Support", "mailto:yohannesnatnael9@gmail.com"))
        
        layout.addWidget(links_card)
        layout.addSpacing(32)
        
        # ── Footer ──
        lbl_footer = QLabel("Made by the Vocynx contributors")
        lbl_footer.setAlignment(Qt.AlignCenter)
        lbl_footer.setStyleSheet(f"font-size: 11px; color: {C_MUTED_FG};")
        layout.addWidget(lbl_footer)
        layout.addSpacing(4)
        
        lbl_copyright = QLabel("© 2026 Vocynx. Open Source.")
        lbl_copyright.setAlignment(Qt.AlignCenter)
        lbl_copyright.setStyleSheet(f"font-size: 9px; color: {C_MUTED_FG};")
        layout.addWidget(lbl_copyright)
        
        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
