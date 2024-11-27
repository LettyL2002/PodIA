import pytest
from unittest.mock import MagicMock, patch
from core.script import ScriptGenerator
from core.characters.anfitrion import Anfitrion
from core.characters.participante1 import Participante1
from utils.constants import SCRIPT_MODEL, DEFAULT_NUM_EXCHANGES
import json

@pytest.fixture
def api_key():
    return "test_api_key"

@pytest.fixture
def script_generator(api_key):
    return ScriptGenerator(api_key=api_key)

@pytest.fixture
def mock_openai_response():
    def _create_mock(content):
        return MagicMock(
            choices=[MagicMock(
                message=MagicMock(content=content)
            )]
        )
    return _create_mock

@pytest.mark.initialization
class TestScriptGeneratorInitialization:
    def test_initialization(self, script_generator, api_key):
        assert script_generator.anfitrion_ai.api_key == api_key
        assert script_generator.participante_ai.api_key == api_key
        assert isinstance(script_generator.anfitrion, Anfitrion)
        assert isinstance(script_generator.participante, Participante1)
        assert script_generator.conversation == []
        assert script_generator.anfitrion_messages == []
        assert script_generator.participante_messages == []
        assert script_generator.model == SCRIPT_MODEL

    def test_update_model(self, script_generator):
        new_model = "gpt-3.5-turbo"
        script_generator.update_model(new_model)
        assert script_generator.model == new_model

@pytest.mark.responses
class TestResponseGeneration:
    @patch('core.script.OpenAI')
    def test_generate_anfitrion_response(self, mock_openai, script_generator, mock_openai_response):
        expected_response = "Anfitrion response"
        mock_chat = MagicMock()
        mock_completions = MagicMock()
        mock_completions.create.return_value = mock_openai_response(expected_response)
        mock_chat.completions = mock_completions
        script_generator.anfitrion_ai.chat = mock_chat
        
        response = script_generator._generate_anfitrion_response("Test prompt")
        assert response == expected_response

    @patch('core.script.OpenAI')
    def test_generate_participante_response(self, mock_openai, script_generator, mock_openai_response):
        expected_response = "Participante response"
        mock_chat = MagicMock()
        mock_completions = MagicMock()
        mock_completions.create.return_value = mock_openai_response(expected_response)
        mock_chat.completions = mock_completions
        script_generator.participante_ai.chat = mock_chat
        
        response = script_generator._generate_participante_response("Test prompt")
        assert response == expected_response

@pytest.mark.script_generation
class TestScriptGeneration:
    @pytest.fixture
    def mock_responses(self):
        return {
            'anfitrion': [
                "Anfitrion initial response",
                "Anfitrion response 1",
                "Anfitrion response 2",
                "Anfitrion despedida"
            ],
            'participante': [
                "Participante response 1",
                "Participante response 2"
            ]
        }

    @patch('core.script.ScriptGenerator._generate_anfitrion_response')
    @patch('core.script.ScriptGenerator._generate_participante_response')
    def test_generate_complete_script(
        self, mock_participante_resp, mock_anfitrion_resp,
        script_generator, mock_responses
    ):
        mock_anfitrion_resp.side_effect = mock_responses['anfitrion']
        mock_participante_resp.side_effect = mock_responses['participante']
        
        script = script_generator.generate_script("Test summary", 2)
        script_dict = json.loads(script)
        
        assert isinstance(script_dict, dict)
        assert "title" in script_dict
        assert "dialogue" in script_dict
        assert len(script_dict["dialogue"]) > 0
        
        # Verify conversation flow
        dialogue = script_dict["dialogue"]
        assert dialogue[0]["character"] == "Anfitrion"
        assert dialogue[1]["character"] == "Participante"

@pytest.mark.messages
class TestMessageRetrieval:
    def test_get_messages(self, script_generator):
        # Test anfitrion messages
        test_anfitrion_msgs = ["Message 1", "Message 2"]
        script_generator.anfitrion_messages = test_anfitrion_msgs
        assert script_generator.get_anfitrion_messages() == test_anfitrion_msgs

        # Test participante messages
        test_participante_msgs = ["Message A", "Message B"]
        script_generator.participante_messages = test_participante_msgs
        assert script_generator.get_participante_messages() == test_participante_msgs

    def test_get_conversation(self, script_generator):
        test_conversation = [
            ("Anfitrion", "[Anfitrion] Hello"),
            ("Participante", "[Participante] Hi")
        ]
        script_generator.conversation = test_conversation
        assert script_generator.get_conversation() == test_conversation

    def test_format_script(self, script_generator):
        script_generator.conversation = [
            ("Anfitrion", "[Anfitrion] Welcome"),
            ("Participante", "[Participante] Thanks")
        ]
        formatted = json.loads(script_generator._format_script())
        
        assert formatted["title"] == "GUION DEL PODCAST"
        assert len(formatted["dialogue"]) == 2
        assert formatted["dialogue"][0]["character"] == "Anfitrion"
        assert formatted["dialogue"][0]["message"] == "Welcome"
