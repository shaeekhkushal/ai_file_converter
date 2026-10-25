from pathlib import Path

from services.conversion import convert_file


def file_to_json(
    input_file: str | Path,
    output_file: str | Path,
    max_records: int | None = None,
) -> Path:
    """Compatibility wrapper for JSON output beside the input file."""
    input_path = Path(input_file).expanduser().resolve(strict=True)
    output_path = Path(output_file).expanduser()
    if output_path.parent.resolve() != input_path.parent:
        raise ValueError(
            "The compatibility API only writes beside the input file. "
            "Use services.conversion.convert_file for another output directory."
        )
    return convert_file(
        input_path,
        output_directory=input_path.parent,
        output_name=output_path.name,
        max_records=max_records,
    )
