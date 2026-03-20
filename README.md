# Vocynx

<div align="center">
  <img src="images/home.png" alt="Vocynx Home Interface" width="400">
  <p><b>Lightweight, fast, privacy-first alternative to WhisperFlow.ai</b></p>
</div>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#why-vocynx">Why Vocynx?</a> •
  <a href="#installation">Installation</a> •
  <a href="#how-it-works">How it Works</a> •
  <a href="#development">Development</a>
</p>

---

**Vocynx** is a next-generation desktop application for real-time, on-device speech-to-text (STT) and multi-language translation. Designed for uncompromising speed and complete user privacy, Vocynx lives quietly in your system tray and empowers you to dictate text *anywhere* with a simple global hotkey.

No cloud subscriptions, no data harvesting just pure, local AI transcription powered by the state-of-the-art Faster-Whisper engine.

---

## Features

* **Instant Global Dictation**: Press `Ctrl+Shift+D` to start/stop dictation in any application instantly. No window focus required.
* **100% Privacy & Local-First**: Your voice data **never** leaves your machine. Transcription happens entirely offline.
* **WhisperFlow.ai Alternative**: All the premium features of cloud-based transcription apps, completely free and open-source.
* **Real-time Translation**: Dictate in your native language and automatically translate to another using built-in services.
* **Lightning Fast**: Optimized for CPU inference. Achieves ~0.2x real-time factor (transcribes 5s of audio in 1s) with a low memory footprint.
* **Beautiful Modern UI**: A sleek, dark-themed dashboard built with PySide6 that feels native and responsive.

---

## Screenshots

| Dashboard | Settings |
|:---:|:---:|
| <img src="images/home.png" width="400"> | <img src="images/settings.png" width="400"> |
| **Licenses & Info** | **About** |
| <img src="images/license.png" width="400"> | <img src="images/about.png" width="400"> |

---

## Why Vocynx over WhisperFlow.ai?

Cloud-based solutions like WhisperFlow.ai charge monthly subscriptions and process your private conversations on their servers. 
Vocynx leverages highly-optimized local AI models, giving you:
- **Zero Latency**: No waiting for network requests.
- **Zero Cost**: Completely free forever.
- **Zero Tracking**: Maximum privacy and security.

### Performance Benchmarks

| Metric | Result |
| :--- | :--- |
| **Base Memory Usage** | ~30 MB |
| **Active Memory (Whisper Tiny)** | ~280 MB |
| **Transcription Speed (CPU)** | ~0.2x Real-time |
| **Executable Size** | ~140 MB |
| **Connectivity Required** | None (Off-line capable) |

---

## Installation & First-Time Setup

1. **Download & Install**: Grab the latest `VocynxInstaller.exe` from the [Releases](#) page and run it.
2. **Launch**: Open Vocynx from your Desktop or Start Menu. It will dock neatly into your system tray.
3. **Choose Your Engine**: On first launch, head to **Settings** and select your preferred Whisper model.
    - **Tiny (Default)**: ~100 MB footprint. Highly recommended for blazingly fast transcription.
    - **Base/Small**: Higher accuracy, requires slightly more memory.
4. **Auto-Download**: Vocynx will automatically download the selected model locally (only happens once).

---

## Architecture & Tech Stack

Vocynx uses a hybrid architecture for maximum performance and native system integration:

- **Core AI Engine**: Python + [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2) + [NumPy](https://numpy.org/).
- **Audio Capture**: Real-time buffer streaming with [SoundDevice](https://python-sounddevice.readthedocs.io/).
- **GUI & System Integration**: [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python). Handles global hotkeys and modern, responsive styling.
- **Standalone Installer**: Engineered with [Wails](https://wails.io/) (Go + Vite/TS) to handle dependencies smoothly on Windows.
- **Packaging**: Built into a single executable using [PyInstaller](https://pyinstaller.org/).

---

## Development

Want to contribute to the open-source alternative to WhisperFlow? We'd love your help!

### Prerequisites
- Python 3.9+
- Go 1.21+ (for installer modifications)
- Windows OS (Currently Windows-focused, Linux/macOS support planned)

### Build from Source
```bash
# Clone the repository
git clone https://github.com/Natnael-crypto/Vocynx.git
cd Vocynx

# Install dependencies
pip install -r requirements.txt

# Run in dev mode
python main.py

# Build the main application executable
python build_all.py
```

---

## License & Attribution

Vocynx is proudly released under the **MIT License**.

Developed and maintained by [Natnael-crypto](https://github.com/Natnael-crypto).
Special thanks to the open-source AI community and the creators of Whisper, PySide/Qt, and Faster-Whisper.

<div align="center">
  <i>"Dictate anywhere, privately, at the speed of thought."</i>
</div>
