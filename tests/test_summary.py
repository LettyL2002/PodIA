import pytest
from unittest.mock import patch, MagicMock
from core.summary import SummaryGenerator


@pytest.fixture
def api_key():
    return "test-api-key"


@pytest.fixture
def sample_text():
    return "This is a sample text to summarize"


@pytest.fixture
def sample_summary():
    return """
    Tema principal: Texto de prueba
    Ideas principales:
    1. Primera idea
    2. Segunda idea
    3. Tercera idea
    
    Puntos clave:
    - Punto 1
    - Punto 2
    
    Citas destacadas:
    - "Cita de prueba"
    
    Resumen para debate:
    Este es un resumen de prueba.
    """


@pytest.fixture
def summary_generator(api_key):
    return SummaryGenerator(api_key)


def test_summary_generator_init(api_key):
    generator = SummaryGenerator(api_key)
    assert generator.client.api_key == api_key

@patch('openai.OpenAI')
def test_generate_summary_error(mock_openai, summary_generator, sample_text):
    # Configure mock to raise an exception
    mock_openai.return_value.chat.completions.create.side_effect = Exception(
        "API Error")

    # Test that the error is raised
    with pytest.raises(Exception):
        summary_generator.generate_summary(sample_text)


def test_summary_generator_empty_key():
    with pytest.raises(Exception):
        SummaryGenerator("")


if __name__ == "__main__":
    pytest.main(["-v"])
