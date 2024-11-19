from openai import OpenAI
from utils.env_loader import OPENAI_API_KEY, load_environment_variables


class SummaryGenerator:
    """
    Clase para generar resúmenes estructurados utilizando OpenAI GPT.

    Attributes:
        client (OpenAI): Cliente de OpenAI para realizar las peticiones a la API.
    """

    def __init__(self, api_key: str) -> None:
        """
        Inicializa el generador de resúmenes.

        Args:
            api_key (str): Clave de API de OpenAI.
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        self.client = OpenAI(api_key=api_key)

    def generate_summary(self, text: str) -> str:
        """
        Genera un resumen estructurado del texto proporcionado.

        Args:
            text (str): Texto a analizar y resumir.

        Returns:
            str: Resumen estructurado que incluye tema principal, puntos clave y resumen para debate.
        """
        prompt = f"""
        You’re a skilled podcast producer with a knack for transforming complex texts into engaging and entertaining summaries. You understand what captivates an audience and how to structure information for maximum impact. Your specialty is crafting summaries that not only inform but also spark lively discussions among listeners.

        Your task is to generate a summary of a text for an interesting and entertaining podcast. Please follow this structure:
        1. Main topic, theme, or subject of the text,
        2. Main ideas or the finality of the text, (maximum 3)
        3. Key points or arguments (maximum 10)
        4. Notable quotes or references (maximum 3),
        5. Additional context or background information (if necessary),
        6. Summary for discussion.

        Ensure the summary is engaging, concise, and tailored for a podcast audience. The goal is to inform and entertain listeners while encouraging them to share their thoughts and opinions.

        Ur response must be in Spanish language and should be at least 200 words long.

        Text to summarize:
        {text}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en análisis y resumen de textos enfocado en generar resúmenes interesantes y estructurados para debates."},
                {"role": "user", "content": prompt}
            ]
        )
        return str(response.choices[0].message.content)


# Para propósitos de desarrollo
if __name__ == "__main__":
    import gradio as gr  # type: ignore
    from utils.env_loader import OPENAI_API_KEY, load_environment_variables

    load_environment_variables()
    print("Clave API:", OPENAI_API_KEY)

    def create_gradio_interface() -> gr.Interface:
        """
        Crea y configura la interfaz de Gradio para el generador de resúmenes.

        Returns:
            gr.Interface: Interfaz web de Gradio configurada.
        """
        generator = SummaryGenerator(str(OPENAI_API_KEY))

        def process_text(input_text: str) -> str:
            """
            Procesa el texto de entrada y genera un resumen.

            Args:
                input_text (str): Texto a resumir.

            Returns:
                str: Resumen generado.
            """
            return generator.generate_summary(input_text)

        iface = gr.Interface(
            fn=process_text,
            inputs=gr.Textbox(lines=10, label="Ingresa el texto a resumir"),
            outputs=gr.Textbox(lines=10, label="Resumen generado"),
            title="Generador de Resúmenes para Debate",
            description="Ingresa un texto y obtén un resumen estructurado con el tema principal y puntos clave."
        )
        return iface

    app = create_gradio_interface()
    app.launch()
