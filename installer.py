import sys
import os
import shutil
import threading
import time
from pathlib import Path
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QProgressBar, 
                             QStackedWidget, QTextEdit, QCheckBox, QFileDialog)
from PySide6.QtCore import Qt, Signal, QThread, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor, QPalette

from installer_utils import get_app_dir, register_startup, install_files, create_shortcut

# Color Palette
BG_COLOR = "#0c0c0c"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#007bff"
SECONDARY_BG = "#1a1a1a"

class DownloadWorker(QThread):
    progress_update = Signal(int, str)
    finished = Signal(bool, str)

    def __init__(self, models_to_download, target_dir):
        super().__init__()
        self.models_to_download = models_to_download
        self.target_dir = target_dir

    def run(self):
        try:
            from faster_whisper import WhisperModel
            total_models = len(self.models_to_download)
            for i, model in enumerate(self.models_to_download):
                self.progress_update.emit(int((i / total_models) * 100), f"Downloading {model} model...")
                
                # This will download the model to the target_dir if it doesn't exist
                # WhisperModel is smart enough to skip if already downloaded
                WhisperModel(model, device="cpu", compute_type="float32", download_root=self.target_dir)
                
                self.progress_update.emit(int(((i + 1) / total_models) * 100), f"Finished downloading {model}")
            
            self.progress_update.emit(100, "Installation complete!")
            self.finished.emit(True, "Success")
        except Exception as e:
            self.finished.emit(False, f"Download failed: {str(e)}")

class InstallerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vocynx Installer")
        self.setFixedSize(600, 450)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Title Bar
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout(self.title_bar)
        title_label = QLabel("Vocynx Setup")
        title_label.setStyleSheet("color: #888; font-weight: bold; margin-left: 10px;")
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setStyleSheet("QPushButton { border: none; font-size: 20px; color: #ffffff; } QPushButton:hover { background-color: #ffffff; color: #0c0c0c; }")
        self.close_btn.clicked.connect(self.close)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_btn)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_layout.addWidget(self.title_bar)

        # Content - Stacked Widget
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

        self.init_welcome_page()
        self.init_license_page()
        self.init_installing_page()
        self.init_finish_page()

    def apply_styles(self):
        self.central_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_COLOR};
                color: {TEXT_COLOR};
                font-family: 'Segoe UI', sans-serif;
                border-radius: 10px;
            }}
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #0056b3;
            }}
            QPushButton:disabled {{
                background-color: #444;
            }}
            QLabel {{
                font-size: 14px;
            }}
            QProgressBar {{
                border: none;
                background-color: {SECONDARY_BG};
                height: 5px;
                text-align: center;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_COLOR};
                border-radius: 2px;
            }}
            QTextEdit {{
                background-color: {SECONDARY_BG};
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
                color: #ccc;
            }}
            QCheckBox {{
                spacing: 10px;
            }}
        """)

    def init_welcome_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        logo_label = QLabel()
        # Use a placeholder if icon doesn't exist yet
        icon_path = os.path.join(os.path.dirname(__file__), "vocynx_icon.png")
        if os.path.exists(icon_path):
            logo_label.setPixmap(QPixmap(icon_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("VOCYNX")
            logo_label.setStyleSheet("font-size: 48px; font-weight: bold; color: white;")
        logo_label.setAlignment(Qt.AlignCenter)
        
        welcome_title = QLabel("Welcome to Vocynx")
        welcome_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 20px;")
        welcome_title.setAlignment(Qt.AlignCenter)
        
        welcome_desc = QLabel("The fastest local dictation app for your PC.")
        welcome_desc.setStyleSheet("color: #888; margin-bottom: 40px;")
        welcome_desc.setAlignment(Qt.AlignCenter)
        
        install_btn = QPushButton("Install Now")
        install_btn.setFixedWidth(200)
        install_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        
        layout.addStretch()
        layout.addWidget(logo_label)
        layout.addWidget(welcome_title)
        layout.addWidget(welcome_desc)
        layout.addWidget(install_btn, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        self.content_stack.addWidget(page)

    def init_license_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 10, 30, 30)
        
        title = QLabel("License and Privacy")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        # Privacy text
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        try:
            # Try to read from privacy_policy.md if it exists in the same dir for simplicity
            # For now, hardcode a brief version
            license_text.setPlainText("Vocynx Privacy & License Agreement\n\n1. Local Privacy: All audio stays on your device.\n2. No Tracking: We do not collect your data.\n3. Usage: You agree to use this software for productive purposes.\n\nFull terms at: https://vocynx.io/terms")
        except:
            license_text.setPlainText("Loading agreement...")
            
        self.agree_check = QCheckBox("I agree to the terms and conditions")
        self.agree_check.stateChanged.connect(self.toggle_next_btn)
        
        btn_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("background-color: transparent; border: 1px solid #444;")
        back_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        
        self.next_btn = QPushButton("Next")
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.start_installation)
        
        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.next_btn)
        
        layout.addWidget(title)
        layout.addWidget(license_text)
        layout.addWidget(self.agree_check)
        layout.addLayout(btn_layout)
        
        self.content_stack.addWidget(page)

    def toggle_next_btn(self, state):
        self.next_btn.setEnabled(self.agree_check.isChecked())

    def init_installing_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 50, 50, 50)
        
        self.status_label = QLabel("Preparing installation...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(12)
        
        self.detail_label = QLabel("Copying files...")
        self.detail_label.setStyleSheet("color: #666; font-size: 12px;")
        
        layout.addStretch()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.detail_label)
        layout.addStretch()
        
        self.content_stack.addWidget(page)

    def init_finish_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        success_icon = QLabel("✓")
        success_icon.setStyleSheet(f"font-size: 80px; color: {ACCENT_COLOR}; font-weight: bold;")
        success_icon.setAlignment(Qt.AlignCenter)
        
        title = QLabel("Successfully Installed!")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        
        desc = QLabel("Vocynx is now ready to use. It will start with Windows.")
        desc.setStyleSheet("color: #888;")
        desc.setAlignment(Qt.AlignCenter)
        
        launch_btn = QPushButton("Launch Vocynx")
        launch_btn.setFixedWidth(200)
        launch_btn.clicked.connect(self.launch_app)
        
        layout.addStretch()
        layout.addWidget(success_icon)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch()
        layout.addWidget(launch_btn, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        self.content_stack.addWidget(page)

    def start_installation(self):
        self.content_stack.setCurrentIndex(2)
        app_dir = get_app_dir()
        source_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 1. Copy Files
        self.status_label.setText("Copying application files...")
        self.progress_bar.setValue(5)
        if not install_files(source_dir, app_dir):
            self.on_install_finished(False, "Failed to copy application files.")
            return

        # 2. Register startup
        # We'll use the final path for the entry point
        main_py = os.path.join(app_dir, "main.py")
        register_startup(f"{sys.executable} \"{main_py}\"")
        
        # 3. Create Shortcuts
        self.status_label.setText("Creating shortcuts...")
        self.progress_bar.setValue(10)
        # Note: In compiled version, target would be the .exe, but for now we point to script
        # In build_all.py we'll adjust this or handle it via a wrapper
        target_exe = os.path.join(app_dir, "vocynx.exe") if getattr(sys, 'frozen', False) else main_py
        create_shortcut(target_exe, "Vocynx")

        # 4. Start model downloads in background
        self.worker = DownloadWorker(["tiny", "base"], str(app_dir / "models"))
        self.worker.progress_update.connect(self.update_install_progress)
        self.worker.finished.connect(self.on_install_finished)
        self.worker.start()

    def update_install_progress(self, val, status):
        self.progress_bar.setValue(val)
        self.status_label.setText(status)

    def on_install_finished(self, success, message):
        if success:
            self.content_stack.setCurrentIndex(3)
        else:
            self.status_label.setText("Error during installation")
            self.detail_label.setText(message)
            self.detail_label.setStyleSheet("color: #e81123;")

    def launch_app(self):
        # In a real app, we would start the main.py process
        # os.startfile(os.path.join(get_app_dir(), "main.py"))
        print("Launching application...")
        self.close()

    # Mouse events for dragging the borderless window
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InstallerWindow()
    window.show()
    sys.exit(app.exec())
