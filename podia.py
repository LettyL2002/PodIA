# future : Under Development
import gradio as gr  # type: ignore
from audio.video_processor import VideoProcessor
from core.summary import SummaryGenerator
from core.script import ScriptGenerator
from docs.pdf_processor import PDFProcessor
from utils.url_processor import URLProcessor
from utils.env_loader import load_environment_variables, OPENAI_API_KEY


class PodIA:
    def __init__(self):
        self.summary_generator = SummaryGenerator(OPENAI_API_KEY)
        self.pdf_processor = PDFProcessor()
        self.video_processor = VideoProcessor(OPENAI_API_KEY)
        self.url_processor = URLProcessor(OPENAI_API_KEY)
        self.script_generator = ScriptGenerator(OPENAI_API_KEY)
        self.theme = self._create_theme()

    def _create_theme(self):
        return gr.themes.Soft(
            primary_hue="purple",
            secondary_hue="indigo",
            neutral_hue="slate",
            font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"]
        ).set(
            button_primary_background_fill="*primary_500",
            button_primary_background_fill_hover="*primary_600",
            button_primary_text_color="white",
            block_label_text_size="sm",
            block_title_text_size="lg",
        )

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
        """Procesa el contenido secuencialmente: primero extrae el texto,
        luego genera el resumen, y finalmente crea el guión

        Args:
            input_type (str): Tipo de contenido proporcionado por el usuario
            content (str): Contenido proporcionado por el usuario
        """
        # Paso 1: Extraer texto del contenido
        progress = gr.Progress()
        progress(0.1, "Extrayendo texto...")
        extracted_text = self.process_input(input_type, content, progress)
        if not extracted_text:
            return "Error al extraer texto", "", ""

        # Paso 2: Generar resumen del texto extraído
        progress(0.4, "Generando resumen...")
        summary = self.summary_generator.generate_summary(extracted_text)
        if not summary:
            return extracted_text, "Error al generar resumen", ""

        # Paso 3: Crear guión basado en el resumen
        progress(0.7, "Creando guión...")
        script = self.script_generator.generate_script(summary)
        progress(1.0, "¡Proceso completado!")

        return extracted_text, summary, script

    def create_ui(self):
        with gr.Blocks(theme=self.theme, title="🎙️ PodIA - Generador de Podcasts Inteligente", css="""
        /* Enhance styles for better UI */
        #pdf_input .wrap, #media_input .wrap {
            max-width: 400px;
            margin: auto;
        }
        .gradio-container {
            font-family: 'Inter', sans-serif;
        }
        """) as app:
            gr.Markdown("""
                # 🎙️ PodIA - Generador de Podcasts Inteligente
                ### Transforma cualquier contenido en un podcast interactivo
                
                > **Nota**: Esta herramienta procesa contenido de diferentes fuentes y lo convierte en un formato de podcast dinámico.
            """)

            with gr.Tabs():
                with gr.TabItem("📝 Entrada de Contenido"):
                    gr.Markdown("""
                        ### 📝 Instrucciones:
                        1. **Seleccione** el tipo de contenido que desea procesar 📄🌐🎥
                        2. **Proporcione** el contenido según el tipo seleccionado
                        3. **Configure** las voces para el podcast 🗣️
                    """)

                    input_type = gr.Radio(
                        choices=["📄 PDF", "🌐 URL", "🎥 Video/Audio"],
                        label="Tipo de Contenido",
                        value="🌐 URL",
                        info="Seleccione el formato de su contenido de entrada"
                    )

                    pdf_input = gr.File(
                        label="📄 Subir PDF",
                        file_types=[".pdf"],
                        visible=False,
                    )

                    url_input = gr.Textbox(
                        label="🌐 URL de YouTube",
                        placeholder="Ej: https://www.youtube.com/watch?v=...",
                        visible=True,
                        info="Pegue la URL del video de YouTube que desea procesar"
                    )

                    media_input = gr.File(
                        label="🎥 Subir Video/Audio",
                        file_types=["video/*", "audio/*"],
                        visible=False,
                    )

                    gr.Markdown("""
                        ### 🗣️ Configuración de Voces
                        Personalice los nombres de los personajes que participarán en el podcast
                    """)

                    with gr.Row():
                        with gr.Column(scale=1):
                            voice1 = gr.Textbox(
                                label="👤 Nombre del Personaje 1",
                                value="Ana",
                                info="Primer locutor del podcast"
                            )
                        with gr.Column(scale=1):
                            voice2 = gr.Textbox(
                                label="👤 Nombre del Personaje 2",
                                value="Carlos",
                                info="Segundo locutor del podcast"
                            )

                    process_btn = gr.Button(
                        "🎙️ Generar Podcast", variant="primary", scale=0.5)

                with gr.TabItem("📊 Resultados"):
                    gr.Markdown("""
                        ### 📊 Resultados del Procesamiento
                        Aquí podrá ver el contenido procesado, el resumen generado y el guión del podcast.
                    """)

                    with gr.Accordion("📄 Contenido Extraído", open=False):
                        content_output = gr.Textbox(
                            label="Texto extraído del contenido original",
                            lines=5,
                            interactive=False
                        )

                    with gr.Accordion("📝 Resumen", open=True):
                        summary_output = gr.Textbox(
                            label="Resumen procesado por IA",
                            lines=5,
                            interactive=False
                        )

                    with gr.Accordion("🎭 Guión del Podcast", open=True):
                        script_output = gr.JSON(
                            label="Guión generado para el podcast",
                            visible=True
                        )

            gr.Markdown("""
                ---
                ### ℹ️ Información Adicional
                - ⏳ El procesamiento puede tomar varios minutos dependiendo del tamaño del contenido
                - 📂 Los archivos muy grandes pueden requerir más tiempo de procesamiento
                - ✅ Para obtener mejores resultados, asegúrese de que el contenido sea claro y esté bien estructurado
            """)

            def update_visibility(choice):
                return (
                    gr.update(visible=choice == "📄 PDF"),
                    gr.update(visible=choice == "🌐 URL"),
                    gr.update(visible=choice == "🎥 Video/Audio")
                )

            def get_active_content(input_type, pdf_content, url_content, media_content):
                content_map = {
                    "PDF": pdf_content,
                    "URL": url_content,
                    "Video/Audio": media_content
                }
                return content_map.get(input_type)

            # Evento para cambiar visibilidad
            input_type.change(
                fn=update_visibility,
                inputs=[input_type],
                outputs=[pdf_input, url_input, media_input]
            )

            # Evento para procesar contenido
            process_btn.click(
                fn=lambda *args: self.process_content(
                    args[0],  # input_type
                    get_active_content(
                        args[0], args[1], args[2], args[3]),  # content
                ),
                inputs=[
                    input_type,
                    pdf_input,
                    url_input,
                    media_input,
                    voice1,
                    voice2
                ],
                outputs=[content_output, summary_output, script_output]
            )

        return app

    def launch(self):
        app = self.create_ui()
        app.launch()


if __name__ == "__main__":
    load_environment_variables()
    podia = PodIA()
    podia.launch()
