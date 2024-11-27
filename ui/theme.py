import gradio as gr  # type: ignore


class PodIATheme:

    css = """
    /* Estilos para ocultar imágenes y personalizar uploads */
    .file-upload [data-testid="image"], .file-upload img, .file-upload svg {
        display: none !important;
    }
    
    .file-upload {
        min-height: 0 !important;
        padding: 1rem !important;
    }
    
    .file-upload:before {
        content: none !important;
    }
    
    /* Estilos para el JSON output */
    .json-output [data-testid="image"], .json-output img, .json-output svg {
        display: none !important;
    }
    
    /* Eliminar padding y espacios innecesarios */
    .file-upload .wrap {
        min-height: 0 !important;
        padding: 0 !important;
    }
    
    /* Estilo minimalista para el botón de upload */
    .file-upload button {
        width: 100% !important;
        margin: 0 !important;
    }

    /* Estilos para el componente de audio */
    .clean-audio [data-testid="image"], .clean-audio img, .clean-audio svg {
        display: none !important;
    }

    .clean-audio audio {
        width: 100% !important;
        margin: 0 !important;
    }

    .clean-audio .wrap {
        min-height: 0 !important;
        padding: 0 !important;
    }
    """

    def create_theme(self):
        return gr.themes.Soft(
            primary_hue="pink",
            secondary_hue="indigo",
            neutral_hue="zinc",
            font=[gr.themes.GoogleFont("Quicksand"),
                  "system-ui", "sans-serif"],
        ).set(
            button_primary_background_fill="*primary_500",
            button_primary_background_fill_hover="*primary_600",
            button_primary_text_color="white",
            button_primary_border_color="transparent",
            block_label_text_size="sm",
            block_title_text_size="xl",
            block_shadow="0 4px 6px rgba(0,0,0,0.05)",
            block_title_text_weight="700",
            block_border_width="0px",
            block_radius="xl",
            input_background_fill="*neutral_50",
            input_border_width="1px",
            input_border_color="*neutral_200",
            input_shadow="0 2px 4px rgba(0,0,0,0.03)",
            input_radius="lg",
        )
