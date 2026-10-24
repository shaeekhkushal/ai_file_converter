# File Converter

A desktop application for previewing and converting Excel, CSV, text, Markdown,
and Word documents to JSON. The application uses PyQt6 and works with native
desktop file dialogs; it does not require a web service or network connection.

## Requirements

- Python 3.10 or newer
- A supported desktop environment for PyQt6 (Windows, macOS, or Linux)

## Install

Create and activate a virtual environment, then install the application
dependencies:

**Windows (PowerShell)**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**macOS and Linux**

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Launch

From the repository root, run:

```sh
python main.py
```

Choose a file, review the preview, select **Convert to JSON**, and choose where
to save the output. By default, the suggested output is named
`<input-filename>.json` beside the source file.

`gui_pyqt.py` contains the PyQt window and is not a separate launch command.
`gui_tkinter.py` is a deprecated compatibility command that starts the same
PyQt application; use `python main.py` for new launch scripts and shortcuts.

## Supported formats

- `.xlsx`: Excel workbooks, including the existing merged-cell handling
- `.xls`: legacy Excel workbooks, read through `xlrd`
- `.csv`: CSV files
- `.txt`, `.log`, `.md`: UTF-8 text files
- `.docx`: Word documents
- `.pdf`: PDF documents (text extracted per page)
- `.ppt`, `.pptx`: PowerPoint presentations (text extracted per slide)

Excel files are converted sheet by sheet. CSV rows and non-empty text lines are
represented as JSON records; Word paragraph text is also preserved as records.
The preview is intentionally limited to a small sample and does not alter the
conversion output.

## Project layout

```text
main.py                 Canonical application launcher
gui_pyqt.py             PyQt desktop interface
gui_tkinter.py          Deprecated launcher compatibility shim
utils/
  csv_utils.py          CSV data processing
  docx_utils.py         Word document processing
  excel_utils.py        Excel data processing
  file_selector.py      Native Qt file-selection helper
  json_writer.py        Conversion dispatch and JSON output
  text_utils.py         Text data processing
requirements.txt        Direct runtime dependencies
```

Conversion writes to a temporary file in the destination directory and replaces
the destination only after JSON serialization succeeds. The source path cannot
be used as the output path.

## Tests

There is currently no automated test suite in this repository.
