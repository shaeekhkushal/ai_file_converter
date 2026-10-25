def process_text(file_path, max_records=None):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                data.append({"line": line})
                if max_records is not None and len(data) >= max_records:
                    break
    return data
