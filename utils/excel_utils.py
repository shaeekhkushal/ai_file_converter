from pathlib import Path

from utils.dependencies import load_optional_dependency


def get_value_from_merged_cell(sheet, cell):
    for merged_range in sheet.merged_cells.ranges:
        if cell.coordinate in merged_range:
            return sheet.cell(merged_range.min_row, merged_range.min_col).value
    return cell.value


def process_excel(file_path, max_records=None):
    pandas = load_optional_dependency("pandas", "pandas")
    if Path(file_path).suffix.lower() == ".xls":
        data_frames = pandas.read_excel(
            file_path,
            sheet_name=None,
            nrows=None if max_records is None else max_records,
        )
        return {
            sheet_name: frame.dropna(how='all').to_dict('records')
            for sheet_name, frame in data_frames.items()
        }

    openpyxl = load_optional_dependency("openpyxl", "openpyxl")
    wb = openpyxl.load_workbook(
        file_path,
        data_only=True,
        read_only=max_records is not None,
    )

    try:
        if max_records is None and any(sheet.tables for sheet in wb.worksheets):
            df = pandas.read_excel(file_path, sheet_name=None)
            return {
                sheet_name: frame.dropna(how='all').to_dict('records')
                for sheet_name, frame in df.items()
            }

        if max_records is not None:
            data = {}
            for sheet_name in wb.sheetnames:
                worksheet = wb[sheet_name]
                rows = worksheet.iter_rows(values_only=True)
                headers = next(rows, ())
                last_values = {header: None for header in headers}
                sheet_data = []

                for row_number, row in enumerate(rows):
                    if row_number >= max_records:
                        break
                    row_data = {}
                    for header, value in zip(headers, row):
                        if value is None and last_values[header] is not None:
                            value = last_values[header]
                        elif value is not None:
                            last_values[header] = value
                        if value is not None:
                            row_data[header] = value
                    if row_data:
                        sheet_data.append(row_data)
                data[sheet_name] = sheet_data
            return data

        data = {}
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            headers = [get_value_from_merged_cell(ws, cell) for cell in ws[1]]
            last_values = {header: None for header in headers}
            sheet_data = []

            for row in ws.iter_rows(min_row=2):
                row_data = {}
                for header, cell in zip(headers, row):
                    value = get_value_from_merged_cell(ws, cell)
                    if value is None and last_values[header] is not None:
                        value = last_values[header]
                    elif value is not None:
                        last_values[header] = value
                    else:
                        continue
                    row_data[header] = value
                if row_data:
                    sheet_data.append(row_data)

            data[sheet] = sheet_data

        return data
    finally:
        wb.close()
