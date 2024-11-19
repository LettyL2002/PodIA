# docs/pdf_processor.py
import os
from pypdf import PdfReader # type: ignore


class PDFProcessor:
    """
    Clase para procesar archivos PDF y extraer su contenido textual.

    Attributes:
        output_path (str): Ruta donde se guardarán los archivos de transcripción.
    """

    def __init__(self):
        """Inicializa el procesador PDF y crea el directorio de salida si no existe."""
        self.output_path = "../assets/docs/transcript/pdf/"
        os.makedirs(self.output_path, exist_ok=True)

    def extract_text(self, pdf_file: str) -> str:
        """
        Extrae texto de un archivo PDF y lo guarda en un archivo de texto.

        Args:
            pdf_file (str): Ruta del archivo PDF a procesar.

        Returns:
            str: Mensaje con la ruta del archivo guardado y el contenido extraído.

        Raises:
            FileNotFoundError: Si el archivo PDF no existe.
            PermissionError: Si no hay permisos para escribir el archivo de salida.
        """
        reader = PdfReader(pdf_file)
        transcript_text = ""

        for page in reader.pages:
            transcript_text += page.extract_text() + "\n"

        # Obtener nombre del archivo original sin extensión y añadir _transcripcion
        base_name = os.path.splitext(os.path.basename(pdf_file))[0]
        output_filename = f"{base_name}_transcripcion.txt"
        output_file = os.path.join(self.output_path, output_filename)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        return f"Transcripción guardada en: {output_file} \n\nContenido de la transcripción:\n{transcript_text}"

    def process_pdf(self, pdf_file) -> str:
        """
        Procesa un archivo PDF y guarda la transcripción en un archivo de texto.

        Args:
            pdf_file: Objeto archivo PDF desde la interfaz Gradio.

        Returns:
            str: Mensaje con el resultado del procesamiento.
        """
        output_file = self.extract_text(pdf_file.name)
        return output_file


#? Dev Purpose
if __name__ == "__main__":
    import gradio as gr  # type: ignore
    from utils.env_loader import OPENAI_API_KEY
    print("Iniciando la Interfaz del Procesador PDF...")
    print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
    processor = PDFProcessor()
    iface = gr.Interface(
        fn=processor.process_pdf,
        inputs=gr.File(label="Sube tu archivo PDF"),
        outputs=gr.Textbox(label="Resultado"),
        title="Extractor de Texto de PDF",
        description="Sube un archivo PDF para extraer su texto y guardarlo en un archivo de texto."
    )
    iface.launch()
