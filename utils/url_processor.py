from pathlib import Path
import gradio as gr  # type: ignore
import yt_dlp  # type: ignore
from audio.video_processor import VideoProcessor
import os
import re
from docs.youtube_processor import YoutubeProcessor


class URLProcessor:
    def __init__(self, openai_api_key: str) -> None:
        """
        Inicializa el procesador con una instancia de VideoProcessor.

        Args:
            openai_api_key (str): Clave de API de OpenAI para procesamiento de video.
        """
        self.video_processor = VideoProcessor(openai_api_key)
        self.download_path = Path("../temp/")
        self.download_path.mkdir(parents=True, exist_ok=True)

    def download_video(self, youtube_url: str) -> str:
        """
        Descarga solo el audio de un video de YouTube.

        Args:
            youtube_url (str): URL del video de YouTube a descargar.

        Returns:
            str: Ruta al archivo de audio descargado.
        """
        try:
            # First extract info without downloading
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                # Sanitize filename: remove special characters and spaces
                safe_title = re.sub(r'[^\w_-]', '_', info['title'])

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
                'outtmpl': str(self.download_path / f"{safe_title}"),
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
                video_path = str(self.download_path / f"{safe_title}.mp3")
                return video_path

        except Exception as e:
            return f"Error en el procesamiento: {str(e)}"

    def process_youtube_url(self, youtube_url: str, progress=gr.Progress()) -> str:
        """
        Procesa una URL de YouTube para obtener su transcripción.

        Intenta obtener la transcripción directamente. Si no está disponible,
        descarga y procesa el audio para generar la transcripción.

        Args:
            youtube_url (str): URL del video de YouTube.
            progress: Objeto de progreso de Gradio para actualizar el progreso.

        Returns:
            str: Transcripción del video o mensaje de error.
        """
        video_id = YoutubeProcessor.get_video_id(youtube_url)
        if not video_id:
            return "URL inválida"

        try:
            # Primero intenta obtener la transcripción directamente
            transcript_text = YoutubeProcessor.download_transcript(
                video_id, language=["es"])
            if transcript_text:
                return f"Transcripción obtenida directamente:\n\n{transcript_text}"
            else:
                raise FileExistsError("Transcripción no disponible")

        except Exception as e:
            print(f"No se pudo obtener transcripción directa: {str(e)}")
            try:
                # Descargar y procesar el audio si la transcripción no está disponible
                print("Descargando audio para procesamiento...")
                progress(0.1, "Descargando audio...")
                audio_path = self.download_video(youtube_url)
                progress(0.5, "Audio descargado. Procesando...")

                # Procesa el audio usando VideoProcessor
                transcript_path, transcript = self.video_processor.process_media(
                    audio_path)
                progress(1.0, "Procesamiento completado.")

                # Elimina el archivo de audio descargado
                os.remove(audio_path)

                return f"Transcripción generada por IA:\n\nArchivo guardado en: {transcript_path}\n\n{transcript}"

            except Exception as e:
                return f"Error en el procesamiento: {str(e)}"


# Propósito de desarrollo
if __name__ == "__main__":
    from utils.env_loader import load_environment_variables, OPENAI_API_KEY
    load_environment_variables()
    print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
    processor = URLProcessor(str(OPENAI_API_KEY))

    interface = gr.Interface(
        fn=processor.process_youtube_url,
        inputs=gr.Textbox(label="URL de YouTube"),
        outputs=gr.Textbox(label="Resultado"),
        title="Procesador de Videos de YouTube",
        description="Ingresa una URL de YouTube para obtener su transcripción (directa o mediante IA)",
    )

    interface.launch()
