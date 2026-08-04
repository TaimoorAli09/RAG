import fitz


def extract_text_from_pdf(file_path):

    pdf = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(pdf):

        text = page.get_text()

        pages.append({"page_number": page_number + 1, "text": text})

    pdf.close()

    return pages
