from openai import OpenAI
from typing import List, Tuple
from core.characters.anfitrion import Anfitrion
from core.characters.participante1 import Participante1


class ScriptGenerator:
    def __init__(self, api_key: str) -> None:
        """Inicializa OpenAI y los personajes del podcast."""
        # Crear instancias separadas de OpenAI para cada personaje
        self.anfitrion_ai = OpenAI(api_key=api_key)
        self.participante_ai = OpenAI(api_key=api_key)

        self.anfitrion = Anfitrion()
        self.participante = Participante1()
        self.conversation: List[Tuple[str, str]] = []
        self.anfitrion_messages: List[str] = []
        self.participante_messages: List[str] = []

    def _initial_anfitrion_response(self, summary: str) -> str:
        try:
            # * Anfitrion

            # Personalizamos el prompt inicial del anfitrión en base al resumen del tema a discutir
            host_init_prompt = self.anfitrion.anfitrion_init(summary)

            # Generar respuesta inicial del anfitrión en base al prompt personalizado
            host_response = self._generate_anfitrion_response(host_init_prompt)

            # Agregar la respuesta inicial del anfitrión a la conversación
            self.conversation.append(("Anfitrion", host_response))

            # Agregar la respuesta inicial del anfitrión a la lista de mensajes del anfitrión
            self.anfitrion_messages.append(host_response)

            # Imprimir la respuesta inicial del anfitrión
            print(f"Anfitrion inicial: {host_response}")

            return host_response

        except Exception as e:
            print(f"Error: {e}")
            return "Error: No se pudo generar el guion del podcast."

    def _generate_anfitrion_response(self, prompt: str) -> str:
        """Genera una respuesta usando la instancia de OpenAI del anfitrión."""
        response = self.anfitrion_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.anfitrion.anfitrion_prompt()},
                {"role": "user", "content": prompt}]
        )
        return str(response.choices[0].message.content)

    def _initial_participante_response(self, summary: str, previous_response: str) -> str:

        try:
            # * Participante

            # Personalizamos el prompt inicial del participante en base al resumen del tema a discutir y la respuesta del anfitrión
            guest_init_prompt = self.participante.participante1_init(
                summary, previous_response)

            # Generar respuesta inicial del participante en base al prompt personalizado
            guest_response = self._generate_participante_response(
                guest_init_prompt)

            # Agregar la respuesta inicial del participante a la conversación
            self.conversation.append(("Participante", guest_response))

            # Agregar la respuesta inicial del participante a la lista de mensajes del participante
            self.participante_messages.append(guest_response)

            print(f"Participante inicial: {guest_response}")
            return guest_response

        except Exception as e:
            print(f"Error: {e}")
            return "Error: No se pudo generar el guion del podcast."

    def _generate_participante_response(self, prompt: str) -> str:
        """Genera una respuesta usando la instancia de OpenAI del participante."""
        response = self.participante_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.participante.participante1_prompt()},
                {"role": "user", "content": prompt}]
        )
        return str(response.choices[0].message.content)

    def generate_script(self, summary: str, num_exchanges: int = 2) -> str:
        """Genera un guion de podcast completo."""

        # Generar respuesta inicial del anfitrión
        host_response = self._initial_anfitrion_response(summary)

        # Generar respuesta inicial del participante
        guest_response = self._initial_participante_response(
            summary, host_response)

        # Generar el resto del diálogo
        for i in range(num_exchanges):
            print(f"Intercambio {i + 1} de {num_exchanges}")

            # Respuesta del anfitrión
            host_prompt = f"{self.anfitrion.anfitrion_prompt(
            )}\n\nÚltima respuesta del participante: {guest_response}"
            host_response = self._generate_anfitrion_response(host_prompt)
            self.conversation.append(("Anfitrion", host_response))
            self.anfitrion_messages.append(host_response)
            print(f"Anfitrion: {host_response}")

            # Si no es el último intercambio, generar respuesta del participante
            if i < num_exchanges - 1:
                guest_prompt = f"{self.participante.participante1_prompt(
                )}\n\nÚltima respuesta del anfitrión: {host_response}\n"
                guest_response = self._generate_participante_response(
                    guest_prompt)
                self.conversation.append(("Participante", guest_response))
                self.participante_messages.append(guest_response)
                print(f"Participante: {guest_response}")

        # Agregar la despedida del anfitrión
        despedida_prompt = f"{self.anfitrion.anfitrion_prompt()}\n\n{
            self.anfitrion.anfitrion_despedida()}"
        despedida_response = self._generate_anfitrion_response(
            despedida_prompt)
        self.conversation.append(("Anfitrion", despedida_response))
        self.anfitrion_messages.append(despedida_response)
        print(f"Anfitrion despedida: {despedida_response}")

        return self._format_script()

    def get_anfitrion_messages(self) -> List[str]:
        """Devuelve una lista de mensajes del anfitrión."""
        return self.anfitrion_messages

    def get_participante_messages(self) -> List[str]:
        """Devuelve una lista de mensajes del participante."""
        return self.participante_messages

    def get_conversation(self) -> List[Tuple[str, str]]:
        """Devuelve la conversación completa."""
        return self.conversation

    def _format_script(self) -> str:
        """Formatea la conversación en un guion legible."""
        script = "GUION DEL PODCAST\n\n"
        for speaker, text in self.conversation:
            script += f"{speaker}: {text}\n\n"
        return script


# ? Dev Purpose
if __name__ == "__main__":
    import gradio as gr  # type: ignore
    from utils.env_loader import load_environment_variables, OPENAI_API_KEY
    load_environment_variables()
    key = OPENAI_API_KEY
    print(f"API KEY : {key}")

    def generate_podcast_script(summary: str, num_exchanges: int = 3) -> str:
        script_gen = ScriptGenerator(api_key=str(key))
        script = script_gen.generate_script(
            summary=summary, num_exchanges=int(num_exchanges))
        return script

    # Gradio Interface to input summary and generate the script
    def ui():
        gr.Interface(
            fn=generate_podcast_script,
            inputs=[
                gr.Textbox(lines=10, label="Summary"),
                gr.Slider(minimum=1, maximum=10, value=3,
                          label="Number of Exchanges")
            ],
            outputs="text",
            title="Podcast Script Generator",
            description="Generates a podcast script based on a summary.",
            live=True
        ).launch()

    ui()
