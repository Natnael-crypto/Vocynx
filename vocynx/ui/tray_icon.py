from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QObject

class TrayIcon(QSystemTrayIcon):
    # Signals to communicate back to the main app instance
    open_requested = Signal()
    settings_requested = Signal()
    start_dictation_requested = Signal()
    stop_dictation_requested = Signal()
    quit_requested = Signal()
    
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.setToolTip("Vocynx - Local Dictation")
        
        self.menu = QMenu()
        self.menu.setStyleSheet("""
            QMenu { background-color: #FFFFFF; color: #221F1C; border: 1px solid #E9E4DD; border-radius: 8px; }
            QMenu::item { padding: 6px 20px; font-family: 'Inter', 'Segoe UI', sans-serif; font-size: 13px; }
            QMenu::item:selected { background-color: #F2EFE9; }
            QMenu::separator { height: 1px; background: #E9E4DD; margin: 4px 8px; }
        """)
        
        self.action_open = QAction("Open Dashboard", self)
        self.action_open.triggered.connect(self.open_requested.emit)
        
        self.action_start = QAction("Start Dictation", self)
        self.action_start.triggered.connect(self.start_dictation_requested.emit)
        
        self.action_stop = QAction("Stop Dictation", self)
        self.action_stop.triggered.connect(self.stop_dictation_requested.emit)
        
        self.action_settings = QAction("Settings", self)
        self.action_settings.triggered.connect(self.settings_requested.emit)
        
        self.action_quit = QAction("Quit", self)
        self.action_quit.triggered.connect(self.quit_requested.emit)
        
        self.menu.addAction(self.action_open)
        self.menu.addSeparator()
        self.menu.addAction(self.action_start)
        self.menu.addAction(self.action_stop)
        self.menu.addSeparator()
        self.menu.addAction(self.action_settings)
        self.menu.addSeparator()
        self.menu.addAction(self.action_quit)
        
        self.setContextMenu(self.menu)
        self.activated.connect(self._on_activate)
        
        self.update_state("Idle")
        
    def _on_activate(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.open_requested.emit()
            
    def update_state(self, state):
        if state == "Idle" or state.startswith("Error"):
            self.action_start.setEnabled(True)
            self.action_stop.setEnabled(False)
        else:
            self.action_start.setEnabled(False)
            self.action_stop.setEnabled(True)
            
        self.setToolTip(f"Vocynx - {state}")
