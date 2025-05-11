import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('/app/utils/.env')
load_dotenv(dotenv_path=dotenv_path)

env = dict(
    PYTHON_API_USERNAME = os.getenv('PYTHON_API_USERNAME'),
    PYTHON_API_PASSWORD = os.getenv('PYTHON_API_PASSWORD'),
)
