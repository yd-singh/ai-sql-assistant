import os
import yaml
from assistant_utils.assistant_utils import (
    get_client,
    create_assistant_from_file,
    update_assistant_instructions_from_file,
    load_assistant_ids,
    get_assistant_details
)

CONFIG_PATH = "assistant_utils/assistants_config.yaml"
ORG_API_KEY = os.getenv("ORG_OPENAI_API_KEY")

def load_config(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)

def create_or_update_assistants():
    client = get_client(ORG_API_KEY)
    config = load_config(CONFIG_PATH)
    assistant_ids = load_assistant_ids()

    for assistant in config.get("assistants", []):
        name = assistant["name"]
        model = assistant["model"]
        instruction_file = assistant["instruction_file"]
        reasoning = assistant.get("reasoning", "high")

        if name in assistant_ids:
            update_assistant_instructions_from_file(client, name, instruction_file)
        else:
            create_assistant_from_file(client, name, model, instruction_file, reasoning)

def get_and_print_assistant_details():
    client = get_client(ORG_API_KEY)
    assistant_ids = load_assistant_ids()
    for name, assistant_id in assistant_ids.items():
        details = get_assistant_details(client, assistant_id)
        print(f"Assistant '{name}' details: {details}")

if __name__ == "__main__":
    get_and_print_assistant_details()
    create_or_update_assistants()