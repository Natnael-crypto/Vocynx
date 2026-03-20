from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QCheckBox, QPushButton, QSlider,
    QRadioButton, QButtonGroup, QScrollArea, QFrame,
    QLineEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from vocynx.config import config
import os
import sys

def get_asset_path(filename):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'vocynx', 'assets', filename)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", filename)

ARROW_PATH = get_asset_path("ic_drop_down.svg").replace('\\', '/')

class NonScrollingComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()
from vocynx.audio import get_available_microphones

# ─── Light Theme Colors ──────────────────────────────────────────────────────
C_BG         = "#F8F9FC"
C_FG         = "#221F1C"
C_CARD       = "#FFFFFF"
C_PRIMARY    = "#221F1C"
C_PRIMARY_FG = "#FAF8F5"
C_SECONDARY  = "#F5EDCF"
C_MUTED      = "#F2EFE9"
C_MUTED_FG   = "#857F79"
C_BORDER     = "#E9E4DD"
C_INPUT      = "#E9E4DD"


class SettingSection(QFrame):
    """A rounded card section that groups related settings."""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("section")
        self.setStyleSheet(f"""
            QFrame#section {{
                background-color: {C_CARD};
                border-radius: 12px;
                border: 1px solid {C_BORDER};
            }}
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        
        # Section title (shown ABOVE the card externally, not inside)
        # We add it inside for simplicity but with transparent bg
        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet(f"""
            font-size: 10px; font-weight: 700; color: {C_MUTED_FG};
            letter-spacing: 1.5px; padding: 14px 16px 6px 16px;
        """)
        self._layout.addWidget(lbl_title)
    
    def add_row(self, widget):
        self._layout.addWidget(widget)


class SettingRow(QFrame):
    """A single row inside a setting section."""
    def __init__(self, label, description=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: none;
                border-bottom: 1px solid {C_BORDER};
            }}
        """)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(16, 10, 16, 10)
        self._layout.setSpacing(12)
        
        left = QVBoxLayout()
        left.setSpacing(2)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {C_FG}; border: none;")
        left.addWidget(lbl)
        
        if description:
            desc = QLabel(description)
            desc.setStyleSheet(f"font-size: 11px; color: {C_MUTED_FG}; font-weight: 400; border: none;")
            desc.setWordWrap(True)
            left.addWidget(desc)
        
        self._layout.addLayout(left, 1)
    
    def add_control(self, widget):
        self._layout.addWidget(widget)


class SettingsView(QWidget):
    settings_saved = Signal()

    MODELS = {
        "OpenAI": [
            "gpt-5.4", "gpt-5.4-thinking", "gpt-5.4-pro",
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo",
            "o1", "o1-mini", "whisper-1"
        ],
        "Groq": [
            "openai/gpt-oss-120b", "openai/gpt-oss-20b",
            "llama-3.1-8b-instant", "llama-3.3-70b-versatile",
            "deepseek-r1-distill-llama-70b", "qwen/qwen3-32b",
            "whisper-large-v3", "whisper-large-v3-turbo"
        ]
    }

    COMBO_STYLE = f"""
        QComboBox {{
            background-color: {C_CARD};
            color: {C_FG};
            border: 1px solid {C_BORDER};
            border-radius: 6px;
            padding: 4px 10px;
            min-height: 28px;
            font-size: 12px;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }}
        QComboBox:hover {{ border: 1px solid {C_MUTED_FG}; }}
        QComboBox::drop-down {{ border: none; width: 24px; }}
        QComboBox::down-arrow {{
            image: url({ARROW_PATH});
            width: 10px;
            height: 6px;
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {C_CARD};
            color: {C_FG};
            selection-background-color: {C_MUTED};
            border: 1px solid {C_BORDER};
            outline: none;
            padding: 4px 0px;
            font-size: 12px;
        }}
    """

    LINEEDIT_STYLE = f"""
        QLineEdit {{
            background-color: {C_CARD};
            color: {C_FG};
            border: 1px solid {C_BORDER};
            border-radius: 6px;
            padding: 4px 10px;
            min-height: 28px;
            font-size: 12px;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }}
        QLineEdit:focus {{ border: 1px solid {C_MUTED_FG}; }}
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsView")
        self.setStyleSheet(f"""
            QWidget#settingsView {{ 
                background-color: {C_BG}; 
            }}
            QWidget {{
                color: {C_FG}; 
                font-family: 'Inter', 'Segoe UI', sans-serif; 
            }}
            QRadioButton {{ spacing: 8px; color: {C_FG}; font-size: 13px; }}
            QRadioButton::indicator {{ 
                width: 16px; height: 16px; border-radius: 8px; 
                background-color: {C_CARD}; border: 2px solid {C_BORDER}; 
            }}
            QRadioButton::indicator:checked {{ 
                background-color: {C_PRIMARY}; border: 2px solid {C_PRIMARY}; 
            }}
            QRadioButton::indicator:hover {{ border: 2px solid {C_MUTED_FG}; }}
            QCheckBox {{ spacing: 8px; color: {C_FG}; font-size: 13px; }}
            QCheckBox::indicator {{ 
                width: 38px; height: 20px; border-radius: 10px; 
                background-color: {C_BORDER}; border: none; 
            }}
            QCheckBox::indicator:checked {{ 
                background-color: {C_PRIMARY}; border: none; 
            }}
            QSlider::groove:horizontal {{ 
                border: none; height: 4px; 
                background: {C_BORDER}; border-radius: 2px; 
            }}
            QSlider::handle:horizontal {{ 
                background: {C_PRIMARY}; border: none; 
                width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; 
            }}
            QSlider::sub-page:horizontal {{
                background: {C_PRIMARY}; border-radius: 2px;
            }}
            QScrollBar:vertical {{
                border: none; background: {C_BG}; width: 6px;
                border-radius: 3px; margin: 4px 2px;
            }}
            QScrollBar::handle:vertical {{ 
                background: {C_BORDER}; min-height: 30px; border-radius: 3px; 
            }}
            QScrollBar::handle:vertical:hover {{ background: {C_MUTED_FG}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        self.setup_ui()
        self.load_current_settings()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet(f"#container {{ background-color: {C_BG}; }}")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 40, 20, 100)
        layout.setSpacing(16)
        
        # ── Header ──
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        lbl_h1 = QLabel("Settings")
        lbl_h1.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {C_FG};")
        header_layout.addWidget(lbl_h1)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        layout.addSpacing(8)
        
        # ── Audio Section ──
        sec_audio = SettingSection("Audio")
        row_mic = SettingRow("Microphone", "Select audio input device")
        self.combo_mic = NonScrollingComboBox()
        self.combo_mic.setStyleSheet(self.COMBO_STYLE)
        self.combo_mic.setFixedWidth(150)
        self.combo_mic.addItems(get_available_microphones())
        row_mic.add_control(self.combo_mic)
        sec_audio.add_row(row_mic)
        layout.addWidget(sec_audio)

        # ── Language Section ──
        sec_lang = SettingSection("Language")
        row_lang = SettingRow("Input Language", "Whisper language for transcription")
        self.combo_lang = NonScrollingComboBox()
        self.combo_lang.setStyleSheet(self.COMBO_STYLE)
        self.combo_lang.setFixedWidth(130)
        
        self.whisper_languages = {
            "auto": "Auto Detect",
            "af": "Afrikaans", "am": "Amharic", "ar": "Arabic", "as": "Assamese", "az": "Azerbaijani",
            "ba": "Bashkir", "be": "Belarusian", "bg": "Bulgarian", "bn": "Bengali", "bo": "Tibetan",
            "br": "Breton", "bs": "Bosnian", "ca": "Catalan", "cs": "Czech", "cy": "Welsh",
            "da": "Danish", "de": "German", "el": "Greek", "en": "English", "es": "Spanish",
            "et": "Estonian", "eu": "Basque", "fa": "Persian", "fi": "Finnish", "fo": "Faroese",
            "fr": "French", "gl": "Galician", "gu": "Gujarati", "ha": "Hausa", "haw": "Hawaiian",
            "hi": "Hindi", "hr": "Croatian", "hu": "Hungarian", "hy": "Armenian", "id": "Indonesian",
            "is": "Icelandic", "it": "Italian", "iw": "Hebrew", "ja": "Japanese", "jw": "Javanese",
            "ka": "Georgian", "kk": "Kazakh", "km": "Khmer", "kn": "Kannada", "ko": "Korean",
            "la": "Latin", "lb": "Luxembourgish", "ln": "Lingala", "lo": "Lao", "lt": "Lithuanian",
            "lv": "Latvian", "mg": "Malagasy", "mi": "Maori", "mk": "Macedonian", "ml": "Malayalam",
            "mn": "Mongolian", "mr": "Marathi", "ms": "Malay", "mt": "Maltese", "my": "Burmese",
            "ne": "Nepali", "nl": "Dutch", "nn": "Nynorsk", "no": "Norwegian", "oc": "Occitan",
            "pa": "Punjabi", "pl": "Polish", "ps": "Pashto", "pt": "Portuguese", "ro": "Romanian",
            "ru": "Russian", "sa": "Sanskrit", "sd": "Sindhi", "si": "Sinhala", "sk": "Slovak",
            "sl": "Slovenian", "sn": "Shona", "so": "Somali", "sq": "Albanian", "sr": "Serbian",
            "su": "Sundanese", "sv": "Swedish", "sw": "Swahili", "ta": "Tamil", "te": "Telugu",
            "tg": "Tajik", "th": "Thai", "tk": "Turkmen", "tl": "Tagalog", "tr": "Turkish",
            "tt": "Tatar", "uk": "Ukrainian", "ur": "Urdu", "uz": "Uzbek", "vi": "Vietnamese",
            "yi": "Yiddish", "yo": "Yoruba", "zh": "Chinese"
        }
        for val, lbl in self.whisper_languages.items():
            self.combo_lang.addItem(lbl, userData=val)
        row_lang.add_control(self.combo_lang)
        sec_lang.add_row(row_lang)
        layout.addWidget(sec_lang)

        # ── Transcription Mode Section ──
        sec_mode = SettingSection("Transcription Mode")
        
        mode_widget = QWidget()
        mode_widget.setStyleSheet("background-color: transparent; border: none;")
        mode_layout = QVBoxLayout(mode_widget)
        mode_layout.setContentsMargins(16, 10, 16, 10)
        mode_layout.setSpacing(10)
        
        self.radio_group = QButtonGroup(self)
        self.radio_transcribe = QRadioButton("Transcribe only")
        self.radio_translate = QRadioButton("Translation")
        self.radio_group.addButton(self.radio_transcribe)
        self.radio_group.addButton(self.radio_translate)
        
        self.radio_transcribe.toggled.connect(self.on_mode_changed)
        self.radio_translate.toggled.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.radio_transcribe)
        mode_layout.addWidget(self.radio_translate)
        
        self.target_lang_row = QWidget()
        self.target_lang_row.setStyleSheet("border: none;")
        tl_layout = QHBoxLayout(self.target_lang_row)
        tl_layout.setContentsMargins(0, 4, 0, 0)
        tl_lbl = QLabel("Target Language")
        tl_lbl.setStyleSheet(f"font-size: 13px; color: {C_MUTED_FG}; border: none;")
        self.combo_target_lang = NonScrollingComboBox()
        self.combo_target_lang.setStyleSheet(self.COMBO_STYLE)
        self.combo_target_lang.setFixedWidth(130)
        for val, lbl in self.whisper_languages.items():
            if val != "auto":
                self.combo_target_lang.addItem(lbl, userData=val)
        tl_layout.addWidget(tl_lbl)
        tl_layout.addStretch()
        tl_layout.addWidget(self.combo_target_lang)
        mode_layout.addWidget(self.target_lang_row)
        
        sec_mode.add_row(mode_widget)
        layout.addWidget(sec_mode)

        # ── LLM Refinement Section ──
        sec_llm = SettingSection("LLM Refinement")
        
        row_provider = SettingRow("Provider")
        self.combo_llm_provider = NonScrollingComboBox()
        self.combo_llm_provider.setStyleSheet(self.COMBO_STYLE)
        self.combo_llm_provider.setFixedWidth(110)
        self.combo_llm_provider.addItems(["None", "OpenAI", "Groq"])
        row_provider.add_control(self.combo_llm_provider)
        sec_llm.add_row(row_provider)
        
        self.row_model = SettingRow("Model")
        self.combo_llm_model = NonScrollingComboBox()
        self.combo_llm_model.setStyleSheet(self.COMBO_STYLE)
        self.combo_llm_model.setFixedWidth(150)
        self.combo_llm_model.setEditable(True)
        self.row_model.add_control(self.combo_llm_model)
        sec_llm.add_row(self.row_model)
        
        self.row_apikey = SettingRow("API Key")
        self.input_llm_api_key = QLineEdit()
        self.input_llm_api_key.setPlaceholderText("Enter key")
        self.input_llm_api_key.setEchoMode(QLineEdit.Password)
        self.input_llm_api_key.setStyleSheet(self.LINEEDIT_STYLE)
        self.input_llm_api_key.setFixedWidth(150)
        self.row_apikey.add_control(self.input_llm_api_key)
        sec_llm.add_row(self.row_apikey)
        
        self.combo_llm_provider.currentTextChanged.connect(self.on_llm_provider_changed)
        layout.addWidget(sec_llm)

        # ── Transcription Model Section ──
        sec_model = SettingSection("Transcription Model")
        row_model = SettingRow("Whisper Model", "Larger models are more accurate but slower")
        self.combo_model = NonScrollingComboBox()
        self.combo_model.setStyleSheet(self.COMBO_STYLE)
        self.combo_model.setFixedWidth(90)
        self.combo_model.addItems(["tiny", "base", "small"])
        row_model.add_control(self.combo_model)
        sec_model.add_row(row_model)
        layout.addWidget(sec_model)

        # ── Silence Timeout Section ──
        sec_timeout = SettingSection("Silence Timeout")
        
        timeout_widget = QWidget()
        timeout_widget.setStyleSheet("background-color: transparent; border: none;")
        timeout_layout = QVBoxLayout(timeout_widget)
        timeout_layout.setContentsMargins(16, 10, 16, 14)
        timeout_layout.setSpacing(8)
        
        timeout_header = QHBoxLayout()
        lbl_timeout_title = QLabel("Timeout Duration")
        lbl_timeout_title.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {C_FG}; border: none;")
        self.lbl_timeout_val = QLabel("1.5s")
        self.lbl_timeout_val.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {C_FG}; border: none;")
        timeout_header.addWidget(lbl_timeout_title)
        timeout_header.addStretch()
        timeout_header.addWidget(self.lbl_timeout_val)
        timeout_layout.addLayout(timeout_header)
        
        self.slider_timeout = QSlider(Qt.Horizontal)
        self.slider_timeout.setRange(8, 25)
        self.slider_timeout.setSingleStep(1)
        self.slider_timeout.valueChanged.connect(
            lambda v: self.lbl_timeout_val.setText(f"{v/10.0:.1f}s")
        )
        timeout_layout.addWidget(self.slider_timeout)
        
        range_layout = QHBoxLayout()
        lbl_min = QLabel("0.8s")
        lbl_min.setStyleSheet(f"font-size: 10px; color: {C_MUTED_FG}; border: none;")
        lbl_max = QLabel("2.5s")
        lbl_max.setStyleSheet(f"font-size: 10px; color: {C_MUTED_FG}; border: none;")
        range_layout.addWidget(lbl_min)
        range_layout.addStretch()
        range_layout.addWidget(lbl_max)
        timeout_layout.addLayout(range_layout)
        
        sec_timeout.add_row(timeout_widget)
        layout.addWidget(sec_timeout)

        # ── Global Hotkey Section ──
        sec_hotkey = SettingSection("Global Hotkey")
        row_hotkey = SettingRow("Shortcut", "Toggle transcription")
        self.combo_hotkey = NonScrollingComboBox()
        self.combo_hotkey.setStyleSheet(self.COMBO_STYLE)
        self.combo_hotkey.setFixedWidth(140)
        self.combo_hotkey.addItems([
            "ctrl+alt+space", "ctrl+shift+space", "alt+space", "shift+f12"
        ])
        self.combo_hotkey.setEditable(True)
        row_hotkey.add_control(self.combo_hotkey)
        sec_hotkey.add_row(row_hotkey)
        layout.addWidget(sec_hotkey)

        # ── System Section ──
        sec_system = SettingSection("System")
        row_tray = SettingRow("Run in Tray", "Minimize to system tray on close")
        self.check_tray = QRadioButton()
        self.check_tray.setAutoExclusive(False)
        row_tray.add_control(self.check_tray)
        sec_system.add_row(row_tray)
        layout.addWidget(sec_system)
        
        layout.addSpacing(8)

        # ── Save Button ──
        self.btn_save = QPushButton("Save Settings")
        self.btn_save.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_save.setFixedHeight(44)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {C_PRIMARY};
                color: {C_PRIMARY_FG};
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 700;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{
                background-color: #3A3630;
            }}
        """)
        self.btn_save.clicked.connect(self.save_settings)
        layout.addWidget(self.btn_save)
        
        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
    def on_mode_changed(self):
        is_translate = self.radio_translate.isChecked()
        self.target_lang_row.setVisible(is_translate)

    def on_llm_provider_changed(self, text):
        show = text != "None"
        self.row_model.setVisible(show)
        self.row_apikey.setVisible(show)
        self.input_llm_api_key.setVisible(show)
        
        if text in self.MODELS:
            current_model = self.combo_llm_model.currentText()
            self.combo_llm_model.clear()
            self.combo_llm_model.addItems(self.MODELS[text])
            if current_model in self.MODELS[text]:
                self.combo_llm_model.setCurrentText(current_model)

    def load_current_settings(self):
        mic = config.get("audio_device")
        idx = self.combo_mic.findText(mic)
        if idx >= 0: self.combo_mic.setCurrentIndex(idx)
        lang = config.get("language")
        idx = self.combo_lang.findData(lang)
        if idx >= 0: self.combo_lang.setCurrentIndex(idx)
        is_translate = config.get("translate", False)
        if is_translate: self.radio_translate.setChecked(True)
        else: self.radio_transcribe.setChecked(True)
        target_lang = config.get("target_language", "en")
        idx = self.combo_target_lang.findData(target_lang)
        if idx >= 0: self.combo_target_lang.setCurrentIndex(idx)
        
        model = config.get("model")
        idx = self.combo_model.findText(model)
        if idx >= 0: self.combo_model.setCurrentIndex(idx)
        timeout = int(config.get("silence_timeout", 1.5) * 10)
        self.slider_timeout.setValue(timeout)
        hotkey = config.get("hotkey")
        self.combo_hotkey.setCurrentText(hotkey)
        self.check_tray.setChecked(config.get("run_minimized", True))
        
        llm_prov = config.get("llm_provider", "None")
        idx = self.combo_llm_provider.findText(llm_prov)
        if idx >= 0: self.combo_llm_provider.setCurrentIndex(idx)
        
        self.on_llm_provider_changed(llm_prov)
        
        saved_model = config.get("llm_model", "")
        self.combo_llm_model.setCurrentText(saved_model)
        self.input_llm_api_key.setText(config.get("llm_api_key", ""))
        
    def save_settings(self):
        config.set("audio_device", self.combo_mic.currentText())
        config.set("language", self.combo_lang.currentData())
        config.set("translate", self.radio_translate.isChecked())
        config.set("target_language", self.combo_target_lang.currentData())
        config.set("model", self.combo_model.currentText())
        config.set("silence_timeout", self.slider_timeout.value() / 10.0)
        config.set("hotkey", self.combo_hotkey.currentText().lower())
        config.set("run_minimized", self.check_tray.isChecked())
        config.set("llm_provider", self.combo_llm_provider.currentText())
        config.set("llm_model", self.combo_llm_model.currentText())
        config.set("llm_api_key", self.input_llm_api_key.text())
        self.settings_saved.emit()
