from decimal import Decimal, getcontext, ROUND_HALF_UP
from datetime import datetime

getcontext().prec = 28

class Money:
    """Класс для безопасной работы с деньгами"""
    
    def __init__(self, value):
        if isinstance(value, Decimal):
            self.value = value
        elif isinstance(value, Money):
            self.value = value.value
        elif isinstance(value, (int, float, str)):
            try:
                self.value = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            except:
                self.value = Decimal('0')
        else:
            raise TypeError(f"Неверный тип для Money: {type(value)}")
    
    def __str__(self):
        return f"{self.value:.2f}"
    
    def __repr__(self):
        return f"Money('{self.value:.2f}')"
    
    def __add__(self, other):
        return Money(self.value + self._to_money(other).value)
    
    def __sub__(self, other):
        return Money(self.value - self._to_money(other).value)
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Money(self.value * other)
        return Money(self.value * self._to_money(other).value)
    
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Money(self.value / other)
        return Money(self.value / self._to_money(other).value)
    
    def __gt__(self, other):
        return self.value > self._to_money(other).value
    
    def __lt__(self, other):
        return self.value < self._to_money(other).value
    
    def __eq__(self, other):
        return self.value == self._to_money(other).value
    
    def __float__(self):
        return float(self.value)
    
    def to_cents(self):
        return int(self.value * 100)
    
    @staticmethod
    def from_cents(cents):
        return Money(Decimal(cents) / Decimal(100))
    
    @staticmethod
    def _to_money(value):
        if isinstance(value, Money):
            return value
        return Money(value)
    
    @property
    def is_positive(self):
        return self.value > 0
    
    @property
    def is_negative(self):
        return self.value < 0

class Transaction:
    """Базовый класс для транзакций"""
    
    def __init__(self, date=None, amount=None, comment=""):
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.amount = Money(amount) if amount else Money(0)
        self.comment = comment
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at
    
    def validate(self):
        if not self.date:
            raise ValueError("Дата не указана")
        if self.amount.value <= 0:
            raise ValueError("Сумма должна быть положительной")
        return True

class Income(Transaction):
    """Доход"""
    
    def __init__(self, date=None, account_id=None, amount=None, comment="", id=None):
        super().__init__(date, amount, comment)
        self.id = id
        self.account_id = account_id
    
    def validate(self):
        super().validate()
        if not self.account_id:
            raise ValueError("Счет дохода не выбран")
        return True

class Expense(Transaction):
    """Расход"""
    
    def __init__(self, date=None, budget_id=None, amount=None, comment="", id=None):
        super().__init__(date, amount, comment)
        self.id = id
        self.budget_id = budget_id
    
    def validate(self):
        super().validate()
        if not self.budget_id:
            raise ValueError("Бюджет не выбран")
        return True

class Budget:
    """Бюджет"""
    
    PERIOD_MONTH = "month"
    PERIOD_QUARTER = "quarter"
    PERIOD_YEAR = "year"
    
    PERIODS = {
        PERIOD_MONTH: "Месяц",
        PERIOD_QUARTER: "Квартал",
        PERIOD_YEAR: "Год"
    }
    
    def __init__(self, name, amount, period, start_date=None, end_date=None, 
                 comment="", is_active=True, id=None):
        self.id = id
        self.name = name
        self.amount = Money(amount)
        self.period = period
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active
        self.comment = comment
    
    def validate(self):
        if not self.name:
            raise ValueError("Название бюджета не указано")
        if self.amount.value <= 0:
            raise ValueError("Сумма бюджета должна быть положительной")
        if self.period not in self.PERIODS:
            raise ValueError(f"Неверный период: {self.period}")
        return True

class IncomeAccount:
    """Счет дохода"""
    
    def __init__(self, name, comment="", is_active=True, id=None):
        self.id = id
        self.name = name
        self.comment = comment
        self.is_active = is_active
    
    def validate(self):
        if not self.name:
            raise ValueError("Название счета не указано")
        return True