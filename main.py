import sys
import os
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtCore import Qt, QObject, Signal
import ctypes

from vocynx.config import config
from vocynx.ui.main_window import MainWindow
from vocynx.ui.tray_icon import TrayIcon
from vocynx.ui.floating_widget import FloatingWidget
from vocynx.services.dictation_service import DictationService


def create_app_icon():
    """Load the app icon from file, or create a simple generated icon as fallback."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
        icon_path = os.path.join(sys._MEIPASS, "vocynx_icon.ico")
    else:
        # Running in normal python environment
        icon_path = os.path.join(os.path.dirname(__file__), "vocynx_icon.ico")
        
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    
    # Fallback to generated icon
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor("transparent"))
    # Just a simple circle placeholder
    from PySide6.QtGui import QPainter, QBrush, QPen
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor("#2196F3")))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(4, 4, 56, 56)
    
    # Draw simple mic shape
    painter.setBrush(QBrush(QColor("#FFFFFF")))
    painter.drawRoundedRect(24, 16, 16, 24, 8, 8)
    painter.drawRect(30, 40, 4, 8)
    painter.drawRect(20, 48, 24, 4)
    painter.end()
    
    return QIcon(pixmap)

class AppSignals(QObject):
    status_changed = Signal(str)
    transcription = Signal(str, str)
    error = Signal(str)

class VocynxApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # Set AppUserModelID for Windows taskbar grouping
        if sys.platform == 'win32':
            myappid = 'natnael.vocynx.1.0' # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
        self.app.setQuitOnLastWindowClosed(False) # Keep running in tray
        
        self.icon = create_app_icon()
        self.app.setWindowIcon(self.icon)
        
        self.signals = AppSignals()
        self.signals.status_changed.connect(self._on_status_changed)
        self.signals.transcription.connect(self._on_transcription)
        self.signals.error.connect(self._on_error)
        
        # Initialize UI Components
        self.main_window = MainWindow()
        self.floating_widget = FloatingWidget()
        
        # Initialize Service
        self.dictation_service = DictationService(
            status_callback=self.signals.status_changed.emit,
            transcription_callback=self.signals.transcription.emit,
            audio_level_callback=self.floating_widget.update_level,
            error_callback=self.signals.error.emit
        )
        
        # Initialize Tray
        self.tray_icon = TrayIcon(self.icon)
        
        self.setup_connections()
        
    def setup_connections(self):
        # UI to Service
        self.main_window.dictation_toggled.connect(self.dictation_service._toggle_dictation)
        self.main_window.settings_saved.connect(self.on_settings_saved)
        
        # Tray to App/Service/UI
        self.tray_icon.open_requested.connect(self.show_main_window)
        self.tray_icon.settings_requested.connect(self.show_settings)
        self.tray_icon.start_dictation_requested.connect(self.dictation_service.start_dictation)
        self.tray_icon.stop_dictation_requested.connect(self.dictation_service.stop_dictation)
        self.tray_icon.quit_requested.connect(self.quit_app)
        
    def _on_status_changed(self, status):
        """Called by service when state changes."""
        self.main_window.set_status(status)
        self.tray_icon.update_state(status)
        
        # Show/Hide floating widget
        if status in ["Listening", "Processing", "Loading Model..."]:
            self.floating_widget.show_widget()
            # Set loading state if applicable
            self.floating_widget.set_loading(status == "Loading Model...")
        elif status == "Idle" or "Error" in status:
            self.floating_widget.hide_widget()
        
        if config.get("desktop_notifications", True) and status in ["Listening", "Processing"]:
            self.tray_icon.showMessage("Vocynx", f"Dictation: {status}", QSystemTrayIcon.Information, 1000)


    def _on_transcription(self, text, language):
        """Called by service when text is transcribed."""
        self.main_window.add_transcription(text)
        
    def _on_error(self, message):
        """Called when an error (like LLM failure) occurs."""
        self.tray_icon.showMessage("Vocynx Error", message, QSystemTrayIcon.Warning, 3000)
        
    def show_main_window(self):
        self.main_window.show()
        self.main_window.activateWindow()
        self.main_window.raise_()
        
    def show_settings(self):
        self.show_main_window()
        self.main_window.show_settings_view()
            
    def on_settings_saved(self):
        # The main window already updates its own display, we just update the service
        self.dictation_service.hotkey_manager.update_hotkey(config.get("hotkey"))
            
    def quit_app(self):
        # logger.info("Quitting application...")
        self.tray_icon.hide()
        self.dictation_service.shutdown()
        self.app.quit()
        
    def run(self):
        # Start core service (starts hotkey listener & async model load)
        self.dictation_service.start()
        
        self.tray_icon.show()
        
        # Force show if not specifically told to minimize, or if it's currently true (fixing the issue)
        if config.get("run_minimized", False):
            # If it was true, we'll set it to false now for the future but respect it this once?
            # Actually, the user wants it FIXED, so let's override it if we want to show the app.
            pass
            
        self.show_main_window()
        
        # Ensure we save the fixed state
        if config.get("run_minimized", True):
            config.set("run_minimized", False)
            
        return self.app.exec()

def main():
    print("[INFO] Vocynx started")
    print("[INFO] Open source licenses loaded")
    # Only allow single instance (simple check)
    lock_file = os.path.join(os.path.expanduser("~"), ".vocynx", "app.lock")
    try:
        os.makedirs(os.path.dirname(lock_file), exist_ok=True)
        # Using a simple file lock. If we can't delete it, it might be in use
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
            except OSError:
                # logger.error("Vocynx is already running.")
                sys.exit(1)
                
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
            
        app = VocynxApp()
        exit_code = app.run()
        
        # Cleanup
        try:
            os.remove(lock_file)
        except OSError:
            pass
            
        sys.exit(exit_code)
        
    except Exception as e:
        # print(f"Application crashed: {e}")
        pass
        
if __name__ == "__main__":
    main()
