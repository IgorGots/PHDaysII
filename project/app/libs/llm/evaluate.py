import yaml
import os

from typing import Generator

from libs.messages import TgMessage
from libs.llm.tools import compare_answers
from libs.llm import brain

import libs.logger as logger
log = logger.setup_applevel_logger()


def get_yaml_files(path: str = '/tests') -> Generator[str, None, None]:
    """
    Get YAML files from a specific directory.

    Args:
    - path (str): The directory path.

    Returns:
    - List[str]: List of YAML file paths.
    """

    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                yield os.path.join(root, file)


def read_yaml_file(file_path: str) -> dict:
    """
    Read a YAML file and return its contents as a dictionary.

    Args:
    - file_path (str): The path to the YAML file.

    Returns:
    - dict: The contents of the YAML file as a dictionary.
    """
    with open(file_path, "r") as yaml_file:
        yaml_content: dict = yaml.safe_load(yaml_file)
    return yaml_content


def evaluate(message: str) -> str:

    results = ''

    for file in get_yaml_files():
        data = read_yaml_file(file)

        content = brain.soc_brain(
            TgMessage(
                sender_message=data['question'],
                sender_id=0,
                sender_name='',
                chat_id=0,
                message_id=0
            )
        )

        answer = compare_answers(
            data['question'],
            data['answer'],
            content
        )

        results += f'''**Вопрос**: {data['question']}\n{answer}\n'''

    return results
