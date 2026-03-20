import os
import json
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QTextEdit, QHeaderView,
    QFrame, QScrollArea
)
from PySide6.QtCore import Qt

# ─── Light Theme Colors ──────────────────────────────────────────────────────
C_BG         = "#F8F9FC"
C_FG         = "#221F1C"
C_CARD       = "#FFFFFF"
C_SECONDARY  = "#F5EDCF"
C_MUTED      = "#F2EFE9"
C_MUTED_FG   = "#857F79"
C_BORDER     = "#E9E4DD"

def get_base_path():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'vocynx')
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class FeatureItem(QFrame):
    """Feature list item with checkmark icon."""
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background-color: transparent; border: none; }")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)
        
        lbl_check = QLabel("✓")
        lbl_check.setStyleSheet("font-size: 13px; border: none;")
        lbl_check.setFixedWidth(20)
        layout.addWidget(lbl_check)
        
        lbl_text = QLabel(label)
        lbl_text.setStyleSheet(f"font-size: 13px; color: {C_FG}; border: none;")
        layout.addWidget(lbl_text, 1)


class DetailRow(QFrame):
    """Key-value detail row."""
    def __init__(self, key, value, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { background-color: transparent; border: none; }")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(0)
        
        lbl_key = QLabel(key)
        lbl_key.setStyleSheet(f"font-size: 13px; color: {C_MUTED_FG}; border: none;")
        layout.addWidget(lbl_key)
        layout.addStretch()
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {C_FG}; border: none;")
        layout.addWidget(lbl_val)


class LicensesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("licensesView")
        self.setStyleSheet(f"""
            QWidget#licensesView {{ 
                background-color: {C_BG}; 
            }}
            QWidget {{
                color: {C_FG}; 
                font-family: 'Inter', 'Segoe UI', sans-serif; 
            }}
            QTableWidget {{
                background-color: {C_CARD};
                color: {C_FG};
                border: 1px solid {C_BORDER};
                border-radius: 8px;
                gridline-color: {C_BORDER};
                font-size: 12px;
            }}
            QTableWidget::item {{ padding: 8px; }}
            QTableWidget::item:selected {{ background-color: {C_MUTED}; color: {C_FG}; }}
            QHeaderView::section {{
                background-color: {C_CARD};
                color: {C_MUTED_FG};
                border: none;
                border-bottom: 1px solid {C_BORDER};
                padding: 8px;
                font-weight: 700;
                font-size: 10px;
                letter-spacing: 1px;
            }}
            QTextEdit {{
                background-color: {C_CARD};
                color: {C_MUTED_FG};
                border: 1px solid {C_BORDER};
                border-radius: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                padding: 12px;
                font-size: 11px;
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

        self.licenses_data = []
        self.licenses_dir = os.path.join(get_base_path(), "licenses")

        self.setup_ui()
        self.load_licenses()

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
        layout.setSpacing(0)
        
        # ── Header ──
        header = QHBoxLayout()
        header.setSpacing(8)
        lbl_h1 = QLabel("License")
        lbl_h1.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {C_FG};")
        header.addWidget(lbl_h1)
        header.addStretch()
        layout.addLayout(header)
        layout.addSpacing(24)
        
        # ── Current Plan Card ──
        plan_card = QFrame()
        plan_card.setStyleSheet(f"""
            QFrame {{
                background-color: {C_SECONDARY};
                border-radius: 16px;
                border: none;
            }}
        """)
        plan_layout = QVBoxLayout(plan_card)
        plan_layout.setContentsMargins(20, 20, 20, 20)
        plan_layout.setSpacing(8)
        
        plan_header = QHBoxLayout()
        plan_header.setSpacing(8)
        lbl_name = QLabel("Vocynx")
        lbl_name.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {C_FG}; border: none;")
        lbl_badge = QLabel("Open Source")
        lbl_badge.setStyleSheet(f"""
            font-size: 9px; font-weight: 700; 
            color: {C_MUTED_FG}; 
            background-color: {C_MUTED}; 
            padding: 2px 8px; 
            border-radius: 8px; 
            border: none;
        """)
        plan_header.addWidget(lbl_name)
        plan_header.addWidget(lbl_badge)
        plan_header.addStretch()
        plan_layout.addLayout(plan_header)
        
        lbl_plan_desc = QLabel("Vocynx is free and open source. All features are available to everyone.")
        lbl_plan_desc.setWordWrap(True)
        lbl_plan_desc.setStyleSheet(f"font-size: 12px; color: {C_MUTED_FG}; border: none;")
        plan_layout.addWidget(lbl_plan_desc)
        
        layout.addWidget(plan_card)
        layout.addSpacing(20)
        
        # ── License Details Card ──
        details_card = QFrame()
        details_card.setStyleSheet(f"""
            QFrame {{
                background-color: {C_CARD};
                border-radius: 12px;
                border: 1px solid {C_BORDER};
            }}
        """)
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(16, 16, 16, 16)
        details_layout.setSpacing(2)
        
        lbl_details_title = QLabel("LICENSE DETAILS")
        lbl_details_title.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {C_MUTED_FG}; letter-spacing: 1.5px; border: none;")
        details_layout.addWidget(lbl_details_title)
        details_layout.addSpacing(8)
        
        details_layout.addWidget(DetailRow("License Type", "MIT License"))
        details_layout.addWidget(DetailRow("Repository", "https://github.com/Natnael-crypto/Vocynx"))
        details_layout.addWidget(DetailRow("First Release", "2026"))
        details_layout.addWidget(DetailRow("Cost", "Free forever"))
        
        layout.addWidget(details_card)
        layout.addSpacing(20)
        
        # ── Included Features Card ──
        features_card = QFrame()
        features_card.setStyleSheet(f"""
            QFrame {{
                background-color: {C_CARD};
                border-radius: 12px;
                border: 1px solid {C_BORDER};
            }}
        """)
        features_layout = QVBoxLayout(features_card)
        features_layout.setContentsMargins(16, 16, 16, 16)
        features_layout.setSpacing(2)
        
        lbl_features_title = QLabel("INCLUDED FEATURES")
        lbl_features_title.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {C_MUTED_FG}; letter-spacing: 1.5px; border: none;")
        features_layout.addWidget(lbl_features_title)
        features_layout.addSpacing(8)
        
        features = [
            "Unlimited transcriptions",
            "All Whisper models (tiny, base, small)",
            "LLM refinement (OpenAI, Groq)",
            "Real-time translation",
            "Custom hotkey support",
            "Priority support",
        ]
        for f in features:
            features_layout.addWidget(FeatureItem(f))
        
        layout.addWidget(features_card)
        layout.addSpacing(20)
        
        # ── Enterprise CTA Card ──
        cta_card = QFrame()
        cta_card.setStyleSheet(f"""
            QFrame {{
                background-color: {C_CARD};
                border-radius: 12px;
                border: 1px solid {C_BORDER};
            }}
        """)
        cta_layout = QHBoxLayout(cta_card)
        cta_layout.setContentsMargins(16, 16, 16, 16)
        cta_layout.setSpacing(12)

        
        
        layout.addWidget(cta_card)
        layout.addSpacing(24)
        
        # ── Open Source Libraries ──
        lbl_libs_title = QLabel("OPEN SOURCE LIBRARIES")
        lbl_libs_title.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {C_MUTED_FG}; letter-spacing: 1.5px;")
        layout.addWidget(lbl_libs_title)
        layout.addSpacing(12)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Library", "License"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(180)
        self.table.setMaximumHeight(250)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)
        layout.addSpacing(12)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setMinimumHeight(200)
        self.text_area.setMaximumHeight(350)
        layout.addWidget(self.text_area)
        
        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def load_licenses(self):
        json_path = os.path.join(self.licenses_dir, "licenses.json")
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.licenses_data = json.load(f)
        except Exception as e:
            self.text_area.setText(f"Failed to load licenses.json: {e}")
            return

        self.table.setRowCount(len(self.licenses_data))
        for row, pkg in enumerate(self.licenses_data):
            self.table.setItem(row, 0, QTableWidgetItem(pkg.get("name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(pkg.get("license", "")))

        if len(self.licenses_data) > 0:
            self.table.selectRow(0)

    def on_selection_changed(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        pkg = self.licenses_data[row]
        filename = pkg.get("file", "")
        
        if not filename:
            self.text_area.setText("No license file specified.")
            return

        file_path = os.path.join(self.licenses_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.text_area.setText(f.read())
        except Exception as e:
            self.text_area.setText(f"Failed to load {filename}: {e}")
