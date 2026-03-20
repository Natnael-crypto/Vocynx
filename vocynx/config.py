import json
import os
from pathlib import Path


class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".vocynx"
        self.config_file = self.config_dir / "config.json"
        
        self.default_config = {
            "audio_device": "Default Microphone",
            "language": "auto",
            "translate": False,
            "model": "tiny",
            "models_path": str(Path.home() / ".vocynx" / "models"),
            "hotkey": "ctrl+alt+space",
            "silence_timeout": 1.5,
            "start_on_boot": False,
            "run_minimized": False,
            "desktop_notifications": True,
            "target_language": "en",
            "theme": "dark",
            "cpu_limit": 50,
            "gpu_acceleration": False,
            "llm_provider": "None",
            "llm_model": "",
            "llm_api_key": ""
        }
        
        self.settings = self.default_config.copy()
        self.load()

    def load(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    loaded_config = json.load(f)
                    self.settings.update(loaded_config)
                # print("Configuration loaded from ~/.vocynx/config.json")
            except Exception as e:
                # print(f"Failed to load config: {e}")
                pass
            
    def save(self):
        try:
            if not self.config_dir.exists():
                self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(self.settings, f, indent=4)
            # print("Configuration saved to ~/.vocynx/config.json")
        except Exception as e:
            # print(f"Failed to save config: {e}")
            pass

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()

# Singleton instance
config = Config()
