from database import get_db_connection
from models import Money
from datetime import datetime, timedelta
from decimal import Decimal
import json

class ReportService:
    @staticmethod
    def get_summary(start_date, end_date):
        """Получение сводки за период"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Доходы
            cursor.execute("""
                SELECT SUM(amount) as total FROM incomes 
                WHERE date BETWEEN ? AND ?
            """, (start_date, end_date))
            total_income = cursor.fetchone()["total"] or "0"
            
            # Расходы
            cursor.execute("""
                SELECT SUM(amount) as total FROM expenses 
                WHERE date BETWEEN ? AND ?
            """, (start_date, end_date))
            total_expense = cursor.fetchone()["total"] or "0"
            
            # Переводы
            cursor.execute("""
                SELECT SUM(amount) as total FROM transfers 
                WHERE date BETWEEN ? AND ?
            """, (start_date, end_date))
            total_transfers = cursor.fetchone()["total"] or "0"
            
            conn.close()
            
            income_money = Money(total_income)
            expense_money = Money(total_expense)
            
            return {
                "start_date": start_date,
                "end_date": end_date,
                "income": str(income_money),
                "income_obj": income_money,
                "expense": str(expense_money),
                "expense_obj": expense_money,
                "transfers": str(Money(total_transfers)),
                "balance": str(income_money - expense_money),
                "balance_obj": income_money - expense_money
            }
        except Exception as e:
            print(f"Ошибка получения сводки: {e}")
            return None
    
    @staticmethod
    def get_income_by_account(start_date, end_date):
        """Доходы по счетам"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT a.name, SUM(i.amount) as total
                FROM incomes i
                LEFT JOIN income_accounts a ON i.account_id = a.id
                WHERE i.date BETWEEN ? AND ?
                GROUP BY i.account_id
                ORDER BY total DESC
            """, (start_date, end_date))
            
            rows = cursor.fetchall()
            conn.close()
            
            result = []
            for row in rows:
                if row["name"]:  # Пропускаем удаленные счета
                    result.append({
                        "name": row["name"],
                        "total": row["total"] if row["total"] else "0"
                    })
            
            return result
        except Exception as e:
            print(f"Ошибка получения доходов по счетам: {e}")
            return []
    
    @staticmethod
    def get_expenses_by_budget(start_date, end_date):
        """Расходы по бюджетам"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT b.name, SUM(e.amount) as total
                FROM expenses e
                LEFT JOIN budgets b ON e.budget_id = b.id
                WHERE e.date BETWEEN ? AND ?
                GROUP BY e.budget_id
                ORDER BY total DESC
            """, (start_date, end_date))
            
            rows = cursor.fetchall()
            conn.close()
            
            result = []
            for row in rows:
                if row["name"]:  # Пропускаем удаленные бюджеты
                    result.append({
                        "name": row["name"],
                        "total": row["total"] if row["total"] else "0"
                    })
            
            return result
        except Exception as e:
            print(f"Ошибка получения расходов по бюджетам: {e}")
            return []
    
    @staticmethod
    def get_daily_balance(start_date, end_date):
        """Ежедневный баланс"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Получаем все дни в диапазоне
            date_list = []
            current = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            while current <= end:
                date_str = current.strftime("%Y-%m-%d")
                
                # Доходы за день
                cursor.execute("SELECT SUM(amount) as total FROM incomes WHERE date = ?", (date_str,))
                daily_income = cursor.fetchone()["total"] or "0"
                
                # Расходы за день
                cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE date = ?", (date_str,))
                daily_expense = cursor.fetchone()["total"] or "0"
                
                date_list.append({
                    "date": date_str,
                    "income": daily_income,
                    "expense": daily_expense,
                    "balance": str(Money(daily_income) - Money(daily_expense))
                })
                
                current += timedelta(days=1)
            
            conn.close()
            return date_list
        except Exception as e:
            print(f"Ошибка получения дневного баланса: {e}")
            return []
    
    @staticmethod
    def export_to_json(start_date, end_date):
        """Экспорт отчета в JSON"""
        try:
            summary = ReportService.get_summary(start_date, end_date)
            income_by_account = ReportService.get_income_by_account(start_date, end_date)
            expenses_by_budget = ReportService.get_expenses_by_budget(start_date, end_date)
            daily_balance = ReportService.get_daily_balance(start_date, end_date)
            
            report = {
                "period": {"start": start_date, "end": end_date},
                "summary": summary,
                "income_by_account": income_by_account,
                "expenses_by_budget": expenses_by_budget,
                "daily_balance": daily_balance,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(report, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка экспорта отчета: {e}")
            return None