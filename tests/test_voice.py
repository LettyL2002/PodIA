import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch
from core.voice import VoiceGenerator


@pytest.fixture
def voice_generator():
    return VoiceGenerator(api_key="test_key")


@pytest.fixture
def sample_script():
    return json.dumps({
        "dialogue": [
            {
                "character": "Anfitrion",
                "message": "Test message 1"
            },
            {
                "character": "Participante",
                "message": "Test message 2"
            }
        ]
    })


def test_init(voice_generator):
    assert voice_generator.model == "tts-1"
    assert voice_generator.pause_duration == 1000
    assert voice_generator.tittle == "1"
    assert len(voice_generator.characters) == 2


def test_update_model(voice_generator):
    voice_generator.update_model("new-model")
    assert voice_generator.model == "new-model"


def test_get_voice_for_character(voice_generator):
    assert voice_generator._get_voice_for_character("Anfitrion") == "onyx"
    assert voice_generator._get_voice_for_character("Participante") == "nova"
    assert voice_generator._get_voice_for_character("Unknown") == "alloy"


@patch('core.voice.VoiceGenerator.process_script')
@patch('core.voice.VoiceGenerator.concatenate_audio_files')
def test_generate_podcast(mock_concatenate, mock_process, voice_generator, sample_script):
    mock_process.return_value = [{"audio_path": "test1.mp3"}]
    mock_concatenate.return_value = "final_podcast.mp3"

    result = voice_generator.generate_podcast(sample_script)

    assert isinstance(result, Path)
    assert str(result) == "final_podcast.mp3"


def test_generate_podcast_empty(voice_generator):
    result = voice_generator.generate_podcast("{}")
    assert result == ""
