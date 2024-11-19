import pytest
import os
from unittest.mock import mock_open, patch, MagicMock

@pytest.fixture
def pdf_processor():
    from docs.pdf_processor import PDFProcessor  # Import inside the fixture
    return PDFProcessor()


@pytest.fixture
def sample_pdf_content():
    return "Sample PDF text\nPage 1\nPage 2"


def test_init_creates_output_directory(pdf_processor):
    assert os.path.exists(pdf_processor.output_path)


@patch('docs.pdf_processor.PdfReader')
def test_extract_text_success(mock_pdfreader, pdf_processor, sample_pdf_content):
    # Configure mock
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample PDF text"
    mock_pdfreader.return_value.pages = [mock_page, mock_page]

    with patch('builtins.open', mock_open()) as mock_file:
        result = pdf_processor.extract_text("test.pdf")

    assert "Transcripción guardada en:" in result
    assert "Sample PDF text\nSample PDF text" in result
    mock_file.assert_called_once()


def test_extract_text_file_not_found(pdf_processor):
    with pytest.raises(FileNotFoundError):
        pdf_processor.extract_text("nonexistent.pdf")


@patch('docs.pdf_processor.PdfReader')
def test_process_pdf(mock_pdfreader, pdf_processor):
    # Create mock file object
    mock_file = MagicMock()
    mock_file.name = "test.pdf"

    # Configure PdfReader mock
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Sample PDF text"
    mock_pdfreader.return_value.pages = [mock_page]

    with patch('builtins.open', mock_open()):
        result = pdf_processor.process_pdf(mock_file)

    assert "Transcripción guardada en:" in result
    assert "Sample PDF text" in result


def test_output_file_naming(pdf_processor):
    test_pdf = "test_document.pdf"
    expected_output = os.path.join(
        pdf_processor.output_path,
        "test_document_transcripcion.txt"
    )

    with patch('docs.pdf_processor.PdfReader') as mock_reader, \
            patch('builtins.open', mock_open()) as mock_file:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "test content"
        mock_reader.return_value.pages = [mock_page]

        pdf_processor.extract_text(test_pdf)

    mock_file.assert_called_with(expected_output, "w", encoding="utf-8")


def test_output_file_content(pdf_processor):
    test_pdf = "test_document.pdf"
    expected_content = "test content"

    with patch('docs.pdf_processor.PdfReader') as mock_reader, \
            patch('builtins.open', mock_open()) as mock_file:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = expected_content
        mock_reader.return_value.pages = [mock_page]

        pdf_processor.extract_text(test_pdf)

    mock_file().write.assert_called_with(expected_content + "\n")


if __name__ == "__main__":
    pytest.main(["-v"])
