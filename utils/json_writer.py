import json
import os
import tempfile
from pathlib import Path

from utils.excel_utils import process_excel
from utils.csv_utils import process_csv
from utils.text_utils import process_text
from utils.pdf_utils import process_pdf
from utils.ppt_utils import process_ppt
from utils.docx_utils import process_docx


def file_to_json(input_file: str | Path, output_file: str | Path) -> Path:
    input_path = Path(input_file).expanduser().resolve(strict=True)
    output_path = Path(output_file).expanduser().resolve()
    file_extension = input_path.suffix.lower()

    if input_path == output_path:
        raise ValueError("The JSON output path must not overwrite the input file.")

    if file_extension in ['.xlsx', '.xls']:
        data = process_excel(input_path)
    elif file_extension == '.csv':
        data = process_csv(input_path)
    elif file_extension in ['.txt', '.log', '.md']:
        data = process_text(input_path)
    elif file_extension == '.docx':
        data = process_docx(input_path)
    elif file_extension == '.pdf':
        data = process_pdf(input_path)
    elif file_extension in ['.ppt', '.pptx']:
        data = process_ppt(input_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension or '(none)'}")

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_path.parent,
            prefix=f".{output_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(data, temporary_file, indent=4, ensure_ascii=False)
            temporary_file.write("\n")
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return output_path
