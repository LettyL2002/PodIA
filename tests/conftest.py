
import pytest

def pytest_configure(config):
    """Register custom marks."""
    config.addinivalue_line("markers", "initialization: tests for initialization")
    config.addinivalue_line("markers", "responses: tests for response generation")
    config.addinivalue_line("markers", "script_generation: tests for script generation")
    config.addinivalue_line("markers", "messages: tests for message handling")