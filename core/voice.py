import json
from pathlib import Path
from typing import Dict, List, Literal, Union
from openai import OpenAI
from pydub import AudioSegment  # type: ignore
from core.characters.anfitrion import Anfitrion
from core.characters.participante1 import Participante1
from utils.constants import VOICE_MODEL, PAUSE_DURATION


class VoiceGenerator:
    def __init__(self, api_key: str, model: str = VOICE_MODEL, podcast_number: str = "1"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.pause_duration = PAUSE_DURATION
        self.tittle = podcast_number

        # Initialize character instances with type hints
        self.characters: Dict[str, Union[Anfitrion, Participante1]] = {
            "Anfitrion": Anfitrion(),
            "Participante": Participante1()
        }

    def update_model(self, new_model: str) -> None:
        """Updates the voice generation model being used"""
        self.model = new_model
        print(f"Updated voice model to: {new_model}")

    def _get_voice_for_character(self, character_name: str) -> Literal['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']:
        """Get the character's configured voice"""
        if character_name in self.characters:
            return self.characters[character_name].voice
        return 'alloy'  # default voice

    def generate_speech(self, text: str, voice_model: Literal['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'], filename: str) -> str:
        """Generate speech from text using OpenAI's TTS API"""
        try:
            response = self.client.audio.speech.create(
                model=self.model,
                voice=voice_model,
                input=text
            )

            output_path = self.output_dir / filename
            response.write_to_file(str(output_path))
            return str(output_path)

        except Exception as e:
            print(f"Error generating speech: {e}")
            return ""

    def process_script(self, script_json: str) -> List[Dict[str, str]]:
        """Process the script and generate audio files for each dialogue"""
        try:
            script_data = json.loads(script_json)
            audio_files = []

            for i, entry in enumerate(script_data["dialogue"]):
                character = entry["character"]
                message = entry["message"]

                # Select voice based on character
                voice = self._get_voice_for_character(character)

                # Generate audio file
                filename = f"{i+1}_{character}.mp3"
                audio_path = self.generate_speech(message, voice, filename)

                if audio_path:
                    audio_files.append({
                        "character": character,
                        "audio_path": audio_path,
                        "message": message
                    })

            return audio_files

        except Exception as e:
            print(f"Error processing script: {e}")
            return []

    def concatenate_audio_files(self, audio_files: List[Dict[str, str]]) -> str:
        """Concatenate all audio files with natural pauses between them"""
        try:
            # Create a blank audio segment
            final_audio = AudioSegment.silent(
                duration=500)  # Start with 0.5s silence

            # Add each audio file with a pause between them
            for audio_file in audio_files:
                # Load the audio file
                current_audio = AudioSegment.from_mp3(audio_file['audio_path'])

                # Add the current audio to the final audio
                final_audio += current_audio

                # Add a pause after the dialogue
                final_audio += AudioSegment.silent(
                    duration=self.pause_duration)

            # Save the final concatenated audio
            output_path = self.output_dir / "podcast_final.mp3"
            final_audio.export(str(output_path))

            return str(output_path)

        except Exception as e:
            print(f"Error concatenating audio files: {e}")
            return ""

    def generate_podcast(self, script_json: str) -> Path | str:
        """Generate individual audio files and concatenate them into a single podcast"""
        # Set the output directory based on the title
        self.output_dir = Path("assets/podcast") / self.tittle
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate individual audio files
        audio_files = self.process_script(script_json)

        if not audio_files:
            return ""

        # Concatenate all audio files
        final_podcast: Path = Path(self.concatenate_audio_files(audio_files))

        # Return the path relative to the project root
        return final_podcast


if __name__ == "__main__":
    # Example usage

    # ? Gradio UI for testing

    import gradio as gr  # type: ignore
    from utils.env_loader import load_environment_variables, OPENAI_API_KEY

    load_environment_variables()
    script_test = {
        "title": "GUION DEL PODCAST",
        "dialogue": [
            {
                "character": "Alfonso",
                "message": "¡Bienvenidos al podcast de PodIA"
            },
            {
                "character": "Patricia",
                "message": "¡Hola a todos!!"
            },
            {
                "character": "Alfonso",
                "message": "¡Hey, Patricia!"
            }
        ]

    }

    def generate_podcast(script_json: str) -> Path | str:
        voice_generator = VoiceGenerator(api_key=str(OPENAI_API_KEY))
        final_path = voice_generator.generate_podcast(script_json)
        # Verify the file exists before returning
        if Path(final_path).exists():
            print(f"Podcast generated successfully: {final_path}")
            return final_path
        print('No se encontró el archivo final')
        return ""

    def ui():
        with gr.Blocks() as iface:
            gr.Markdown("# Podcast Generator")
            gr.Markdown("Generate a podcast from a script.")

            with gr.Row():
                input_text = gr.Textbox(
                    label="Script JSON",
                    placeholder="Enter your podcast script in JSON format",
                    lines=10
                )

            with gr.Row():
                generate_btn = gr.Button("Generate Podcast")

            with gr.Row():
                audio_output = gr.Audio(
                    label="Podcast Final",
                    type="filepath",
                    autoplay=False,
                    show_label=True,
                    interactive=False,
                )

            generate_btn.click(
                fn=generate_podcast,
                inputs=[input_text],
                outputs=[audio_output]
            )

            gr.Examples(
                examples=[json.dumps(script_test, indent=2)],
                inputs=input_text
            )

        iface.launch()

    ui()
