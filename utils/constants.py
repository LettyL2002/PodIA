from typing import Literal

# Voice configurations
MALE_VOICES: list[Literal['onyx', 'echo', 'fable']] = [
    'onyx', 'echo', 'fable']
FEMALE_VOICES: list[Literal['nova', 'shimmer', 'alloy']] = [
    'nova', 'shimmer', 'alloy']

# Model options
AVAILABLE_TRANSCRIPT_MODELS = ["whisper-1"]
AVAILABLE_SUMMARY_MODELS = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo",
                            "gpt-4o-mini", "gpt-4o", "gpt-4o-realtime-preview", "chatgpt-4o-latest"]
AVAILABLE_SCRIPT_MODELS = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo",
                           "gpt-4o", "gpt-4o-realtime-preview", "chatgpt-4o-latest"]
AVAILABLE_VOICE_MODELS = ["tts-1", "tts-1-hd"]

# Model configurations
TRANSCRIPT_MODEL = "whisper-1"  # Default model for text processing
SUMMARY_MODEL = "gpt-4o-mini"  # Default model for summary generation
SCRIPT_MODEL = "gpt-4o-mini"  # Default model for script generation
VOICE_MODEL = "tts-1"  # Default model for voice generation

# ? Extras ( No enable to modify)

# Interface configurations
DEFAULT_NUM_EXCHANGES = 1  # Default number of exchanges in podcast script

# Pause duration in milliseconds
PAUSE_DURATION = 1000  # Default pause duration in milliseconds

# Constants for input types
URL_INPUT = "🌐 URL"
PDF_INPUT = "📄 PDF"
VIDEO_INPUT = "🎥 Video/Audio"


def get_pronouns(gender: Literal["male", "female"]) -> dict[str, str]:
    return {
        'subject': 'he' if gender == "male" else 'she',
        'object': 'him' if gender == "male" else 'her',
        'possessive': 'his' if gender == "male" else 'her',
        'gender_noun': 'boy' if gender == "male" else 'girl'
    }
