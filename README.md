# File Converter

A cross-platform PyQt6 desktop application and command-line tool for converting
documents and tabular files to JSON. Conversion is handled by a reusable
service that can be called from the desktop UI or other Python code.

## Requirements and installation

- Python 3.10 or newer
- Windows, macOS, or Linux for the graphical application

Create a virtual environment and install the pinned dependencies.

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

## Usage

Launch the desktop application:

```sh
python main.py
```

Choose an input file, review the preview, set an optional record limit, select
**Convert to JSON**, and choose an output location. The default filename replaces
the source extension (`report.csv` becomes `report.json`). The save dialog lets
you choose a different output folder.

The same entry point supports headless command-line conversion. When no output
name is provided, the input basename with a `.json` extension is used:

```sh
python main.py report.csv
python main.py report.xlsx --output-dir ./converted --output-name quarterly.json
python main.py report.pdf --max-records 20
```

`--output-dir` chooses the destination directory. `--output-name` accepts a
filename only, not a path; directory components such as `../` are rejected.
When no output directory is provided, JSON is saved beside the input file.
`--max-records` is optional and caps rows, paragraphs, pages, or slides in each
relevant section. By default, all records are converted.

The conversion service can also be used from Python:

```python
from services.conversion import convert_file

output_path = convert_file(
    "report.csv",
    output_directory="./converted",
    output_name="report.json",
    max_records=1000,
)
```

## Supported formats

| Input | Required format-specific packages | JSON representation |
|---|---|---|
| `.csv` | None | Non-empty rows as objects keyed by the header row |
| `.txt`, `.log`, `.md` | None | Non-empty lines as `{"line": ...}` records |
| `.xlsx` | `openpyxl`, `pandas` | A mapping of worksheet names to row objects |
| `.xls` | `xlrd`, `pandas` | A mapping of worksheet names to row objects |
| `.docx` | `python-docx` | Non-empty paragraphs as `{"paragraph": ...}` records |
| `.pdf` | `PyPDF2` | Extractable page text as page records |
| `.ppt`, `.pptx` | `python-pptx` | Non-empty slide text as slide records |

Format-specific packages are imported only for the format being processed. If a
required package is missing, conversion reports its name and installation
command. Install the complete supported dependency set with
`python -m pip install -r requirements.txt`.

## Output safety and conversion limits

- The output directory must already exist and is selected explicitly by the
  user or caller. The output filename is restricted to one filename component,
  normalized to `.json`, and cannot overwrite the input file.
- JSON is written to a temporary file in the selected destination directory and
  replaces the destination only after serialization succeeds.
- `--max-records` limits extracted records per worksheet or document section.
  For `.xlsx`, a limit enables read-only row iteration to reduce workbook
  conversion memory use. With no limit, the existing full-workbook behavior is
  retained, including merged-cell handling.
- The cap limits extracted output records; it is not a hard memory or file-size
  limit. PDF and PowerPoint libraries may load document structures while
  parsing, and the generated JSON records are still held before serialization.
- PDF conversion extracts selectable text only. It does not OCR scanned pages.
- The preview is a small sample; it does not determine the full conversion
  output.

## Project layout

```text
main.py                    GUI launcher and CLI
gui_pyqt.py                PyQt desktop UI
services/conversion.py     Shared conversion service
utils/                     Format processors and dependency helpers
requirements.txt           Pinned direct runtime dependencies
```

`utils/json_writer.py` retains a compatibility wrapper for existing callers
that save beside the input file. New integrations that need a custom destination
should use `services.conversion.convert_file` and pass the output directory and
filename separately.

## Logging

The application writes a rotating local log with conversion success/failure,
input and output sizes, selected format, record limit, and elapsed time.
Successful conversion metrics do not include source or destination paths, and
the application does not send telemetry to a remote service. Error tracebacks
can include diagnostic details from the underlying file libraries. Logs are
stored in the platform's user data location:

- Windows: `%LOCALAPPDATA%\AIFileConverter\Logs`
- macOS: `~/Library/Logs/AIFileConverter`
- Linux: `$XDG_STATE_HOME/ai-file-converter/logs`, or
  `~/.local/state/ai-file-converter/logs` when `XDG_STATE_HOME` is unset

The active log is `application.log`; up to three rotated files are retained.

## Development and contributions

1. Create and activate a virtual environment, then install development
   dependencies with `python -m pip install -r requirements-dev.txt`.
2. Keep format processing in `utils/` and reusable orchestration in
   `services/conversion.py`; avoid adding conversion behavior to the UI.
3. Preserve the desktop and CLI workflows when changing shared conversion
   behavior, and add focused tests for new processors and safety rules.
4. Run the checks with `python -m pytest`. GitHub Actions runs the suite on
   pushes and pull requests using Python 3.10 and 3.12.
5. Before submitting a change, review the diff. Do not commit virtual
   environments, caches, local secrets, or generated conversion output.
