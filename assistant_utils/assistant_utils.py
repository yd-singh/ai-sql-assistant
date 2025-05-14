import os
import json
from dotenv import load_dotenv
from openai import OpenAI

ASSISTANT_CONFIG_FILE = "assistant_ids.json"

def get_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)

def save_assistant_id(name: str, assistant_id: str):
    data = {}
    if os.path.exists(ASSISTANT_CONFIG_FILE):
        with open(ASSISTANT_CONFIG_FILE, "r") as f:
            data = json.load(f)

    data[name] = assistant_id

    with open(ASSISTANT_CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved assistant '{name}' with ID: {assistant_id}")

def load_assistant_ids():
    # Load environment variables
    load_dotenv()

    # Retrieve assistant IDs from environment variables
    sql_assistant_id = os.getenv("SQL_ASSISTANT_ID")
    qreview_assistant_id = os.getenv("QREVIEW_ASSISTANT_ID")
    return {
        "SQL Assistant": sql_assistant_id,
        "QReview Assistant": qreview_assistant_id
    }

def create_assistant_from_file(
    client: OpenAI,
    name: str,
    model: str,
    instruction_file: str,
    reasoning: str = "high"
) -> str:
    if not os.path.exists(instruction_file):
        raise FileNotFoundError(f"Instruction file not found: {instruction_file}")

    with open(instruction_file, "r") as f:
        instructions = f.read()

    tool_config = {
        "type": "code_interpreter"
    }
    
    # If the model is "o3-mini", do not include any tools.
    tools = [] if model == "o3-mini" else [tool_config]

    metadata = {
        "reasoning_depth": reasoning
    }

    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model=model,
        tools=tools,
        metadata=metadata
    )

    assistant_id = assistant.id
    save_assistant_id(name, assistant_id)
    return assistant_id

def update_assistant_instructions_from_file(
    client: OpenAI,
    name: str,
    instruction_file: str
) -> str:
    assistant_ids = load_assistant_ids()

    if name not in assistant_ids:
        print(f"⚠️ Assistant '{name}' not found in {ASSISTANT_CONFIG_FILE}. Skipping update.")
        return None

    assistant_id = assistant_ids[name]

    if not os.path.exists(instruction_file):
        raise FileNotFoundError(f"Instruction file not found: {instruction_file}")

    with open(instruction_file, "r") as f:
        new_instructions = f.read()

    updated = client.beta.assistants.update(
        assistant_id=assistant_id,
        instructions=new_instructions
    )

    print(f"✅ Updated instructions for assistant '{name}' (ID: {assistant_id})")
    return updated.id

def get_assistant_details(client: OpenAI, assistant_id: str):
    return client.beta.assistants.retrieve(assistant_id=assistant_id)