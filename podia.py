import json
import gradio as gr  # type: ignore
from audio.video_processor import VideoProcessor
from core.summary import SummaryGenerator
from core.script import ScriptGenerator
from core.voice import VoiceGenerator
from docs.pdf_processor import PDFProcessor
from utils.gen_podcast_name import Extra
from utils.url_processor import URLProcessor
from utils.env_loader import load_environment_variables, OPENAI_API_KEY
from ui.podia_ui import PodIAUI


class PodIA:
    def __init__(self):
        self.summary_generator = SummaryGenerator(OPENAI_API_KEY)
        self.podcast_number = Extra.enumarate_podcast_name()
        self.pdf_processor = PDFProcessor()
        self.video_processor = VideoProcessor(OPENAI_API_KEY)
        self.url_processor = URLProcessor(OPENAI_API_KEY)
        self.script_generator = ScriptGenerator(OPENAI_API_KEY)
        self.voice_generator = VoiceGenerator(
            OPENAI_API_KEY, podcast_number=self.podcast_number)
        self.ui = PodIAUI(self)

    def update_models_config(self, transcript_model, summary_model, script_model, voice_model):
        """Update the AI models configuration"""
        try:
            self.video_processor.update_model(transcript_model)
            self.summary_generator.update_model(summary_model)
            self.script_generator.update_model(script_model)
            self.voice_generator.update_model(voice_model)
            # Update voice model in relevant components

            return "✅ Configuración actualizada exitosamente"
        except Exception as e:
            return f"❌ Error actualizando la configuración: {str(e)}"

    def update_voice_config(self, host_name, host_gender, host_voice,
                            guest_name, guest_gender, guest_voice):
        """Update voice configuration for characters"""
        try:
            self.script_generator.anfitrion.name = host_name
            self.script_generator.anfitrion.set_gender(host_gender)
            self.script_generator.anfitrion.set_voice(host_voice)

            self.script_generator.participante.name = guest_name
            self.script_generator.participante.set_gender(guest_gender)
            self.script_generator.participante.set_voice(guest_voice)

            return "✅ Configuración de voces actualizada exitosamente"
        except Exception as e:
            return f"❌ Error actualizando la configuración de voces: {str(e)}"

    def process_input(self, input_type, content, progress=gr.Progress()):
        progress(0.2, "Procesando entrada...")

        if input_type == "PDF":
            return self.pdf_processor.process_pdf(content)
        elif input_type == "URL":
            return self.url_processor.process_youtube_url(content, progress)
        elif input_type == "Video/Audio":
            return self.video_processor.process_media(content)

        return "Por favor, seleccione un tipo de entrada válido y proporcione el contenido."

    def process_content(self, input_type, content):
        """Procesa el contenido secuencialmente"""
        try:
            # Extraer texto
            extracted_text = self.process_input(input_type, content)
            if not extracted_text:
                return "Error al extraer texto", "", {}

            # Generar resumen
            summary = self.summary_generator.generate_summary(extracted_text)
            if not summary:
                return extracted_text, "Error al generar resumen", {}

            # Crear guión (ahora ya viene como JSON válido)
            script = self.script_generator.generate_script(summary)

            return extracted_text, summary, script
        except Exception as e:
            return f"Error en el procesamiento: {str(e)}", "", {}

    def extract_text(self, input_type, pdf_content, url_content, media_content):
        content = self._get_active_content(
            input_type, pdf_content, url_content, media_content)
        return self.process_input(input_type, content)

    def generate_summary(self, text):
        if not text.strip():
            return "Por favor, primero extraiga el texto del contenido."
        return self.summary_generator.generate_summary(text)

    def generate_script(self, summary):
        if not summary.strip():
            return {}
        return self.script_generator.generate_script(summary)

    def generate_podcast(self, script_json: dict) -> str | None:
        """Generate audio podcast from script"""
        try:
            # Convert dict to JSON string if needed
            script_str = json.dumps(script_json) if isinstance(
                script_json, dict) else script_json
            # Generate the podcast audio file
            audio_path = self.voice_generator.generate_podcast(script_str)
            return audio_path
        except Exception as e:
            print(f"Error generating podcast: {e}")
            return None

    def _get_active_content(self, input_type, pdf_content, url_content, media_content):
        content_map = {
            "PDF": pdf_content,
            "URL": url_content,
            "Video/Audio": media_content
        }
        return content_map.get(input_type)

    def launch(self):
        ui = PodIAUI(self)
        app = ui.create_ui()
        app.launch(share=False, server_port=4022, show_api=False)


if __name__ == "__main__":
    try:
        load_environment_variables()
    except Exception as e:
        print(f"Error cargando las variables de entorno: {str(e)}")
    podia = PodIA()
    podia.launch()
