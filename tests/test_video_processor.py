import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path


@pytest.fixture
def video_processor():
    from audio.video_processor import VideoProcessor
    return VideoProcessor("fake-api-key")


@pytest.fixture
def sample_video_path():
    return "test_video.mp4"


@pytest.fixture
def sample_audio_path():
    return "test_audio.mp3"


@pytest.fixture
def sample_transcript():
    return "This is a test transcript"


def test_init(video_processor):
    assert video_processor.client is not None
    assert isinstance(video_processor.transcript_path, Path)


@patch('pathlib.Path.mkdir')
def test_init_creates_directory(mock_mkdir):
    from audio.video_processor import VideoProcessor
    VideoProcessor("fake-api-key")
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


@patch('moviepy.editor.VideoFileClip')
def test_extract_audio(mock_videoclip, video_processor, sample_video_path):
    from audio.video_processor import VideoProcessor
    mock_video = MagicMock()
    mock_audio = MagicMock()
    mock_videoclip.return_value = mock_video
    mock_video.audio = mock_audio

    output_path = video_processor.extract_audio(sample_video_path)

    mock_videoclip.assert_called_once_with(sample_video_path)
    mock_audio.write_audiofile.assert_called_once()
    mock_video.close.assert_called_once()
    assert isinstance(output_path, str)


@patch('openai.OpenAI')
def test_transcribe_audio(mock_openai, video_processor, sample_audio_path, sample_transcript):
    from audio.video_processor import VideoProcessor
    mock_client = MagicMock()
    mock_transcription = MagicMock()
    mock_transcription.text = sample_transcript
    mock_client.audio.transcriptions.create.return_value = mock_transcription
    video_processor.client = mock_client

    with patch('builtins.open', mock_open()):
        result = video_processor.transcribe_audio(sample_audio_path)

    assert result == sample_transcript
    mock_client.audio.transcriptions.create.assert_called_once()


@patch('audio.video_processor.VideoProcessor.extract_audio')
@patch('audio.video_processor.VideoProcessor.transcribe_audio')
@patch('audio.video_processor.VideoProcessor.save_transcript')
@patch('os.remove')
def test_process_video(mock_remove, mock_save, mock_transcribe, mock_extract,
                      video_processor, sample_video_path, sample_transcript):
    mock_extract.return_value = "temp_audio.mp3"
    mock_transcribe.return_value = sample_transcript
    mock_save.return_value = "transcript.txt"

    _, transcript = video_processor.process_video(sample_video_path)

    mock_extract.assert_called_once_with(sample_video_path)
    mock_transcribe.assert_called_once_with("temp_audio.mp3")
    mock_save.assert_called_once_with(sample_transcript, sample_video_path)
    mock_remove.assert_called_once_with("temp_audio.mp3")
    assert transcript == sample_transcript


@patch('audio.video_processor.VideoProcessor.transcribe_audio')
@patch('audio.video_processor.VideoProcessor.save_transcript')
def test_process_audio(mock_save, mock_transcribe, video_processor,
                      sample_audio_path, sample_transcript):
    mock_transcribe.return_value = sample_transcript
    mock_save.return_value = "transcript.txt"

    _, transcript = video_processor.process_audio(sample_audio_path)

    mock_transcribe.assert_called_once_with(sample_audio_path)
    mock_save.assert_called_once_with(sample_transcript, sample_audio_path)
    assert transcript == sample_transcript


@patch('audio.video_processor.VideoProcessor.process_video')
@patch('audio.video_processor.VideoProcessor.process_audio')
def test_process_media(mock_process_audio, mock_process_video, video_processor):
    video_path = "test.mp4"
    audio_path = "test.mp3"

    video_processor.process_media(video_path)
    mock_process_video.assert_called_once_with(video_path)

    video_processor.process_media(audio_path)
    mock_process_audio.assert_called_once_with(audio_path)


def test_save_transcript(video_processor, sample_transcript):
    from audio.video_processor import VideoProcessor
    video_name = "test_video.mp4"

    with patch('builtins.open', mock_open()) as mock_file:
        output_path = video_processor.save_transcript(
            sample_transcript, video_name)

    mock_file.assert_called_once_with(
        video_processor.transcript_path / "test_video_transcript.txt",
        "w",
        encoding="utf-8"
    )
    mock_file().write.assert_called_once_with(sample_transcript)
    assert isinstance(output_path, str)


if __name__ == "__main__":
    pytest.main(["-v"])
