import sys

from PyQt6.QtWidgets import QApplication

from gui_pyqt import FileConverterApp


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("File Converter")
    window = FileConverterApp()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
