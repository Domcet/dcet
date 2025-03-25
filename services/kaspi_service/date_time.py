from datetime import datetime

def make_normal_datetime(date_string: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Преобразует строку в объект datetime с заданным форматом.
    По умолчанию формат: '2025-03-23 14:30:00'
    """
    try:
        return datetime.strptime(date_string, format)
    except ValueError as e:
        raise ValueError(f"Неверный формат даты: {e}")
