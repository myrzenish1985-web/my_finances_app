from decimal import Decimal

def format_money(value):
    """Форматирование денежной суммы"""
    try:
        if isinstance(value, (int, float, Decimal, str)):
            amount = Decimal(str(value))
            return f"{amount:.2f}".replace('.', ',')
        return "0,00"
    except:
        return "0,00"

def format_date(date_str):
    """Форматирование даты"""
    try:
        from datetime import datetime
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d.%m.%Y")
    except:
        return date_str

def format_currency(value, currency="₽"):
    """Форматирование валюты"""
    return f"{format_money(value)} {currency}"