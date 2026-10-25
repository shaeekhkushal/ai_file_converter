import csv
from itertools import islice


def process_csv(file_path, max_records=None):
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = []
        rows = reader if max_records is None else islice(reader, max_records)
        for row in rows:
            row_data = {k: v for k, v in row.items() if v}
            if row_data:
                data.append(row_data)
    return data
