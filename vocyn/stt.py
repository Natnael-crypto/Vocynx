import queue
import time
import numpy as np
import sounddevice as sd
import gc
# faster_whisper imported inside initialize_model to save memory until needed
# deep_translator imported inside _transcribe_audio to save memory

from vocyn.config import config
from vocyn.audio import get_device_index

# Constants
SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_DURATION = 0.03
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION)
ENERGY_THRESHOLD = 0.015

def calculate_energy(audio):
    """Compute RMS energy of the audio frame."""
    return np.sqrt(np.mean(np.square(audio)))

def is_speech(audio):
    """Determine if audio frame contains speech."""
    energy = calculate_energy(audio)
    return energy > ENERGY_THRESHOLD

class TranscriptionWorker:
    def __init__(self, model_loaded_callback=None, transcription_result_callback=None, audio_level_callback=None, error_callback=None):
        self.model = None
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.is_running = True
        self.audio_stream = None
        self.model_loaded_callback = model_loaded_callback
        self.transcription_result_callback = transcription_result_callback
        self.audio_level_callback = audio_level_callback
        self.error_callback = error_callback
        self.current_buffer = []
        self.speech_active = False
        self.last_speech_time = None
        
    def initialize_model(self):
        """Loads the Whisper model synchronously."""
        try:
            model_name = config.get("model", "tiny")
            models_path = config.get("models_path")
            # print(f"Loading Whisper model: {model_name} from {models_path}...")
            # We use float32 for CPU since int8 can sometimes have issues on certain CPUs 
            # or require specific libraries. CPU usage limit is handled separately if needed.
            from faster_whisper import WhisperModel
            import os
            cpu_threads = max(1, os.cpu_count() // 2)
            self.model = WhisperModel(
                model_name,
                device="cpu",
                compute_type="int8",
                cpu_threads=cpu_threads,
                download_root=models_path
            )
            # print("Model loaded successfully.")
            gc.collect() # Clean up any temporary loading memory
            if self.model_loaded_callback:
                self.model_loaded_callback(True)
        except Exception as e:
            # print(f"Failed to load Whisper model: {e}")
            pass
            if self.model_loaded_callback:
                self.model_loaded_callback(False)

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for SoundDevice to feed audio data into the queue."""
        if status:
            pass
        
        if self.is_recording:
            # Emit dynamic audio level for UI (0.0 to 1.0)
            if self.audio_level_callback:
                # calculate energy and normalize roughly for speech values
                energy = calculate_energy(indata)
                # cap max energy at 0.15 for normalization
                max_expected_energy = 0.15  
                level = min(1.0, energy / max_expected_energy)
                self.audio_level_callback(level)
                
            self.audio_queue.put(indata.copy())

    def start_recording(self):
        """Starts the audio listener stream."""
        if self.is_recording:
            return
            
        device_name = config.get("audio_device", "Default Microphone")
        device_idx = get_device_index(device_name)
        
        try:
            self.audio_stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="float32",
                blocksize=FRAME_SIZE,
                device=device_idx,
                callback=self._audio_callback
            )
            self.audio_stream.start()
            self.is_recording = True
            
            # Reset buffers
            self.current_buffer = []
            self.speech_active = False
            self.last_speech_time = None
            
            # Clear the old queue
            while not self.audio_queue.empty():
                self.audio_queue.get(block=False)
                
            # print(f"Started recording on device: {device_name}")
        except Exception as e:
            # print(f"Failed to start recording: {e}")
            pass

    def stop_recording(self):
        """Stops the audio listener stream."""
        if not self.is_recording:
            return
            
        self.is_recording = False
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            self.audio_stream = None
            
        # print("Stopped recording.")
        
        # Force transcription of whatever is left in the buffer
        self._flush_and_transcribe()
        
    def _flush_and_transcribe(self):
        """Transcribes whatever audio remains in the current buffer."""
        if len(self.current_buffer) > 0:
            self._transcribe_audio(self.current_buffer)
            self.current_buffer = []
            
    def _transcribe_audio(self, audio_frames):
        """Transcribes speech using Whisper with automatic language detection."""
        if not self.model or not audio_frames:
            return
            
        # Merge buffered audio frames
        audio = np.concatenate(audio_frames)
        
        # Audio length check. Needs at least a tiny bit of audio
        if len(audio) < SAMPLE_RATE * 0.5: # Half a second
            return
            
        # print("Transcribing audio buffer...")
        
        translate_mode = config.get("translate", False)
        target_lang = config.get("target_language", "en")
        input_lang = config.get("language", "auto")
        llm_provider = config.get("llm_provider", "None")
        llm_model = config.get("llm_model", "")
        llm_api_key = config.get("llm_api_key", "")
        
        whisper_lang = None if input_lang == "auto" else input_lang
        
        task = "translate" if translate_mode and target_lang == "en" else "transcribe"
        
        try:
            segments, info = self.model.transcribe(
                audio,
                beam_size=1,
                best_of=1,
                task=task,
                language=whisper_lang,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=300),
                condition_on_previous_text=False,
            )
            
            text = " ".join(segment.text for segment in segments).strip()
            
            # Refine transcription with LLM if configured
            if llm_provider != "None" and llm_api_key and text:
                print("Refining transcription with LLM...")
                print(f"Provider: {llm_provider}")
                print(f"Model: {llm_model}")
                print(f"API Key: {llm_api_key}")
                print(f"Text: {text}")
                text = self._refine_with_llm(text, llm_provider, llm_api_key, llm_model)
                print(f"Refined Text: {text}")

            # If translation is enabled and target is NOT English, or if Whisper failed to translate to English
            if translate_mode and text:
                if target_lang != "en":
                    # Use deep-translator for non-English targets
                    try:
                        from deep_translator import GoogleTranslator
                        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
                        if translated:
                            text = translated
                    except Exception as te:
                        # print(f"Translation service error: {te}")
                        pass
                elif task == "transcribe" and target_lang == "en" and info.language != "en":
                    # Fallback for English translation if task was transcribe
                    try:
                        from deep_translator import GoogleTranslator
                        translated = GoogleTranslator(source='auto', target='en').translate(text)
                        if translated:
                            text = translated
                    except Exception:
                        pass

            if text and self.transcription_result_callback:
                self.transcription_result_callback(text, info.language)
                
        except Exception as e:
            # print(f"Transcription error: {e}")
            pass

    def _refine_with_llm(self, text, provider, api_key, model=None):
        from vocyn.prompts import REFINEMENT_SYSTEM_PROMPT
        system_prompt = REFINEMENT_SYSTEM_PROMPT
        if provider == "OpenAI":
            if not model: model = "gpt-3.5-turbo"
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=1024,
                    temperature=0.3
                )
                if response.choices:
                    return response.choices[0].message.content.strip()
            except ImportError:
                msg = "OpenAI library not installed."
                print(msg)
                if self.error_callback: self.error_callback(msg)
            except Exception as e:
                msg = f"OpenAI API Error: {e}"
                print(msg)
                if self.error_callback: self.error_callback(msg)
        elif provider == "Groq":
            if not model: model = "llama3-8b-8192"
            try:
                from groq import Groq
                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    max_tokens=1024,
                    temperature=0.3
                )
                if response.choices:
                    return response.choices[0].message.content.strip()
            except ImportError:
                msg = "Groq library not installed."
                print(msg)
                if self.error_callback: self.error_callback(msg)
            except Exception as e:
                msg = f"Groq API Error: {e}"
                print(msg)
                if self.error_callback: self.error_callback(msg)
        return text

    def process_queue(self):
        """Main loop designed to run in a background thread to process audio frames."""
        # Calculate timeout dynamically in case user changes it
        while self.is_running:
            silence_timeout = config.get("silence_timeout", 1.5)
            
            try:
                # Use a small timeout to allow checking `is_running` flag
                data = self.audio_queue.get(timeout=0.1)
                frame = data.flatten()
                
                if is_speech(frame):
                    self.speech_active = True
                    self.last_speech_time = time.time()
                    self.current_buffer.append(frame)
                elif self.speech_active:
                    self.current_buffer.append(frame)
                    
                    if self.last_speech_time and (time.time() - self.last_speech_time) > silence_timeout:
                        # Reached silence timeout, transcribe
                        # We duplicate the buffer and clear it so recording can continue immediately
                        buf_to_transcribe = list(self.current_buffer)
                        self.current_buffer = []
                        self.speech_active = False
                        self.last_speech_time = None
                        
                        # Transcribe the copy (Warning: blocks this thread during inference)
                        # We do this sequentially right now to prevent multiple inferences running at once
                        self._transcribe_audio(buf_to_transcribe)
            except queue.Empty:
                pass
                
    def shutdown(self):
        """Cleans up resources."""
        self.is_running = False
        self.stop_recording()
