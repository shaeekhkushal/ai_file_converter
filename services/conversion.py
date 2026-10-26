import json
import logging
import os
import tempfile
import time
from importlib import import_module
from pathlib import Path

from utils.dependencies import MissingDependencyError, load_optional_dependency


logger = logging.getLogger("ai_file_converter.conversion")


PROCESSORS = {
    ".xlsx": ("utils.excel_utils", "process_excel", ("openpyxl", "pandas")),
    ".xls": ("utils.excel_utils", "process_excel", ("xlrd", "pandas")),
    ".csv": ("utils.csv_utils", "process_csv", ()),
    ".txt": ("utils.text_utils", "process_text", ()),
    ".log": ("utils.text_utils", "process_text", ()),
    ".md": ("utils.text_utils", "process_text", ()),
    ".docx": ("utils.docx_utils", "process_docx", ("python-docx",)),
    ".pdf": ("utils.pdf_utils", "process_pdf", ("PyPDF2",)),
    ".ppt": ("utils.ppt_utils", "process_ppt", ("python-pptx",)),
    ".pptx": ("utils.ppt_utils", "process_ppt", ("python-pptx",)),
}

IMPORT_NAMES = {
    "python-docx": "docx",
    "python-pptx": "pptx",
}


def _resolve_output_path(output_directory: str | Path, output_name: str) -> Path:
    directory = Path(output_directory).expanduser().resolve(strict=True)
    if not directory.is_dir():
        raise NotADirectoryError(f"Output directory does not exist: {directory}")

    if (
        not output_name
        or output_name in {".", ".."}
        or "/" in output_name
        or "\\" in output_name
        or Path(output_name).is_absolute()
    ):
        raise ValueError("Output filename must be a single filename, not a path.")

    filename = Path(output_name)
    if filename.suffix.lower() != ".json":
        filename = filename.with_suffix(".json")

    output_path = (directory / filename).resolve()
    if output_path.parent != directory:
        raise ValueError("Output file must be directly inside the selected directory.")
    return output_path


def _convert_file(
    input_file: str | Path,
    output_directory: str | Path | None = None,
    output_name: str | None = None,
    max_records: int | None = None,
) -> Path:
    """Convert a supported file, saving JSON under an explicitly selected directory.

    ``max_records`` limits rows, paragraphs, pages, or slides in each relevant
    section. ``None`` converts all available records.
    """
    input_path = Path(input_file).expanduser().resolve(strict=True)
    target_directory = (
        Path(output_directory).expanduser()
        if output_directory is not None
        else input_path.parent
    )
    target_name = output_name or input_path.with_suffix(".json").name
    output_path = _resolve_output_path(target_directory, target_name)
    if input_path == output_path:
        raise ValueError("The JSON output path must not overwrite the input file.")
    if max_records is not None and max_records < 1:
        raise ValueError("max_records must be a positive integer or None.")

    processor = PROCESSORS.get(input_path.suffix.lower())
    if processor is None:
        extension = input_path.suffix.lower() or "(none)"
        raise ValueError(f"Unsupported file format: {extension}")
    module_name, function_name, required_packages = processor

    for package_name in required_packages:
        module_to_import = IMPORT_NAMES.get(package_name, package_name)
        load_optional_dependency(module_to_import, package_name)

    try:
        converter_module = import_module(module_name)
    except ModuleNotFoundError as error:
        missing_package = error.name or module_name
        raise MissingDependencyError(missing_package) from error
    convert = getattr(converter_module, function_name)
    data = convert(input_path, max_records=max_records)

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


def convert_file(
    input_file: str | Path,
    output_directory: str | Path | None = None,
    output_name: str | None = None,
    max_records: int | None = None,
) -> Path:
    """Convert a file and log duration and file-size metrics."""
    started_at = time.perf_counter()
    source_path = Path(input_file).expanduser()
    input_format = source_path.suffix.lower() or "(none)"

    try:
        input_size_bytes = source_path.stat().st_size
        output_path = _convert_file(
            input_file,
            output_directory=output_directory,
            output_name=output_name,
            max_records=max_records,
        )
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "conversion_completed format=%s input_size_bytes=%d "
            "output_size_bytes=%d duration_ms=%.2f max_records=%s",
            input_format,
            input_size_bytes,
            output_path.stat().st_size,
            elapsed_ms,
            max_records if max_records is not None else "unlimited",
        )
        return output_path
    except Exception:
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.exception(
            "conversion_failed format=%s duration_ms=%.2f",
            input_format,
            elapsed_ms,
        )
        raise
