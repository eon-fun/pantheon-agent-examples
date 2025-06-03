def clean_json(data) -> dict:
    """Удаляет нулевые байты из всех строк в JSON."""
    if isinstance(data, dict):
        return {k: clean_json(v) for k, v in data.items()}
    if isinstance(data, list):
        return [clean_json(v) for v in data]
    if isinstance(data, str):
        return data.replace("\u0000", "")  # Удаляем \u0000 из строк
    return data


def escape_markdown_v2(text):
    """Экранирует специальные символы для MarkdownV2"""
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)


def split_text(text, max_length=4000):
    """Функция для разбиения длинного текста на части"""
    parts = []
    while text:
        parts.append(text[:max_length])
        text = text[max_length:]
    return parts
