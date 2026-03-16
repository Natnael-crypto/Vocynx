import math
import numpy as np
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

class FloatingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Make the window frameless, always on top, and behave as a tool window so it doesn't show in taskbar
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool |
            Qt.WindowTransparentForInput  # Click-through
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Dimensions (half size)
        self.width = 150
        self.height = 50
        self.setFixedSize(self.width, self.height)
        
        # Position at bottom center of the primary screen
        self._center_on_screen()
        
        # Animation state
        self.current_level = 0.0
        self.target_level = 0.0
        self.bars = 15
        self.bar_width = 4
        self.spacing = 2
        self.max_bar_height = self.height - 10
        self.min_bar_height = 4
        
        # Phase for the continuous subtle wave animation
        self.phase = 0.0
        
        # Animation timer (60fps)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)
        
    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        # Position 50 pixels from the bottom
        x = (screen.width() - self.width) // 2
        y = screen.height() - self.height - 50
        self.move(x, y)
        
    def showEvent(self, event):
        """Ensure it's centered if screen resolution changed."""
        super().showEvent(event)
        self._center_on_screen()
        
    def update_level(self, level):
        """Called by the audio service with a normalized audio level (0.0 to 1.0)."""
        # Exaggerate the level slightly for better visual feedback, cap at 1.0
        self.target_level = min(1.0, level * 1.5)
        
    def _animate(self):
        """Animates the current level towards the target level smoothly."""
        # Smooth interpolation
        diff = self.target_level - self.current_level
        self.current_level += diff * 0.3
        
        # Slowly decay the target level if no new audio comes in
        self.target_level = max(0.0, self.target_level - 0.05)
        
        # Advance the wave phase
        self.phase += 0.1
        
        self.update() # Trigger a repaint
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Total width of all bars and spacing
        total_width = (self.bars * self.bar_width) + ((self.bars - 1) * self.spacing)
        start_x = (self.width - total_width) / 2
        
        center_y = self.height / 2
        
        # Colors based on Vocyn's palette
        base_color = QColor("#2196F3") # Blue
        active_color = QColor("#00BCD4") # Cyan-ish when loud
        
        # Interpolate color based on volume
        r = int(base_color.red() + (active_color.red() - base_color.red()) * self.current_level)
        g = int(base_color.green() + (active_color.green() - base_color.green()) * self.current_level)
        b = int(base_color.blue() + (active_color.blue() - base_color.blue()) * self.current_level)
        
        color = QColor(r, g, b)
        
        # Draw background pill/glow (optional, just for contrast)
        pill_rect = QRectF(start_x - 10, center_y - self.max_bar_height/2 - 5, 
                           total_width + 20, self.max_bar_height + 10)
        painter.setBrush(QBrush(QColor(0, 0, 0, 150))) # Semi-transparent black background
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(pill_rect, 10, 10)

        # Draw bars
        painter.setBrush(QBrush(color))
        
        center_idx = self.bars // 2
        
        for i in range(self.bars):
            # Calculate distance from center (0 at center, 1 at edges)
            dist_from_center = abs(i - center_idx) / (self.bars / 2)
            
            # Base height distribution (bell curve shape)
            shape_factor = math.exp(-2.5 * (dist_from_center ** 2))
            
            # Combine volume level with shape, plus a subtle continuous wave
            wave_factor = math.sin(self.phase + (i * 0.5)) * 0.2 + 0.8
            
            h = self.min_bar_height + (self.max_bar_height - self.min_bar_height) * self.current_level * shape_factor * wave_factor
            
            x = start_x + i * (self.bar_width + self.spacing)
            y = center_y - (h / 2)
            
            painter.drawRoundedRect(x, y, self.bar_width, h, self.bar_width/2, self.bar_width/2)
            
        painter.end()
