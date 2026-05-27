import re
from datetime import datetime

def validate_required(value):
    """Проверка обязательного поля"""
    return bool(value and str(value).strip())

def validate_positive_amount(value):
    """Проверка положительной суммы"""
    try:
        from decimal import Decimal
        amount = Decimal(str(value).replace(',', '.'))
        return amount > 0
    except:
        return False

def validate_date(date_str):
    """Проверка даты"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except:
        return False

def validate_email(email):
    """Проверка email (для возможного будущего использования)"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """Проверка телефона (для возможного будущего использования)"""
    # Упрощенная проверка
    digits = re.sub(r'\D', '', phone)
    return len(digits) >= 10