from openai import OpenAI
from utils.env_loader import OPENAI_API_KEY, load_environment_variables


class SummaryGenerator:
    """
    Clase para generar resúmenes estructurados utilizando OpenAI GPT.

    Attributes:
        client (OpenAI): Cliente de OpenAI para realizar las peticiones a la API.
    """

    def __init__(self, key: str) -> None:
        """
        Inicializa el generador de resúmenes.

        Args:
            key (str): Clave de API de OpenAI.
        """
        self.client = OpenAI(api_key=key)

    def generate_summary(self, text: str) -> str:
        """
        Genera un resumen estructurado del texto proporcionado.

        Args:
            text (str): Texto a analizar y resumir.

        Returns:
            str: Resumen estructurado que incluye tema principal, puntos clave y resumen para debate.
        """
        prompt = f"""
        Analiza el siguiente texto y genera un resumen estructurado que incluya:
        1. Tema principal
        2. Puntos clave (máximo 10)
        3. Resumen para debate

        Texto a analizar:
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
