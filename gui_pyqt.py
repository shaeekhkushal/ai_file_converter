import logging
from pathlib import Path

import pandas as pd
from docx import Document
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from utils.json_writer import file_to_json


logger = logging.getLogger(__name__)


class FileConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path: Path | None = None
        self.setObjectName("appRoot")
        self.setWindowTitle("File Converter")
        self.setMinimumSize(720, 560)
        self.resize(860, 680)
        self.setStyleSheet(
            """
            QWidget {
                color: #1e293b;
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 10pt;
            }
            QWidget#appRoot {
                background: #f3f5f9;
            }
            QLabel#title {
                color: #111827;
                font-size: 23pt;
                font-weight: 700;
            }
            QLabel#subtitle, QLabel#muted {
                color: #64748b;
            }
            QFrame#card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
            QLabel#sectionTitle {
                color: #334155;
                font-size: 11pt;
                font-weight: 600;
            }
            QLabel#fileLabel {
                color: #475569;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 7px;
                padding: 10px 12px;
            }
            QPlainTextEdit {
                background: #f8fafc;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
                selection-background-color: #c7d2fe;
                font-family: "Cascadia Code", "SFMono-Regular", monospace;
                font-size: 9pt;
            }
            QPushButton {
                border: 1px solid #cbd5e1;
                border-radius: 7px;
                padding: 9px 16px;
                font-weight: 600;
            }
            QPushButton#primaryButton {
                color: #ffffff;
                background: #4f46e5;
                border-color: #4f46e5;
            }
            QPushButton#primaryButton:hover {
                background: #4338ca;
                border-color: #4338ca;
            }
            QPushButton#primaryButton:disabled {
                color: #94a3b8;
                background: #e2e8f0;
                border-color: #e2e8f0;
            }
            QPushButton#secondaryButton {
                color: #334155;
                background: #ffffff;
            }
            QPushButton#secondaryButton:hover {
                background: #f8fafc;
                border-color: #94a3b8;
            }
            QPushButton:focus {
                border: 2px solid #818cf8;
            }
            """
        )
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        heading = QVBoxLayout()
        heading.setSpacing(4)
        title = QLabel("File Converter")
        title.setObjectName("title")
        subtitle = QLabel("Turn spreadsheets and documents into structured JSON.")
        subtitle.setObjectName("subtitle")
        heading.addWidget(title)
        heading.addWidget(subtitle)
        layout.addLayout(heading)

        input_card = QFrame()
        input_card.setObjectName("card")
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(20, 18, 20, 18)
        input_layout.setSpacing(12)
        input_title = QLabel("1. Choose a file")
        input_title.setObjectName("sectionTitle")
        input_layout.addWidget(input_title)

        file_row = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("fileLabel")
        self.file_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.file_label.setWordWrap(True)
        self.select_button = QPushButton("Browse files")
        self.select_button.setObjectName("secondaryButton")
        self.select_button.clicked.connect(self.select_file)
        file_row.addWidget(self.file_label, 1)
        file_row.addWidget(self.select_button)
        input_layout.addLayout(file_row)
        layout.addWidget(input_card)

        preview_card = QFrame()
        preview_card.setObjectName("card")
        preview_layout = QVBoxLayout(preview_card)
        preview_layout.setContentsMargins(20, 18, 20, 20)
        preview_layout.setSpacing(12)
        preview_heading = QHBoxLayout()
        preview_title = QLabel("2. Review preview")
        preview_title.setObjectName("sectionTitle")
        preview_hint = QLabel("A small sample of the selected file")
        preview_hint.setObjectName("muted")
        preview_heading.addWidget(preview_title)
        preview_heading.addStretch()
        preview_heading.addWidget(preview_hint)
        preview_layout.addLayout(preview_heading)

        self.preview_area = QPlainTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText(
            "Your file preview will appear here after you choose a file."
        )
        self.preview_area.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        preview_layout.addWidget(self.preview_area, 1)
        layout.addWidget(preview_card, 1)

        footer = QHBoxLayout()
        self.status_label = QLabel("Supported formats: CSV, Excel, text, Markdown, and Word")
        self.status_label.setObjectName("muted")
        self.status_label.setWordWrap(True)
        self.convert_button = QPushButton("Convert to JSON")
        self.convert_button.setObjectName("primaryButton")
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self.convert_file)
        footer.addWidget(self.status_label, 1)
        footer.addWidget(self.convert_button)
        layout.addLayout(footer)

    def select_file(self):
        filters = (
            "Supported files (*.xlsx *.xls *.csv *.txt *.log *.md *.docx);;"
            "Excel files (*.xlsx *.xls);;CSV files (*.csv);;"
            "Text files (*.txt *.log *.md);;Word files (*.docx);;All files (*)"
        )
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose a file", "", filters)
        if not file_name:
            return

        self.file_path = Path(file_name)
        self.file_label.setText(str(self.file_path))
        self.convert_button.setEnabled(True)
        self.preview_data(self.file_path)

    def preview_data(self, file_path: Path):
        try:
            extension = file_path.suffix.lower()
            if extension in {".xlsx", ".xls"}:
                data_frame = pd.read_excel(file_path, sheet_name=0, nrows=5)
                preview_text = data_frame.to_string(index=False)
            elif extension == ".docx":
                document = Document(file_path)
                paragraphs = [
                    paragraph.text.strip()
                    for paragraph in document.paragraphs
                    if paragraph.text.strip()
                ]
                preview_text = "\n".join(paragraphs[:5])
            else:
                try:
                    with file_path.open("r", encoding="utf-8") as source:
                        preview_text = source.read(1000)
                except UnicodeDecodeError:
                    with file_path.open("r", encoding="ISO-8859-1") as source:
                        preview_text = source.read(1000)
            self.preview_area.setPlainText(
                preview_text or "The selected file contains no previewable content."
            )
            self.status_label.setText("File ready to convert.")
        except Exception as error:
            logger.exception("Unable to preview selected file")
            self.preview_area.clear()
            self.status_label.setText("Preview could not be loaded.")
            self._show_message(
                "Preview unavailable",
                f"The selected file could not be previewed:\n{error}",
                kind="warning",
            )

    def _show_message(self, title: str, message: str, kind: str = "info"):
        styles = {
            "info": ("✓", "#dcfce7", "#15803d"),
            "warning": ("!", "#fef3c7", "#b45309"),
            "error": ("×", "#fee2e2", "#b91c1c"),
        }
        icon, icon_background, icon_color = styles[kind]

        dialog = QDialog(self)
        dialog.setObjectName("messageDialog")
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        dialog.setMinimumWidth(440)
        dialog.setStyleSheet(
            f"""
            QDialog#messageDialog {{
                background: #f3f5f9;
                color: #1e293b;
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 10pt;
            }}
            QFrame#messageCard {{
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }}
            QLabel#messageIcon {{
                background: {icon_background};
                color: {icon_color};
                border-radius: 21px;
                font-size: 20pt;
                font-weight: 700;
            }}
            QLabel#messageTitle {{
                color: #111827;
                font-size: 14pt;
                font-weight: 700;
            }}
            QLabel#messageBody {{
                color: #64748b;
            }}
            QPushButton#primaryButton {{
                color: #ffffff;
                background: #4f46e5;
                border: 1px solid #4f46e5;
                border-radius: 7px;
                padding: 9px 18px;
                font-weight: 600;
            }}
            QPushButton#primaryButton:hover {{
                background: #4338ca;
                border-color: #4338ca;
            }}
            QPushButton#primaryButton:focus {{
                border: 2px solid #818cf8;
            }}
            """
        )

        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.setContentsMargins(20, 20, 20, 18)
        dialog_layout.setSpacing(18)

        card = QFrame()
        card.setObjectName("messageCard")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(14)

        icon_label = QLabel(icon)
        icon_label.setObjectName("messageIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(42, 42)
        card_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignTop)

        message_layout = QVBoxLayout()
        message_layout.setSpacing(7)
        title_label = QLabel(title)
        title_label.setObjectName("messageTitle")
        body_label = QLabel(message)
        body_label.setObjectName("messageBody")
        body_label.setWordWrap(True)
        body_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        message_layout.addWidget(title_label)
        message_layout.addWidget(body_label)
        card_layout.addLayout(message_layout, 1)
        dialog_layout.addWidget(card)

        button_row = QHBoxLayout()
        button_row.addStretch()
        close_button = QPushButton("Done")
        close_button.setObjectName("primaryButton")
        close_button.clicked.connect(dialog.accept)
        button_row.addWidget(close_button)
        dialog_layout.addLayout(button_row)

        close_button.setDefault(True)
        dialog.adjustSize()
        dialog.exec()

    def convert_file(self):
        if self.file_path is None:
            self._show_message(
                "Choose a file",
                "Select a file before converting.",
                kind="warning",
            )
            return

        default_output = self.file_path.with_name(f"{self.file_path.name}.json")
        output_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save JSON file",
            str(default_output),
            "JSON files (*.json);;All files (*)",
        )
        if not output_name:
            return

        try:
            output_path = file_to_json(self.file_path, Path(output_name))
        except Exception as error:
            logger.exception("Unable to convert selected file")
            self.status_label.setText("Conversion failed.")
            self._show_message(
                "Conversion failed",
                f"The file could not be converted:\n{error}",
                kind="error",
            )
            return

        self.status_label.setText(f"JSON saved to {output_path}")
        self._show_message(
            "Conversion complete",
            f"Your JSON file was saved to:\n{output_path}",
        )
