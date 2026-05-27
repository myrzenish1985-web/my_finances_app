from database import get_db_connection
from models import Money, Expense
from datetime import datetime

class ExpenseService:
    @staticmethod
    def add_expense(date_str, budget_id, amount, comment=""):
        """Добавление расхода"""
        try:
            if not date_str:
                raise ValueError("Дата не указана")
            if not budget_id:
                raise ValueError("Бюджет не выбран")
            
            money = Money(amount)
            if money.value <= 0:
                raise ValueError("Сумма должна быть положительной")
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Проверяем остаток бюджета
            remaining = BudgetService.get_budget_remaining(budget_id)
            if money > remaining:
                # Предупреждение, но сохраняем
                warning = "Внимание: расход превышает остаток бюджета!"
            else:
                warning = None
            
            cursor.execute("""
                INSERT INTO expenses (date, budget_id, amount, comment, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date_str, budget_id, str(money.value), comment,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            expense_id = cursor.lastrowid
            conn.close()
            
            result = {"success": True, "id": expense_id, "message": "Расход добавлен"}
            if warning:
                result["warning"] = warning
            
            return result
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def update_expense(expense_id, date_str, budget_id, amount, comment=""):
        """Обновление расхода"""
        try:
            money = Money(amount)
            if money.value <= 0:
                raise ValueError("Сумма должна быть положительной")
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE expenses 
                SET date = ?, budget_id = ?, amount = ?, comment = ?, updated_at = ?
                WHERE id = ?
            """, (date_str, budget_id, str(money.value), comment,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"), expense_id))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Расход обновлен"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def delete_expense(expense_id):
        """Удаление расхода"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            conn.close()
            return {"success": True, "message": "Расход удален"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_all_expenses(sort_by="date", order="DESC"):
        """Получение всех расходов"""
        try:
            valid_sort_fields = {"date": "date", "budget": "budget_id", "amount": "amount"}
            sort_field = valid_sort_fields.get(sort_by, "date")
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = f"""
                SELECT e.*, b.name as budget_name 
                FROM expenses e
                LEFT JOIN budgets b ON e.budget_id = b.id
                WHERE b.is_deleted = 0 OR b.is_deleted IS NULL
                ORDER BY {sort_field} {order}
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
            
            expenses = []
            for row in rows:
                expenses.append({
                    "id": row["id"],
                    "date": row["date"],
                    "budget_id": row["budget_id"],
                    "budget_name": row["budget_name"] if row["budget_name"] else "Удален",
                    "amount": row["amount"],
                    "comment": row["comment"] or "",
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            return expenses
        except Exception as e:
            print(f"Ошибка получения расходов: {e}")
            return []
    
    @staticmethod
    def get_total_expense(start_date=None, end_date=None):
        """Получение общей суммы расходов за период"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if start_date and end_date:
                cursor.execute("""
                    SELECT SUM(amount) as total FROM expenses 
                    WHERE date BETWEEN ? AND ?
                """, (start_date, end_date))
            else:
                cursor.execute("SELECT SUM(amount) as total FROM expenses")
            
            row = cursor.fetchone()
            conn.close()
            
            return Money(row["total"] if row["total"] else 0)
        except Exception as e:
            print(f"Ошибка подсчета расходов: {e}")
            return Money(0)