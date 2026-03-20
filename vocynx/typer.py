import threading
import time
from pynput.keyboard import Controller


keyboard = Controller()

def type_text(text):
    """
    Simulates keyboard typing to insert the transcribed text.
    Runs in a separate thread to avoid blocking the main service.
    """
    if not text:
        return
        
    def _type():
        try:
            # print(f"Typing: {text}")
            # Add a space before inserting to separate from existing text
            # if appropriate, or just type it raw.
            keyboard.type(text + " ")
        except Exception as e:
            # print(f"Failed to auto-type text: {e}")
            pass
            
    threading.Thread(target=_type, daemon=True).start()
