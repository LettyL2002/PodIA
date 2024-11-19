import os
import re
import moviepy.editor as mp  # type: ignore
from openai import OpenAI
from pathlib import Path


class VideoProcessor:
    def __init__(self, openai_api_key):
        """
        Inicializa el procesador de video con la API key de OpenAI

        Args:
            openai_api_key (str): API key de OpenAI
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.transcript_path = Path("../assets/docs/transcript/video")

        # Crear el directorio si no existe
        self.transcript_path.mkdir(parents=True, exist_ok=True)

    def extract_audio(self, video_path, output_path=None):
        """
        Extrae el audio de un video

        Args:
            video_path (str): Ruta al archivo de video
            output_path (str, optional): Ruta donde guardar el audio

        Returns:
            str: Ruta del archivo de audio generado
        """
        # Use regex to remove invalid characters
        safe_name = re.sub(r'[^\w\s-]', '', Path(video_path).stem)
        if output_path is None:
            output_path = str(Path(video_path).parent / f"{safe_name}.mp3")

        print(f"Extrayendo audio de {video_path} a {output_path}")
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(output_path)
        video.close()

        return output_path

    def transcribe_audio(self, audio_path):
        """
        Transcribe un archivo de audio usando la API de OpenAI

        Args:
            audio_path (str): Ruta al archivo de audio

        Returns:
            str: Texto transcrito
        """
        print(f"Transcribiendo audio de {audio_path}")
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text

    def process_video(self, video_path):
        """
        Procesa un archivo de video: extrae audio, transcribe y guarda

        Args:
            video_path (str): Ruta al archivo de video

        Returns:
            tuple: (ruta del archivo de transcripción, texto transcrito)
        """
        # Extraer audio del video
        audio_path = self.extract_audio(video_path)

        try:
            # Transcribir el audio
            transcript = self.transcribe_audio(audio_path)
            # Guardar transcripción
            transcript_path = self.save_transcript(transcript, video_path)
        finally:
            # Limpiar el archivo de audio temporal
            os.remove(audio_path)

        return transcript_path, transcript

    def process_audio(self, audio_path):
        """
        Procesa un archivo de audio: transcribe y guarda

        Args:
            audio_path (str): Ruta al archivo de audio

        Returns:
            tuple: (ruta del archivo de transcripción, texto transcrito)
        """
        # Transcribir
        transcript = self.transcribe_audio(audio_path)
        # Guardar transcripción
        transcript_path = self.save_transcript(transcript, audio_path)

        return transcript_path, transcript

    def process_media(self, file_path):
        """
        Valida el tipo de archivo y lo envía al procesador correspondiente

        Args:
            file_path (str): Ruta al archivo de video o audio

        Returns:
            tuple: (ruta del archivo de transcripción, texto transcrito)
        """
        # Determinar si es un archivo de audio o video
        file_ext = Path(file_path).suffix.lower()
        audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.ogg'}

        if file_ext in audio_extensions:
            return self.process_audio(file_path)
        else:
            return self.process_video(file_path)

    def save_transcript(self, transcript, video_name):
        """
        Guarda la transcripción en un archivo

        Args:
            transcript (str): Texto transcrito
            video_name (str): Nombre del video original para nombrar el archivo

        Returns:
            str: Ruta del archivo de transcripción guardado
        """
        print(f"Guardando transcripción de {video_name}")
        output_file = self.transcript_path / \
            f"{Path(video_name).stem}_transcript.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        return str(output_file)


# ? Dev Purpose
if __name__ == "__main__":
    import gradio as gr  # type: ignore
    from utils.env_loader import load_environment_variables, OPENAI_API_KEY
    print("Launching Video Processor Interface...")
    load_environment_variables()
    print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")

    def create_gradio_interface(processor):
        """
        Crea la interfaz de Gradio

        Args:
            processor (VideoProcessor): Instancia del procesador de video
        """
        def process_video_interface(video_path):
            transcript_path, transcript = processor.process_video(video_path)
            return f"Transcripción guardada en: {transcript_path}\n\nTranscripción:\n{transcript}"

        iface = gr.Interface(
            fn=process_video_interface,
            inputs=gr.Video(),
            outputs="text",
            title="Transcriptor de Video",
            description="Sube un video para extraer y transcribir su audio"
        )
        return iface

    API_KEY = OPENAI_API_KEY
    processor = VideoProcessor(API_KEY)

    # Crear y lanzar la interfaz de Gradio
    interface = create_gradio_interface(processor)
    interface.launch()
