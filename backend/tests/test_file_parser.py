from app.tools.file_parser import parse_file_contents


def test_parse_plain_text():
    content = b"Course 1: Machine Learning\nCourse 2: Systems Programming"
    result = parse_file_contents("syllabus.txt", content)
    assert "Machine Learning" in result
    assert "Systems Programming" in result


def test_parse_pdf():
    # Minimal PDF bytes for testing
    import io
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    pdf_bytes_io = io.BytesIO()
    writer.write(pdf_bytes_io)
    pdf_bytes = pdf_bytes_io.getvalue()

    result = parse_file_contents("resume.pdf", pdf_bytes)
    assert isinstance(result, str)
