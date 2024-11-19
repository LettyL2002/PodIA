import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from utils.url_processor import URLProcessor


@pytest.fixture
def url_processor():
    with patch('utils.url_processor.VideoProcessor') as mock_video_processor:
        # Create a mock instance that will be returned when VideoProcessor is instantiated
        mock_instance = MagicMock()
        mock_video_processor.return_value = mock_instance
        processor = URLProcessor("fake-api-key")
        # Now processor.video_processor is our mock instance
        yield processor


@pytest.fixture
def youtube_url():
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def video_id():
    return "dQw4w9WgXcQ"


@pytest.fixture
def transcript_text():
    return "Test transcript text"


@pytest.fixture
def audio_path(tmp_path):
    return str(tmp_path / "test_audio.mp3")


def test_init(url_processor):
    assert isinstance(url_processor.video_processor, MagicMock)
    assert isinstance(url_processor.download_path, Path)


@patch('yt_dlp.YoutubeDL')
def test_download_video(mock_ytdl, url_processor, youtube_url):
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = {"title": "Test Video"}
    mock_ytdl.return_value.__enter__.return_value = mock_instance

    result = url_processor.download_video(youtube_url)
    assert isinstance(result, str)
    assert result.endswith(".mp3")


@patch('yt_dlp.YoutubeDL')
def test_download_video_error(mock_ytdl, url_processor, youtube_url):
    mock_ytdl.side_effect = Exception("Download error")
    result = url_processor.download_video(youtube_url)
    assert "Error en el procesamiento" in result


@patch('docs.youtube_processor.YoutubeProcessor.get_video_id')
@patch('docs.youtube_processor.YoutubeProcessor.download_transcript')
def test_process_youtube_url_direct_transcript(mock_download_transcript, mock_get_video_id, url_processor, youtube_url, video_id, transcript_text):
    mock_get_video_id.return_value = video_id
    mock_download_transcript.return_value = transcript_text

    result = url_processor.process_youtube_url(youtube_url)
    assert "Transcripción obtenida directamente" in result
    assert transcript_text in result


@patch('docs.youtube_processor.YoutubeProcessor.get_video_id')
def test_process_youtube_url_invalid_url(mock_get_video_id, url_processor, youtube_url):
    mock_get_video_id.return_value = None
    result = url_processor.process_youtube_url(youtube_url)
    assert result == "URL inválida"


@patch('docs.youtube_processor.YoutubeProcessor.get_video_id')
@patch('docs.youtube_processor.YoutubeProcessor.download_transcript')
@patch.object(URLProcessor, 'download_video')
@patch('os.remove')  # Add mock for os.remove
def test_process_youtube_url_fallback_to_download(mock_remove, mock_download_video, mock_download_transcript, mock_get_video_id,
                                                  url_processor, youtube_url, video_id, audio_path, transcript_text):
    mock_get_video_id.return_value = video_id
    mock_download_transcript.side_effect = Exception("No direct transcript")
    mock_download_video.return_value = audio_path
    url_processor.video_processor.process_media.return_value = ("transcript.txt", transcript_text)

    result = url_processor.process_youtube_url(youtube_url)
    assert "Transcripción generada por IA" in result
    assert transcript_text in result
    mock_remove.assert_called_once_with(audio_path)  # Verify os.remove was called


@patch('docs.youtube_processor.YoutubeProcessor.get_video_id')
@patch('docs.youtube_processor.YoutubeProcessor.download_transcript')
@patch.object(URLProcessor, 'download_video')
def test_process_youtube_url_download_error(mock_download_video, mock_download_transcript, mock_get_video_id,
                                            url_processor, youtube_url, video_id):
    mock_get_video_id.return_value = video_id
    mock_download_transcript.side_effect = Exception("No direct transcript")
    mock_download_video.side_effect = Exception("Download failed")

    result = url_processor.process_youtube_url(youtube_url)
    assert "Error en el procesamiento" in result


if __name__ == "__main__":
    pytest.main(["-v"])
