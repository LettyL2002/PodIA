from pathlib import Path
import os
from dotenv import load_dotenv

# Global variable to store the API key
OPENAI_API_KEY = None

# ? Example of how to use the OPENAI_API_KEY variable in other files

"""
    # ? from utils.env_loader import OPENAI_API_KEY 

    #* Use the OPENAI_API_KEY variable
    #? print(OPENAI_API_KEY)

"""


def load_environment_variables() -> dict:
    """
    Load OPENAI_API_KEY environment variable from .env file in the project root.
    Sets the global OPENAI_API_KEY variable and returns a dict with the loaded environment variable.
    """
    global OPENAI_API_KEY

    # Get the project root directory (assumes this file is in utils/dotenv.py)
    project_root = Path(__file__).parent.parent.parent

    # Path to .env file
    env_path = project_root / '.env'

    # Load the .env file
    load_dotenv(dotenv_path=env_path)

    # Set the global variable
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Return a dictionary with just OPENAI_API_KEY
    return {"OPENAI_API_KEY": OPENAI_API_KEY}

# ? For Dev purposes


def print_environment_variables() -> None:
    """
    Print all environment variables.
    """
    for key, value in load_environment_variables().items():
        print(f'{key}: {value}')


# ? For Dev purposes
if __name__ == '__main__':
    print_environment_variables()
