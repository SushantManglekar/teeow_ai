import json

def load_intent_object(intent_name: str, file_path: str) -> dict:
    """
    Load the intent object from JSON file for a given intent name.
    
    Args:
        intent_name (str): The intent to look for (e.g., "recommendation").
        file_path (str): Path to the JSON knowledge base file.

    Returns:
        dict: The matched intent object.

    Raises:
        ValueError: If the intent is not found in the knowledge base.
    """
    with open(file_path, "r") as f:
        kb = json.load(f)

    for obj in kb.get("intents", []):
        if obj["intent"] == intent_name:
            return obj

    raise ValueError(f"Intent '{intent_name}' not found in {file_path}")
