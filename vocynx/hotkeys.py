import keyboard

from vocynx.config import config

class GlobalHotkeyManager:
    def __init__(self, toggle_callback):
        self.toggle_callback = toggle_callback
        self.current_hotkey = config.get("hotkey", "ctrl+alt+space")
        self.is_listening = False
        
    def _on_hotkey(self):
        """Called when the global hotkey is pressed. Toggles dictation."""
        self.toggle_callback()
        
    def start(self):
        """Start listening for the globally configured hotkey."""
        if not self.is_listening:
            try:
                keyboard.add_hotkey(self.current_hotkey, self._on_hotkey)
                self.is_listening = True
            except Exception:
                pass

    def stop(self):
        """Stop listening for the global hotkey."""
        if self.is_listening:
            try:
                keyboard.remove_hotkey(self.current_hotkey)
                self.is_listening = False
            except Exception:
                pass
                
    def update_hotkey(self, new_hotkey):
        """Update the global hotkey to listen for."""
        was_listening = self.is_listening
        
        if was_listening:
            self.stop()
            
        self.current_hotkey = new_hotkey
        
        if was_listening:
            self.start()
