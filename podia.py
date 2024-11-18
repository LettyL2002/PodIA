# main.py
import gradio as gr  # type: ignore
from docs.pdf_processor import PDFProcessor
from docs.youtube_processor import YoutubeProcessor
from utils.env_loader import load_environment_variables, OPENAI_API_KEY


def create_enhanced_podcast_ui():
    # Load environment variables
    env_vars = load_environment_variables()

    # Initialize processors
    youtube_processor = YoutubeProcessor()
    pdf_processor = PDFProcessor()
    video_processor = VideoProcessor()
    audio_processor = AudioProcessor()
    podcast_generator = PodcastGenerator(env_vars["OPENAI_API_KEY"])

    theme = gr.themes.Soft(
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

    with gr.Blocks(theme=theme, title="Generador de Podcasts con IA") as app:
        with gr.Row():
            gr.Markdown("""
                # 🎙️ Generador de Podcasts con IA
                Convierte cualquier contenido en una conversación dinámica entre dos personajes
            """)

        with gr.Tabs():
            with gr.TabItem("📝 Entrada de Contenido"):
                with gr.Row():
                    with gr.Column(scale=2):
                        input_type = gr.Radio(
                            choices=["PDF", "URL", "Video"],
                            label="Tipo de Contenido",
                            value="URL"
                        )

                        with gr.Group():
                            file_input = gr.File(
                                label="Subir PDF/Video",
                                visible=False,
                                file_types=[".pdf", ".mp4",
                                            ".avi", ".mov", ".mkv"]
                            )
                            text_input = gr.Textbox(
                                label="URL",
                                placeholder="Ingrese la URL del contenido o video de YouTube",
                                lines=2
                            )

                    with gr.Column(scale=1):
                        with gr.Group():
                            gr.Markdown("### Configuración de Voces")
                            voice1 = gr.Textbox(
                                label="Nombre del Personaje 1",
                                value="Ana"
                            )
                            voice2 = gr.Textbox(
                                label="Nombre del Personaje 2",
                                value="Carlos"
                            )

                generate_btn = gr.Button(
                    "🎙️ Generar Podcast", variant="primary")

            with gr.TabItem("📊 Resultados"):
                with gr.Row():
                    with gr.Column():
                        summary_output = gr.Textbox(
                            label="Resumen del Contenido",
                            lines=5,
                            interactive=False
                        )
                        script_output = gr.JSON(label="Guión del Podcast")
                        audio_output = gr.Audio(
                            label="Podcast Generado",
                            type="filepath",
                            interactive=False
                        )

        def process_content(input_type, content, file, voice1_name, voice2_name, progress=gr.Progress()):
            progress(0.1, desc="Procesando entrada...")
            text_content = transcript_processor.process_input(
                input_type, content, file)

            progress(0.3, desc="Generando resumen...")
            summary = podcast_generator.generate_summary(text_content)

            progress(0.5, desc="Generando guión...")
            script = podcast_generator.generate_script(
                summary, voice1_name, voice2_name)

            progress(0.7, desc="Generando voces...")
            audio_path = audio_processor.generate_podcast(script)

            progress(1.0, desc="¡Listo!")
            return summary, script, audio_path

        def update_input_visibility(input_type):
            return {
                text_input: input_type in ["URL", "Video"],
                file_input: input_type in ["PDF", "Video"]
            }

        input_type.change(
            fn=update_input_visibility,
            inputs=[input_type],
            outputs=[file_input, text_input]
        )

        generate_btn.click(
            fn=process_content,
            inputs=[input_type, text_input, file_input, voice1, voice2],
            outputs=[summary_output, script_output, audio_output]
        )

    return app


if __name__ == "__main__":
    load_environment_variables()
    app = create_enhanced_podcast_ui()
    app.launch()
