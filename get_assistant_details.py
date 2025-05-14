import os
from assistant_utils.assistant_utils import get_client, get_assistant_details
from dotenv import load_dotenv
from pprint import pprint

def main():
    # Load environment variables
    load_dotenv()

    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    client = get_client(api_key)

    # Retrieve assistant IDs from environment variables
    sql_assistant_id = os.getenv("SQL_ASSISTANT_ID")
    qreview_assistant_id = os.getenv("QREVIEW_ASSISTANT_ID")
    assistant_ids = {
        "SQL Assistant": sql_assistant_id,
        "QReview Assistant": qreview_assistant_id
    }

    # Fetch and print details for each assistant
    for name, assistant_id in assistant_ids.items():
        details = get_assistant_details(client, assistant_id)
        print("-----------------------------START----------------------------")
        pprint(details, indent=4)
        print("------------------------------END------------------------------")
        #print(f"Assistant '{name}' details: {details}")

if __name__ == "__main__":
    main()
