import logging
from collections.abc import Callable
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from utils.dependencies import load_optional_dependency
from services.conversion import convert_file


logger = logging.getLogger(__name__)


class FileConverterApp(QWidget):
    def __init__(
        self,
        converter: Callable[
            [str | Path, str | Path | None, str | None, int | None], Path
        ] = convert_file,
    ):
        super().__init__()
        self.converter = converter
        self.file_path: Path | None = None
        self.setObjectName("appRoot")
        self.setWindowTitle("File Converter")
        self.setMinimumSize(720, 560)
        self.resize(860, 680)
        self._build_ui()
        self.apply_theme()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        heading = QVBoxLayout()
        heading.setSpacing(4)
        title = QLabel("File Converter")
        title.setObjectName("title")
        title.setAccessibleName("File Converter")
        subtitle = QLabel("Turn spreadsheets and documents into structured JSON.")
        subtitle.setObjectName("subtitle")
        subtitle.setAccessibleName("Application description")
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
        self.file_label.setAccessibleName("Selected input file")
        self.file_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.file_label.setWordWrap(True)
        self.select_button = QPushButton("Browse files")
        self.select_button.setObjectName("secondaryButton")
        self.select_button.setAccessibleName("Browse for an input file")
        self.select_button.setAccessibleDescription(
            "Choose a supported file to preview and convert."
        )
        self.select_button.clicked.connect(self.select_file)
        self.select_button.setShortcut(QKeySequence(QKeySequence.StandardKey.Open))
        file_row.addWidget(self.file_label, 1)
        file_row.addWidget(self.select_button)
        input_layout.addLayout(file_row)
        limit_row = QHBoxLayout()
        limit_label = QLabel("Maximum records per section (0 = all)")
        limit_label.setAccessibleName("Maximum converted records")
        self.max_records = QSpinBox()
        self.max_records.setObjectName("maxRecords")
        self.max_records.lineEdit().setObjectName("maxRecordsEditor")
        self.max_records.setRange(0, 1_000_000)
        self.max_records.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.max_records.setMinimumWidth(110)
        self.max_records.setAccessibleName("Maximum records per section")
        self.max_records.setAccessibleDescription(
            "Limit rows, paragraphs, pages, or slides in each section. "
            "Zero converts all records."
        )
        self.max_records.setToolTip(
            "Limits rows, paragraphs, pages, or slides in each section. "
            "Set to 0 to convert all records."
        )
        limit_row.addWidget(limit_label)
        limit_row.addStretch()
        limit_row.addWidget(self.max_records)
        input_layout.addLayout(limit_row)
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
        preview_hint.setAccessibleName("Preview help")
        preview_heading.addWidget(preview_title)
        preview_heading.addStretch()
        preview_heading.addWidget(preview_hint)
        preview_layout.addLayout(preview_heading)

        self.preview_area = QPlainTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setAccessibleName("Selected file preview")
        self.preview_area.setAccessibleDescription(
            "Read-only preview of the selected file contents."
        )
        self.preview_area.setPlaceholderText(
            "Your file preview will appear here after you choose a file."
        )
        self.preview_area.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        preview_layout.addWidget(self.preview_area, 1)
        layout.addWidget(preview_card, 1)

        footer = QHBoxLayout()
        self.status_label = QLabel(
            "Supported formats: CSV, Excel, text, Markdown, Word, PDF, and PowerPoint"
        )
        self.status_label.setObjectName("muted")
        self.status_label.setAccessibleName("Application status")
        self.status_label.setWordWrap(True)
        self.convert_button = QPushButton("Convert to JSON")
        self.convert_button.setObjectName("primaryButton")
        self.convert_button.setAccessibleName("Convert selected file to JSON")
        self.convert_button.setAccessibleDescription(
            "Choose an output location and convert the selected file."
        )
        self.convert_button.setEnabled(False)
        self.convert_button.clicked.connect(self.convert_file)
        self.convert_button.setShortcut(QKeySequence(QKeySequence.StandardKey.Save))
        self.theme_button = QPushButton("Dark mode")
        self.theme_button.setObjectName("secondaryButton")
        self.theme_button.setCheckable(True)
        self.theme_button.setAccessibleName("Toggle dark theme")
        self.theme_button.setAccessibleDescription(
            "Switch between light and dark application themes."
        )
        self.theme_button.toggled.connect(self.apply_theme)
        footer.addWidget(self.status_label, 1)
        footer.addWidget(self.theme_button)
        footer.addWidget(self.convert_button)
        layout.addLayout(footer)

    def apply_theme(self, dark_mode: bool | None = None):
        if dark_mode is not None and hasattr(self, "theme_button"):
            self.theme_button.setChecked(dark_mode)
        dark = self.theme_button.isChecked() if hasattr(self, "theme_button") else False
        self.theme_colors = {
            "background": "#111827" if dark else "#f3f5f9",
            "foreground": "#e5e7eb" if dark else "#1e293b",
            "title": "#f8fafc" if dark else "#111827",
            "muted": "#94a3b8" if dark else "#64748b",
            "card": "#1f2937" if dark else "#ffffff",
            "border": "#374151" if dark else "#e2e8f0",
            "field": "#111827" if dark else "#f8fafc",
            "field_foreground": "#e2e8f0" if dark else "#334155",
            "selection": "#3730a3" if dark else "#c7d2fe",
            "button_border": "#4b5563" if dark else "#cbd5e1",
            "button_foreground": "#e5e7eb" if dark else "#334155",
            "disabled_foreground": "#9ca3af" if dark else "#94a3b8",
            "disabled_background": "#374151" if dark else "#e2e8f0",
        }
        self.setStyleSheet(self._application_stylesheet())
        self.theme_button.setText("Light mode" if dark else "Dark mode")
        self.theme_button.setAccessibleDescription(
            "Switch to the light theme." if dark else "Switch to the dark theme."
        )

    def _application_stylesheet(self) -> str:
        colors = self.theme_colors
        return f"""
            QWidget {{
                color: {colors["foreground"]};
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 10pt;
            }}
            QWidget#appRoot {{ background: {colors["background"]}; }}
            QLabel#title {{
                color: {colors["title"]};
                font-size: 23pt;
                font-weight: 700;
            }}
            QLabel#subtitle, QLabel#muted {{ color: {colors["muted"]}; }}
            QFrame#card {{
                background: {colors["card"]};
                border: 1px solid {colors["border"]};
                border-radius: 12px;
            }}
            QLabel#sectionTitle {{
                color: {colors["foreground"]};
                font-size: 11pt;
                font-weight: 600;
            }}
            QLabel#fileLabel {{
                color: {colors["field_foreground"]};
                background: {colors["field"]};
                border: 1px solid {colors["border"]};
                border-radius: 7px;
                padding: 10px 12px;
            }}
            QPlainTextEdit {{
                background: {colors["field"]};
                color: {colors["field_foreground"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                padding: 10px;
                selection-background-color: {colors["selection"]};
                font-family: "Cascadia Code", "SFMono-Regular", monospace;
                font-size: 9pt;
            }}
            QLineEdit#maxRecordsEditor {{
                color: {colors["field_foreground"]};
                background: {colors["field"]};
                border: none;
                selection-background-color: {colors["selection"]};
            }}
            QSpinBox#maxRecords {{
                color: {colors["field_foreground"]};
                background: {colors["field"]};
                border: 1px solid {colors["border"]};
                border-radius: 7px;
                padding: 2px 4px;
            }}
            QSpinBox#maxRecords::up-button, QSpinBox#maxRecords::down-button {{
                width: 16px;
                background: {colors["card"]};
                border: none;
            }}
            QSpinBox#maxRecords::up-arrow, QSpinBox#maxRecords::down-arrow {{
                width: 8px;
                height: 8px;
                color: {colors["button_foreground"]};
            }}
            QPushButton {{
                border: 1px solid {colors["button_border"]};
                border-radius: 7px;
                padding: 9px 16px;
                font-weight: 600;
            }}
            QPushButton#primaryButton {{
                color: #ffffff;
                background: #4f46e5;
                border-color: #4f46e5;
            }}
            QPushButton#primaryButton:hover {{
                background: #4338ca;
                border-color: #4338ca;
            }}
            QPushButton#primaryButton:disabled {{
                color: {colors["disabled_foreground"]};
                background: {colors["disabled_background"]};
                border-color: {colors["disabled_background"]};
            }}
            QPushButton#secondaryButton {{
                color: {colors["button_foreground"]};
                background: {colors["card"]};
            }}
            QPushButton#secondaryButton:hover {{
                background: {colors["field"]};
                border-color: #94a3b8;
            }}
            QPushButton:focus {{ border: 2px solid #818cf8; }}
        """

    def select_file(self):
        filters = (
            "Supported files (*.xlsx *.xls *.csv *.txt *.log *.md *.docx *.pdf *.ppt *.pptx);;"
            "Excel files (*.xlsx *.xls);;CSV files (*.csv);;"
            "Text files (*.txt *.log *.md);;Word files (*.docx);;"
            "PDF files (*.pdf);;PowerPoint files (*.ppt *.pptx);;All files (*)"
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
                if extension == ".xls":
                    load_optional_dependency("xlrd", "xlrd")
                else:
                    load_optional_dependency("openpyxl", "openpyxl")
                pandas = load_optional_dependency("pandas", "pandas")
                data_frame = pandas.read_excel(file_path, sheet_name=0, nrows=5)
                preview_text = data_frame.to_string(index=False)
            elif extension == ".docx":
                docx = load_optional_dependency("docx", "python-docx")
                document = docx.Document(file_path)
                paragraphs = [
                    paragraph.text.strip()
                    for paragraph in document.paragraphs
                    if paragraph.text.strip()
                ]
                preview_text = "\n".join(paragraphs[:5])
            elif extension == ".pdf":
                pdf_module = load_optional_dependency("PyPDF2", "PyPDF2")
                reader = pdf_module.PdfReader(file_path)
                preview_text = "\n".join(
                    page.extract_text() or "" for page in reader.pages[:3]
                )[:1000]
            elif extension in {".ppt", ".pptx"}:
                pptx = load_optional_dependency("pptx", "python-pptx")
                presentation = pptx.Presentation(file_path)
                preview_text = "\n".join(
                    shape.text.strip()
                    for slide in list(presentation.slides)[:3]
                    for shape in slide.shapes
                    if getattr(shape, "text", "").strip()
                )[:1000]
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
        colors = self.theme_colors
        dialog.setStyleSheet(
            f"""
            QDialog#messageDialog {{
                background: {colors["background"]};
                color: {colors["foreground"]};
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 10pt;
            }}
            QFrame#messageCard {{
                background: {colors["card"]};
                border: 1px solid {colors["border"]};
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
                color: {colors["title"]};
                font-size: 14pt;
                font-weight: 700;
            }}
            QLabel#messageBody {{
                color: {colors["muted"]};
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

        default_output = self.file_path.with_suffix(".json")
        output_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save JSON file",
            str(default_output),
            "JSON files (*.json);;All files (*)",
        )
        if not output_name:
            return

        output_path = Path(output_name)
        if output_path.suffix.lower() != ".json":
            output_path = output_path.with_suffix(".json")

        try:
            max_records = self.max_records.value() or None
            output_path = self.converter(
                self.file_path,
                output_path.parent,
                output_path.name,
                max_records,
            )
        except Exception as error:
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
