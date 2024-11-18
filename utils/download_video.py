from pathlib import Path
import gradio as gr  # type: ignore
import yt_dlp  # type: ignore
from audio.video_processor import VideoProcessor
import os
from docs.youtube_processor import YoutubeProcessor


class YouTubeDownloadProcessor:
    def __init__(self, openai_api_key):
        """Initialize processor with VideoProcessor instance"""
        self.video_processor = VideoProcessor(openai_api_key)
        self.download_path = Path("../temp/")
        self.download_path.mkdir(parents=True, exist_ok=True)

    def download_video(self, youtube_url):
        """Download YouTube video"""
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                video_path = ydl.prepare_filename(info)
                return video_path

        except Exception as e:
            return f"Error en el procesamiento: {str(e)}"

    def process_youtube_url(self, youtube_url, progress=gr.Progress()):
        """Main processing function"""
        video_id = YoutubeProcessor.get_video_id(youtube_url)
        if not video_id:
            return "URL inválida"

        try:
            # First try to get transcript directly
            transcript_text = YoutubeProcessor.download_transcript(
                video_id, language=["en"])
            if transcript_text:
                return f"Transcripción obtenida directamente:\n\n{transcript_text}"
            else:
                raise FileExistsError("Transcripción no disponible")

        except Exception as e:
            print(f"No se pudo obtener transcripción directa: {str(e)}")
            try:
                # Download and process video if transcript not available
                print("Descargando video para procesamiento...")
                progress(0.1, "Descargando video...")
                video_path = self.download_video(youtube_url)
                progress(0.5, "Video descargado. Procesando...")

                # Process video using VideoProcessor
                transcript_path, transcript = self.video_processor.process_video(
                    video_path)
                progress(1.0, "Procesamiento completado.")

                # Clean up downloaded video
                os.remove(video_path)

                return f"Transcripción generada por IA:\n\nArchivo guardado en: {transcript_path}\n\n{transcript}"

            except Exception as e:
                return f"Error en el procesamiento: {str(e)}"


# ? Dev Purpose
if __name__ == "__main__":
    from utils.env_loader import load_environment_variables, OPENAI_API_KEY
    load_environment_variables()
    print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
    processor = YouTubeDownloadProcessor(OPENAI_API_KEY)

    interface = gr.Interface(
        fn=processor.process_youtube_url,
        inputs=gr.Textbox(label="URL de YouTube"),
        outputs=gr.Textbox(label="Resultado"),
        title="Procesador de Videos de YouTube",
        description="Ingresa una URL de YouTube para obtener su transcripción (directa o mediante IA)",
    )

    interface.launch()
