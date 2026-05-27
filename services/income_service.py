from database import get_db_connection
from models import Money, Income
from decimal import Decimal
from datetime import datetime

class IncomeService:
    @staticmethod
    def add_income(date_str, account_id, amount, comment=""):
        """Добавление дохода"""
        try:
            # Валидация
            if not date_str:
                raise ValueError("Дата не указана")
            if not account_id:
                raise ValueError("Счет не выбран")
            
            money = Money(amount)
            if money.value <= 0:
                raise ValueError("Сумма должна быть положительной")
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO incomes (date, account_id, amount, comment, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date_str, account_id, str(money.value), comment, 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            income_id = cursor.lastrowid
            conn.close()
            
            return {"success": True, "id": income_id, "message": "Доход добавлен"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def update_income(income_id, date_str, account_id, amount, comment=""):
        """Обновление дохода"""
        try:
            money = Money(amount)
            if money.value <= 0:
                raise ValueError("Сумма должна быть положительной")
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE incomes 
                SET date = ?, account_id = ?, amount = ?, comment = ?, updated_at = ?
                WHERE id = ?
            """, (date_str, account_id, str(money.value), comment,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"), income_id))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Доход обновлен"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def delete_income(income_id):
        """Удаление дохода"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM incomes WHERE id = ?", (income_id,))
            conn.commit()
            conn.close()
            return {"success": True, "message": "Доход удален"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_all_incomes(sort_by="date", order="DESC"):
        """Получение всех доходов"""
        try:
            valid_sort_fields = {"date": "date", "account": "account_id", "amount": "amount"}
            sort_field = valid_sort_fields.get(sort_by, "date")
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = f"""
                SELECT i.*, a.name as account_name 
                FROM incomes i
                LEFT JOIN income_accounts a ON i.account_id = a.id
                WHERE a.is_deleted = 0 OR a.is_deleted IS NULL
                ORDER BY {sort_field} {order}
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            incomes = []
            for row in rows:
                incomes.append({
                    "id": row["id"],
                    "date": row["date"],
                    "account_id": row["account_id"],
                    "account_name": row["account_name"] if row["account_name"] else "Удален",
                    "amount": row["amount"],
                    "comment": row["comment"] or "",
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            return incomes
        except Exception as e:
            print(f"Ошибка получения доходов: {e}")
            return []
    
    @staticmethod
    def get_total_income(start_date=None, end_date=None):
        """Получение общей суммы доходов за период"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if start_date and end_date:
                cursor.execute("""
                    SELECT SUM(amount) as total FROM incomes 
                    WHERE date BETWEEN ? AND ?
                """, (start_date, end_date))
            else:
                cursor.execute("SELECT SUM(amount) as total FROM incomes")
            
            row = cursor.fetchone()
            conn.close()
            
            return Money(row["total"] if row["total"] else 0)
        except Exception as e:
            print(f"Ошибка подсчета доходов: {e}")
            return Money(0)