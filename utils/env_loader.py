from pathlib import Path
import os
from dotenv import load_dotenv

# Variable global para almacenar la clave API
OPENAI_API_KEY = None

# Inicializar variables de entorno cuando se importa el módulo

def init_environment_variables(): return globals().update(
    {"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")})

init_environment_variables()

# ? Ejemplo de cómo usar la variable OPENAI_API_KEY en otros archivos

"""
    # ? from utils.env_loader import OPENAI_API_KEY 

    #* Usar la variable OPENAI_API_KEY
    #? print(OPENAI_API_KEY)

"""


def load_environment_variables() -> dict:
    """
    Cargar la variable de entorno OPENAI_API_KEY desde el archivo .env en la raíz del proyecto.
    Establece la variable global OPENAI_API_KEY y devuelve un diccionario con la variable de entorno cargada.
    """
    global OPENAI_API_KEY

    # Obtener el directorio raíz del proyecto (asume que este archivo está en utils/dotenv.py)
    project_root = Path(__file__).parent.parent.parent

    # Ruta al archivo .env
    env_path = project_root / '.env'

    # Cargar el archivo .env
    load_dotenv(dotenv_path=env_path)

    # Establecer la variable global
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Devolver un diccionario solo con OPENAI_API_KEY
    return {"OPENAI_API_KEY": OPENAI_API_KEY}


# ? Dev Purpose
if __name__ == '__main__':
    def print_environment_variables() -> None:
        """
        Imprimir todas las variables de entorno.
        """
        for key, value in load_environment_variables().items():
            print(f'{key}: {value}')

    print_environment_variables()
