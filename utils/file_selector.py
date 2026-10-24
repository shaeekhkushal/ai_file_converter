import sys

from PyQt6.QtWidgets import QApplication, QFileDialog


def select_file():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select a file",
        "",
        "Supported files (*.xlsx *.xls *.csv *.txt *.log *.md *.docx);;"
        "All files (*)",
    )
    return file_path
