def format_json_as_text(data: dict, indent: int = 0) -> str:
    """
    Recursively converts a nested JSON/dictionary into a readable text format.
    Handles lists, nested dicts, and flat key-value pairs.
    """
    lines = []
    spacer = "  " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{spacer}{key.capitalize()}:")
                lines.append(format_json_as_text(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{spacer}{key.capitalize()}:")
                for idx, item in enumerate(value, start=1):
                    if isinstance(item, (dict, list)):
                        lines.append(f"{spacer}  {idx}.")
                        lines.append(format_json_as_text(item, indent + 2))
                    else:
                        lines.append(f"{spacer}  - {item}")
            else:
                lines.append(f"{spacer}{key.capitalize()}: {value}")
    elif isinstance(data, list):
        for item in data:
            lines.append(format_json_as_text(item, indent))
    else:
        lines.append(f"{spacer}{data}")

    return "\n".join(lines)
