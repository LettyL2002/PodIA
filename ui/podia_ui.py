import gradio as gr  # type: ignore
from typing import TYPE_CHECKING, cast, Literal
from ui.theme import PodIATheme
from utils.constants import (
    AVAILABLE_TRANSCRIPT_MODELS,
    AVAILABLE_SUMMARY_MODELS,
    AVAILABLE_SCRIPT_MODELS,
    AVAILABLE_VOICE_MODELS,
    TRANSCRIPT_MODEL,
    SUMMARY_MODEL,
    SCRIPT_MODEL,
    VOICE_MODEL,
    MALE_VOICES,
    FEMALE_VOICES,
    URL_INPUT,
    PDF_INPUT,
    VIDEO_INPUT
)

if TYPE_CHECKING:
    from podia import PodIA


class PodIAUI:
    def __init__(self, podia_instance: 'PodIA'):
        self.podia: 'PodIA' = podia_instance
        self.theme = PodIATheme().create_theme()

    def create_ui(self):
        # Estados de las dependencias
        # future text_extracted = gr.State(False)
        # future summary_generated = gr.State(False)
        # future script_generated = gr.State(False)

        with gr.Blocks(theme=self.theme, title="🎙️ PodIA - Generador de Podcasts Inteligente", css=PodIATheme.css) as app:
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
                        3. **Siga** el orden de los botones para procesar su contenido
                    """)

                    input_type = gr.Radio(
                        choices=[PDF_INPUT, URL_INPUT, VIDEO_INPUT],
                        label="Tipo de Contenido",
                        value=URL_INPUT,
                        info="Seleccione el formato de su contenido de entrada"
                    )

                    pdf_input = gr.File(
                        label="📄 Subir PDF",
                        file_types=[".pdf"],
                        visible=False,
                        elem_classes=["file-upload"],
                        scale=1,
                        min_width=100
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
                        elem_classes=["file-upload"],
                        scale=1,
                        min_width=100
                    )

                    gr.Markdown("""
                        ### 🔄 Proceso paso a paso:
                        
                        1. **📄 Extraer Texto**: Este botón procesa su entrada y extrae el texto. Es el primer paso necesario.
                        2. **📝 Generar Resumen**: Una vez extraído el texto, este botón creará un resumen conciso del contenido.
                        3. **🎭 Generar Guión**: Usando el resumen, este botón creará un guión conversacional para el podcast.
                        4. **🎙️ Generar Podcast**: Finalmente, este botón convertirá el guión en un podcast de audio.
                    """)

                    extract_text_btn = gr.Button(
                        "📄 Extraer Texto", variant="primary")
                    generate_summary_btn = gr.Button(
                        "📝 Generar Resumen", variant="primary")
                    generate_script_btn = gr.Button(
                        "🎭 Generar Guión", variant="primary")
                    generate_podcast_btn = gr.Button(
                        "🎙️ Generar Podcast de Audio", variant="primary")

                    process_status = gr.Textbox(
                        label="Estado del Proceso",
                        interactive=False,
                        value="Esperando entrada de contenido...",
                        elem_classes=["status-box"]
                    )

                with gr.TabItem("🗣️ Voces"):
                    gr.Markdown(""" 
                        ### 🗣️ Configuración de Voces
                        Personaliza los personajes que participarán en el podcast
                    """)

                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### 👤 Anfitrión")
                            host_name = gr.Textbox(
                                label="Nombre",
                                value="Alfonso",
                                info="Nombre del anfitrión"
                            )
                            host_gender = gr.Radio(
                                choices=[("male", "Masculino"),
                                         ("female", "Femenino")],
                                label="Género",
                                value="male",
                                info="Género del anfitrión"
                            )
                            host_voice = gr.Dropdown(
                                choices=MALE_VOICES,
                                label="Voz",
                                value=MALE_VOICES[0],
                                info="Voz del anfitrión"
                            )

                        with gr.Column():
                            gr.Markdown("### 👤 Participante")
                            guest_name = gr.Textbox(
                                label="Nombre",
                                value="Patricia",
                                info="Nombre del participante"
                            )
                            guest_gender = gr.Radio(
                                choices=[("male", "Masculino"),
                                         ("female", "Femenino")],
                                label="Género",
                                value="female",
                                info="Género del participante"
                            )
                            guest_voice = gr.Dropdown(
                                choices=FEMALE_VOICES,
                                label="Voz",
                                value=FEMALE_VOICES[0],
                                info="Voz del participante"
                            )

                    update_voices_btn = gr.Button(
                        "💾 Actualizar Configuración de Voces",
                        variant="primary"
                    )
                    voices_status = gr.Textbox(
                        label="Estado",
                        interactive=False
                    )

                with gr.TabItem("📊 Resultados"):
                    gr.Markdown(""" 
                        ### 📊 Resultados del Procesamiento
                        Sigue los pasos en orden para procesar el contenido.
                    """)

                    with gr.Accordion("📄 Contenido Extraído", open=False):
                        content_output = gr.Textbox(
                            label="Texto extraído del contenido original",
                            lines=5,
                            interactive=False
                        )

                    with gr.Accordion("📝 Resumen", open=False):
                        summary_output = gr.Textbox(
                            label="Resumen procesado por IA",
                            lines=5,
                            interactive=False
                        )

                    with gr.Accordion("🎭 Guión del Podcast", open=False):
                        script_output = gr.JSON(
                            label="Guión generado para el podcast",
                            visible=True,
                            elem_classes=["json-output"],
                            show_label=True
                        )

                    with gr.Accordion("🎧 Podcast Generado", open=False):
                        with gr.Row():
                            podcast_output = gr.Audio(
                                label="Podcast Final",
                                type="filepath",
                                elem_classes=["clean-audio"],
                                show_label=True,
                                interactive=False,
                                autoplay=False,
                                visible=True,
                                show_download_button=True,
                                waveform_options={
                                    "waveform_color": "pink", "show_controls": True},
                            )

                with gr.TabItem("⚙️ Configuración"):
                    gr.Markdown(""" 
                        ### ⚙️ Configuración de Modelos
                        Seleccione los modelos de IA para cada función
                    """)

                    with gr.Group():
                        transcript_model = gr.Dropdown(
                            choices=AVAILABLE_TRANSCRIPT_MODELS,
                            value=TRANSCRIPT_MODEL,
                            label="Modelo de Transcripción",
                            info="Modelo usado para transcribir audio/video"
                        )

                        summary_model = gr.Dropdown(
                            choices=AVAILABLE_SUMMARY_MODELS,
                            value=SUMMARY_MODEL,
                            label="Modelo de Resumen",
                            info="Modelo usado para generar resúmenes"
                        )

                        script_model = gr.Dropdown(
                            choices=AVAILABLE_SCRIPT_MODELS,
                            value=SCRIPT_MODEL,
                            label="Modelo de Guión",
                            info="Modelo usado para generar el guión del podcast"
                        )

                        voice_model = gr.Dropdown(
                            choices=AVAILABLE_VOICE_MODELS,
                            value=VOICE_MODEL,
                            label="Modelo de Voz",
                            info="Modelo usado para la generación de voz"
                        )

                        save_config_btn = gr.Button(
                            "💾 Guardar Configuración",
                            variant="primary"
                        )

                        config_status = gr.Textbox(
                            label="Estado de la configuración",
                            interactive=False,
                            visible=True
                        )

            gr.Markdown(""" 
                ---
                ### ℹ️ Información Adicional
                - ⏳ El procesamiento puede tomar varios minutos dependiendo del tamaño del contenido
                - 📂 Los archivos muy grandes pueden requerir más tiempo de procesamiento
                - ✅ Para obtener mejores resultados, asegúrese de que el contenido sea claro y esté bien estructurado
            """)

            def update_visibility(choice: str) -> tuple[dict[str, bool], dict[str, bool], dict[str, bool]]:
                return (
                    gr.update(visible=choice == PDF_INPUT),
                    gr.update(visible=choice == URL_INPUT),
                    gr.update(visible=choice == VIDEO_INPUT)
                )

            def extract_text(input_type_val: str, *args) -> tuple[str, str]:
                try:
                    input_type_clean = input_type_val.replace(PDF_INPUT, "PDF").replace(
                        URL_INPUT, "URL").replace(VIDEO_INPUT, "Video/Audio")
                    result = self.podia.extract_text(
                        input_type_clean, args[0], args[1], args[2])
                    status = "✅ Texto extraído correctamente. Puede continuar con 'Generar Resumen' en la pestaña de Resultados."
                    return result, status
                except Exception as e:
                    return "", f"❌ Error al extraer texto: {str(e)}"

            def generate_summary(content: str) -> tuple[str, str]:
                try:
                    result = self.podia.generate_summary(content)
                    status = "✅ Resumen generado correctamente. Puede continuar con 'Generar Guión' en la pestaña de Resultados."
                    return result, status
                except Exception as e:
                    return "", f"❌ Error al generar resumen: {str(e)}"

            def generate_script(summary: str) -> tuple[dict, str]:
                try:
                    result = self.podia.generate_script(summary)
                    status = "✅ Guión generado correctamente. Puede continuar con 'Generar Podcast' en la pestaña de Resultados."
                    return result, status
                except Exception as e:
                    return {}, f"❌ Error al generar guión: {str(e)}"

            def generate_podcast(script: dict) -> tuple[str | None, str, gr.update]:
                try:
                    if not script:
                        return None, "❌ Error: No hay guión disponible para generar el podcast", gr.update(visible=False)

                    audio_path = self.podia.generate_podcast(script)
                    if audio_path:
                        return audio_path, "✅ Podcast generado correctamente. Puede reproducirlo con el botón.", gr.update(visible=True)
                    return None, "❌ Error: No se pudo generar el audio del podcast", gr.update(visible=False)
                except Exception as e:
                    return None, f"❌ Error al generar podcast: {str(e)}", gr.update(visible=False)

            def update_voice_choices(gender: str) -> gr.update:
                """Update voice choices based on selected gender"""
                voices = cast(list[str], MALE_VOICES if gender ==
                              "male" else FEMALE_VOICES)
                return gr.update(choices=voices, value=voices[0])

            # Evento para cambiar visibilidad
            input_type.change(
                fn=update_visibility,
                inputs=[input_type],
                outputs=[pdf_input, url_input, media_input]
            )

            extract_text_btn.click(
                fn=extract_text,
                inputs=[input_type, pdf_input, url_input, media_input],
                outputs=[content_output, process_status]
            )

            generate_summary_btn.click(
                fn=generate_summary,
                inputs=[content_output],
                outputs=[summary_output, process_status]
            )

            generate_script_btn.click(
                fn=generate_script,
                inputs=[summary_output],
                outputs=[script_output, process_status]
            )

            generate_podcast_btn.click(
                fn=generate_podcast,
                inputs=[script_output],
                outputs=[podcast_output, process_status]
            )

            # Add event handler for configuration
            save_config_btn.click(
                fn=self.podia.update_models_config,
                inputs=[transcript_model, summary_model,
                        script_model, voice_model],
                outputs=config_status
            )

            host_gender.change(
                fn=update_voice_choices,
                inputs=[host_gender],
                outputs=[host_voice]
            )

            guest_gender.change(
                fn=update_voice_choices,
                inputs=[guest_gender],
                outputs=[guest_voice]
            )

            update_voices_btn.click(
                fn=self.podia.update_voice_config,
                inputs=[host_name, host_gender, host_voice,
                        guest_name, guest_gender, guest_voice],
                outputs=[voices_status]
            )

        return app
