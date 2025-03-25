import json

def clean_json(data) -> dict:
    """Удаляет нулевые байты из всех строк в JSON."""
    if isinstance(data, dict):
        return {k: clean_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_json(v) for v in data]
    elif isinstance(data, str):
        return data.replace("\u0000", "")  # Удаляем \u0000 из строк
    return data