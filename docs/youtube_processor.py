# docs/youtube_processor.py
from pathlib import Path
import gradio as gr  # type: ignore
from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
from youtube_transcript_api.formatters import TextFormatter  # type: ignore
import requests  # type: ignore
import re
import os


class YoutubeProcessor:
    @staticmethod
    def get_video_id(youtube_url) -> str | None:
        """
        Extrae el ID del video de una URL de YouTube.
        Args:
            youtube_url (str): La URL de YouTube.
        Returns:
            str: El ID del video extraído o None si no se encuentra.
        """
        pattern = (
            r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
        )
        match = re.search(pattern, youtube_url)
        return match.group(1) if match else None

    @staticmethod
    def get_video_title(video_id) -> str:
        """
        Obtiene el título del video de YouTube.
        Args:
            video_id (str): El ID del video de YouTube.
        Returns:
            str: El título del video o "Unknown" si no se encuentra.
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            matches = re.findall(r'<title>(.*?)</title>', response.text)
            return matches[0].replace(" - YouTube", "") if matches else "Unknown"
        except requests.RequestException as e:
            print(f"Error al intentar obtener el título del video: {e}")
            return "Unknown"

    @staticmethod
    def download_transcript(video_id, language=['es']) -> str | None:
        """
        Descarga la transcripción y la devuelve como una cadena de texto.
        Args:
            video_id (str): El ID del video de YouTube.
            language (list): Lista de códigos de idioma a buscar (por defecto: ['es'])
        Returns:
            str: El texto de la transcripción o None si ocurre un error.
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_generated_transcript(language)

            formatter = TextFormatter()
            transcript_text = formatter.format_transcript(transcript.fetch())

            # Elimina códigos de tiempo y nombres de oradores
            transcript_text = re.sub(r'\[\d+:\d+:\d+\]', '', transcript_text)
            transcript_text = re.sub(r'<\w+>', '', transcript_text)
            return transcript_text
        except Exception as e:
            print(f"Error al intentar descargar la transcripción: {e}")
            return None

    @staticmethod
    def process_video(youtube_url) -> str:
        """
        Procesa una URL de video de YouTube y guarda la transcripción en un archivo.
        Args:
            youtube_url (str): La URL del video de YouTube.
        Returns:
            str: El mensaje de estado.
        """
        video_id = YoutubeProcessor.get_video_id(youtube_url)
        if not video_id:
            return "URL invalida"

        transcript_text = YoutubeProcessor.download_transcript(video_id)
        if not transcript_text:
            return "Error al descargar la transcripción"

        video_title = YoutubeProcessor.get_video_title(video_id)
        file_name = f"{video_id}_{video_title}.txt"
        file_name = re.sub(r'[\\/*?:"<>|]', '', file_name)

        # Crea el directorio si no existe
        save_dir = Path("../assets/docs/transcript/web/")
        os.makedirs(save_dir, exist_ok=True)

        # Guarda el archivo en el directorio especificado
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(transcript_text)

        return f"Transcripcion guardada en {file_path}\n\n Contenido de la transcripcion:\n{transcript_text}"


# ? Dev Purpose
if __name__ == "__main__":
    import gradio as gr  # type: ignore
    interface = gr.Interface(
        fn=YoutubeProcessor.process_video,
        inputs=gr.Textbox(label="Ingresa URL de YouTube"),
        outputs=gr.Textbox(label="Resultado"),
        title="Descargar Transcripciones de YouTube",
        description="Ingresa una URL de YouTube para descargar y guardar su transcripción."
    )

    interface.launch()
