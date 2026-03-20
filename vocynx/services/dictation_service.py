import threading
from typing import Optional
import os
import sys
import winsound

from vocynx.config import config
from vocynx.stt import TranscriptionWorker
from vocynx.hotkeys import GlobalHotkeyManager
from vocynx.typer import type_text

class DictationService:
    def __init__(self, status_callback=None, transcription_callback=None, audio_level_callback=None, error_callback=None):
        self.status_callback = status_callback
        self.transcription_callback = transcription_callback
        self.audio_level_callback = audio_level_callback
        self.error_callback = error_callback
        
        self.worker = TranscriptionWorker(
            model_loaded_callback=self._on_model_loaded,
            transcription_result_callback=self._on_transcription,
            audio_level_callback=self.audio_level_callback,
            error_callback=self.error_callback
        )
        
        self.hotkey_manager = GlobalHotkeyManager(
            toggle_callback=self._toggle_dictation
        )
        
        self.worker_thread: Optional[threading.Thread] = None
        self.state = "Idle" # Idle, Listening, Processing
        
    def start(self):
        """Initializes the service and starts listening for hotkeys."""
        # Just start the hotkey manager. We don't load the model until first use to save memory.
        self._set_status("Idle")
        self.hotkey_manager.start()
        
    def _on_model_loaded(self, success):
        """Callback when the Whisper model completes loading."""
        if success:
            # Start the infinite transcription queue processor if not already running
            thread_is_active = self.worker_thread is not None and self.worker_thread.is_alive()
            if not thread_is_active:
                self.worker_thread = threading.Thread(target=self.worker.process_queue, daemon=True)
                self.worker_thread.start()
        else:
            self._set_status("Error: Model Load Failed")
            
    def _toggle_dictation(self):
        """Toggles the recording state."""
        if self.worker.is_recording:
            self.stop_dictation()
        else:
            if self.state == "Listening":
                self._set_status("Idle")
            self.start_dictation()
            
    def start_dictation(self):
        """Forces dictation to start manually."""
        if self.state in ("Loading Model...", "Processing"):
            return
            
        if self.worker.model is None:
            # First time use: Load model then start recording
            self._set_status("Loading Model...")
            def _load_and_start():
                self.worker.initialize_model()
                if self.worker.model:
                    self._on_model_loaded(True)
                    # Now that it's loaded, actually start recording
                    self._do_start_recording()
                else:
                    self._set_status("Error: Model Load Failed")
            
            threading.Thread(target=_load_and_start, daemon=True).start()
            return

        if self.state not in ("Idle", "Error: Audio Device Load Failed"):
            return
            
        self._do_start_recording()

    def _do_start_recording(self):
        """Internal helper to actually start the recording process."""
        self._set_status("Listening")
        
        # Play the modern start sound
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            sound_path = os.path.join(sys._MEIPASS, "vocynx", "assets", "start_rec.wav")
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            sound_path = os.path.join(base_dir, "vocynx", "assets", "start_rec.wav")
            
        if os.path.exists(sound_path):
            try:
                winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception:
                pass
                
        self.worker.start_recording()
        
        if not self.worker.is_recording:
            self._set_status("Error: Audio Device Load Failed")
        
    def stop_dictation(self):
        """Stops dictation, forcing transcription of whatever is buffered."""
        if not self.worker.is_recording:
            if self.state == "Listening":
                self._set_status("Idle")
            return
            
        self._set_status("Processing")
        
        def _process():
            # Stop recording and force flush
            self.worker.stop_recording()
            
            # Switch back to idle when done
            self._set_status("Idle")
            
        threading.Thread(target=_process, daemon=True).start()
        
    def _on_transcription(self, text, language):
        """Callback when the STT worker finishes a transcription chunk."""
        if text:
            # Send to typer
            type_text(text)
            
            # Send to UI callback
            if self.transcription_callback:
                self.transcription_callback(text, language)
        
    def _set_status(self, new_state):
        self.state = new_state
        if self.status_callback:
            self.status_callback(self.state)
            
    def shutdown(self):
        """Cleanup resources."""
        # print("Shutting down dictation service...")
        self.hotkey_manager.stop()
        self.worker.shutdown()
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)

