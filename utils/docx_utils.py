from docx import Document


def process_docx(file_path, max_records=None):
    doc = Document(file_path)
    data = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            data.append({"paragraph": text})
            if max_records is not None and len(data) >= max_records:
                break

    return data
