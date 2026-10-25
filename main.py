import argparse
import sys
from pathlib import Path

from services.conversion import convert_file


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert supported documents to JSON. Run without an input to open the desktop app."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="file to convert; omit this argument to open the desktop app",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="directory for the JSON output (defaults to the input file's directory)",
    )
    parser.add_argument(
        "--output-name",
        help="JSON filename only, without directory components (defaults to input.json)",
    )
    parser.add_argument(
        "--max-records",
        type=_positive_int,
        help="maximum rows, paragraphs, pages, or slides per section; default is unlimited",
    )
    return parser


def _run_gui() -> int:
    from PyQt6.QtWidgets import QApplication

    from gui_pyqt import FileConverterApp

    app = QApplication(sys.argv)
    app.setApplicationName("File Converter")
    window = FileConverterApp()
    window.show()
    return app.exec()


def main() -> int:
    parser = _create_parser()
    args = parser.parse_args()

    if args.input_file is None:
        if args.output_dir is not None or args.output_name is not None or args.max_records is not None:
            parser.error("CLI options require an input file.")
        return _run_gui()

    try:
        result = convert_file(
            args.input_file,
            output_directory=args.output_dir,
            output_name=args.output_name,
            max_records=args.max_records,
        )
    except Exception as error:
        print(f"Conversion failed: {error}", file=sys.stderr)
        return 1

    print(f"Conversion complete: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
