from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QRectF, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
import math

class FloatingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Make the window frameless, always on top, and behave as a tool window
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Dimensions
        self.base_width = 150
        self.base_height = 80 # Taller to allow for bobbing
        self.setFixedSize(self.base_width, self.base_height)
        
        # Animation state
        self.current_level = 0.0
        self.target_level = 0.0
        self.bars = 15
        self.bar_width = 4
        self.spacing = 2
        self.max_bar_height = 40
        self.min_bar_height = 4
        
        # Phase for wave and bobbing
        self.phase = 0.0
        self._opacity = 0.0
        self._is_loading = False
        
        # Position offset for bobbing
        self.y_offset = 0.0
        
        # Center initially
        self._center_on_screen()
        
        # Animation timer (60fps)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)
        
        # Fade animation
        self.fade_anim = QPropertyAnimation(self, b"opacity_prop")
        self.fade_anim.setDuration(300)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_anim.finished.connect(self._on_fade_finished)

    def _on_fade_finished(self):
        if self._opacity < 0.01:
            self.hide()

    def _get_opacity(self):
        return self._opacity

    def _set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)
        self.update()

    opacity_prop = Property(float, _get_opacity, _set_opacity)

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.base_width) // 2
        # Position near bottom, but leave room for bobbing
        y = screen.height() - self.base_height - 60
        self.base_y = y
        self.move(x, y)
        
    def show_widget(self):
        if self.isVisible() and self._opacity > 0.99:
            return
        self._center_on_screen()
        self.show()
        self.fade_anim.stop()
        self.fade_anim.setStartValue(self._opacity)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

    def hide_widget(self):
        if not self.isVisible() or self._opacity < 0.01:
            return
        self.fade_anim.stop()
        self.fade_anim.setStartValue(self._opacity)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.start()

    def set_loading(self, loading):
        self._is_loading = loading
        self.update()

    def update_level(self, level):
        """Called by the audio service with level (0.0 to 1.0)."""
        # Ensure level is a valid finite number
        if not math.isfinite(level):
            level = 0.0
        # Exaggerate the level slightly for better visual feedback, cap at 1.0
        self.target_level = max(self.target_level, min(1.0, level * 1.8))
        
    def _animate(self):
        # Smooth level transitions
        if not math.isfinite(self.target_level):
            self.target_level = 0.0
        if not math.isfinite(self.current_level):
            self.current_level = 0.0
            
        diff = self.target_level - self.current_level
        self.current_level += diff * 0.2
        
        # Decay target level
        self.target_level = max(0.0, self.target_level - 0.08)
        
        # Advance phase
        self.phase += 0.05
        
        # Bobbing animation (vertical movement)
        # Bobs +/- 5 pixels
        self.y_offset = math.sin(self.phase * 0.8) * 5
        
        # Ensure y offset is valid before moving
        if math.isfinite(self.y_offset):
            self.move(self.x(), int(self.base_y + self.y_offset))
        
        self.update()

    def paintEvent(self, event):
        if self._opacity <= 0.01:
            return
            
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Center horizontally
            total_bars_width = (self.bars * self.bar_width) + ((self.bars - 1) * self.spacing)
            start_x = (self.base_width - total_bars_width) / 2
            center_y = self.base_height / 2
            
            # Colors
            base_color = QColor("#2196F3") # Blue
            active_color = QColor("#00BCD4") # Cyan
            loading_color = QColor("#FFC107") # Yellow
            
            # Interpolate color
            level = self.current_level if math.isfinite(self.current_level) else 0.0
            if self._is_loading:
                color = loading_color
            else:
                r = int(base_color.red() + (active_color.red() - base_color.red()) * level)
                g = int(base_color.green() + (active_color.green() - base_color.green()) * level)
                b = int(base_color.blue() + (active_color.blue() - base_color.blue()) * level)
                color = QColor(r, g, b)
            
            # Background pill
            pill_rect = QRectF(start_x - 12, center_y - self.max_bar_height/2 - 8, 
                               total_bars_width + 24, self.max_bar_height + 16)
            painter.setBrush(QBrush(QColor(0, 0, 0, int(180 * self._opacity))))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(pill_rect, 20, 20)

            # Draw bars
            painter.setBrush(QBrush(color))
            center_idx = self.bars // 2
            
            for i in range(self.bars):
                dist_from_center = abs(i - center_idx) / (self.bars / 2)
                shape_factor = math.exp(-3.0 * (dist_from_center ** 2))
                
                # Continuous movement factor (always present)
                # Subtle wave even at 0 volume
                idle_wave = math.sin(self.phase * 2 + (i * 0.4)) * 0.15 + 0.85
                
                if self._is_loading:
                    # Loading animation: scanning wave
                    scan_pos = (math.sin(self.phase * 3) + 1.0) / 2.0 * self.bars
                    dist_to_scan = abs(i - scan_pos)
                    loading_factor = math.exp(-2.0 * (dist_to_scan ** 2))
                    h = self.min_bar_height + (self.max_bar_height - self.min_bar_height) * loading_factor
                else:
                    # Combine volume level
                    h = self.min_bar_height + (self.max_bar_height - self.min_bar_height) * level * shape_factor * idle_wave
                    
                    # Minimum animation when quiet
                    if level < 0.05:
                        h = self.min_bar_height + (math.sin(self.phase + i*0.3) + 1.0) * 2
                
                # Final safety check for h
                if not math.isfinite(h):
                    h = self.min_bar_height
                    
                x = start_x + i * (self.bar_width + self.spacing)
                y = center_y - (h / 2)
                
                painter.drawRoundedRect(QRectF(x, y, self.bar_width, h), self.bar_width/2, self.bar_width/2)
        finally:
            painter.end()



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    widget = FloatingWidget()
    widget.show_widget()
    
    # Simulate some audio spikes
    timer = QTimer()
    timer.timeout.connect(lambda: widget.update_level(math.sin(time.time() * 2) * 0.5 + 0.5))
    import time
    timer.start(500)
    
    sys.exit(app.exec())

