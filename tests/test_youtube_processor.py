import pytest
from unittest.mock import patch, MagicMock

# docs/test_youtube_processor.py


@pytest.fixture
def youtube_url():
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def video_id():
    return "dQw4w9WgXcQ"


@pytest.fixture
def video_title():
    return "Rick Astley - Never Gonna Give You Up (Video)"


@pytest.fixture
def transcript_text():
    return "We're no strangers to love\nYou know the rules and so do I"


def test_get_video_id(youtube_url, video_id):
    from docs.youtube_processor import YoutubeProcessor
    assert YoutubeProcessor.get_video_id(youtube_url) == video_id


@patch('requests.get')
def test_get_video_title(mock_get, video_id, video_title):
    from docs.youtube_processor import YoutubeProcessor
    mock_response = MagicMock()
    mock_response.text = f"<title>{video_title} - YouTube</title>"
    mock_get.return_value = mock_response

    assert YoutubeProcessor.get_video_title(video_id) == video_title


@patch('youtube_transcript_api.YouTubeTranscriptApi.list_transcripts')
def test_download_transcript(mock_list_transcripts, video_id, transcript_text):
    from docs.youtube_processor import YoutubeProcessor
    mock_transcript = MagicMock()
    mock_transcript.fetch.return_value = [{"text": transcript_text}]
    mock_transcript_list = MagicMock()
    mock_transcript_list.find_generated_transcript.return_value = mock_transcript
    mock_list_transcripts.return_value = mock_transcript_list

    result = YoutubeProcessor.download_transcript(video_id)
    assert transcript_text in result


@patch('builtins.open', new_callable=MagicMock)
@patch('os.makedirs')
@patch('docs.youtube_processor.YoutubeProcessor.download_transcript')
@patch('docs.youtube_processor.YoutubeProcessor.get_video_title')
def test_process_video(mock_get_video_title, mock_download_transcript, mock_makedirs, mock_open, youtube_url, video_id, video_title, transcript_text):
    from docs.youtube_processor import YoutubeProcessor
    mock_get_video_title.return_value = video_title
    mock_download_transcript.return_value = transcript_text

    result = YoutubeProcessor.process_video(youtube_url)

    assert "Transcripcion guardada en" in result
    assert transcript_text in result
    mock_open.assert_called_once()
    mock_makedirs.assert_called_once()


def test_get_video_id_invalid_url():
    from docs.youtube_processor import YoutubeProcessor
    invalid_url = "https://www.invalidurl.com/watch?v=invalid"
    assert YoutubeProcessor.get_video_id(invalid_url) is None


@patch('youtube_transcript_api.YouTubeTranscriptApi.list_transcripts')
def test_download_transcript_error(mock_list_transcripts, video_id):
    from docs.youtube_processor import YoutubeProcessor
    mock_list_transcripts.side_effect = Exception("Error")
    result = YoutubeProcessor.download_transcript(video_id)
    assert result is None


if __name__ == "__main__":
    pytest.main(["-v"])
