# docs/pdf_processor.py
import os
from PyPDF2 import PdfReader
from utils.env_loader import OPENAI_API_KEY


class PDFProcessor:
    def __init__(self):
        self.output_path = "../assets/docs/transcript/pdf/"
        os.makedirs(self.output_path, exist_ok=True)

    def extract_text(self, pdf_file):
        """Extrae texto de un archivo PDF y lo guarda en un archivo de texto.
            Args:
                pdf_file (str): El archivo PDF a procesar.

            Returns:
                str: El mensaje de estado.
        """
        reader = PdfReader(pdf_file)
        transcript_text = ""

        for page in reader.pages:
            transcript_text += page.extract_text() + "\n"

        # Get original filename without extension and add _transcripcion
        base_name = os.path.splitext(os.path.basename(pdf_file))[0]
        output_filename = f"{base_name}_transcripcion.txt"
        output_file = os.path.join(self.output_path, output_filename)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        return f"Transcripción guardada en: {output_file} \n\nContenido de la transcripción:\n{transcript_text}"

    def process_pdf(self, pdf_file) -> str:
        """Procesa un archivo PDF y guarda la transcripción en un archivo de texto.
            Args:
                pdf_file (str): El archivo PDF a procesar.
            Returns:
                str: El mensaje de estado.
        """
        output_file = self.extract_text(pdf_file.name)
        return output_file


# ? Dev Purpose
if __name__ == "__main__":
    import gradio as gr  # type: ignore
    print("Launching PDF Processor Interface...")
    print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
    iface = gr.Interface(
        fn=PDFProcessor.process_pdf,
        inputs=gr.File(label="Sube tu archivo PDF"),
        outputs=gr.Textbox(label="Resultado"),
        title="Extractor de Texto de PDF",
        description="Sube un archivo PDF para extraer su texto y guardarlo en un archivo de texto."
    )
    iface.launch()
