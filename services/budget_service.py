from database import get_db_connection
from models import Money, Budget
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class BudgetService:
    @staticmethod
    def create_budget(name, amount, period, start_date=None, end_date=None, comment=""):
        """Создание бюджета"""
        try:
            if not name:
                raise ValueError("Название не указано")
            
            money = Money(amount)
            if money.value <= 0:
                raise ValueError("Сумма должна быть положительной")
            
            # Проверка количества бюджетов
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM budgets WHERE is_deleted = 0")
            count = cursor.fetchone()["count"]
            
            if count >= 50:
                conn.close()
                return {"success": False, "message": "Превышен лимит бюджетов (максимум 50)"}
            
            # Автоматический расчет дат
            if not start_date:
                start_date = datetime.now().strftime("%Y-%m-%d")
            
            if not end_date:
                if period == Budget.PERIOD_MONTH:
                    end_date = (datetime.now() + relativedelta(months=1)).strftime("%Y-%m-%d")
                elif period == Budget.PERIOD_QUARTER:
                    end_date = (datetime.now() + relativedelta(months=3)).strftime("%Y-%m-%d")
                else:  # year
                    end_date = (datetime.now() + relativedelta(years=1)).strftime("%Y-%m-%d")
            
            cursor.execute("""
                INSERT INTO budgets (name, amount, period, start_date, end_date, 
                                   is_active, comment, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
            """, (name, str(money.value), period, start_date, end_date, comment,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            budget_id = cursor.lastrowid
            
            # Сохраняем историю
            cursor.execute("""
                INSERT INTO budget_history (budget_id, amount, changed_at)
                VALUES (?, ?, ?)
            """, (budget_id, str(money.value), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "id": budget_id, "message": "Бюджет создан"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def update_budget(budget_id, name=None, amount=None, period=None, 
                     start_date=None, end_date=None, is_active=None, comment=None):
        """Обновление бюджета с сохранением истории"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Получаем текущий бюджет
            cursor.execute("SELECT * FROM budgets WHERE id = ?", (budget_id,))
            old_budget = cursor.fetchone()
            
            if not old_budget:
                conn.close()
                return {"success": False, "message": "Бюджет не найден"}
            
            updates = []
            params = []
            
            if name:
                updates.append("name = ?")
                params.append(name)
            
            if amount:
                money = Money(amount)
                updates.append("amount = ?")
                params.append(str(money.value))
                
                # Сохраняем в историю при изменении суммы
                cursor.execute("""
                    INSERT INTO budget_history (budget_id, amount, changed_at)
                    VALUES (?, ?, ?)
                """, (budget_id, str(money.value), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            if period:
                updates.append("period = ?")
                params.append(period)
            
            if start_date:
                updates.append("start_date = ?")
                params.append(start_date)
            
            if end_date:
                updates.append("end_date = ?")
                params.append(end_date)
            
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)
            
            if comment is not None:
                updates.append("comment = ?")
                params.append(comment)
            
            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                params.append(budget_id)
                
                query = f"UPDATE budgets SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Бюджет обновлен"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def delete_budget(budget_id, soft_delete=True):
        """Удаление бюджета (мягкое или жесткое)"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Проверяем, есть ли расходы по этому бюджету
            cursor.execute("SELECT COUNT(*) as count FROM expenses WHERE budget_id = ?", (budget_id,))
            expenses_count = cursor.fetchone()["count"]
            
            if expenses_count > 0 and soft_delete:
                # Мягкое удаление
                cursor.execute("UPDATE budgets SET is_deleted = 1, updated_at = ? WHERE id = ?",
                              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), budget_id))
                message = "Бюджет архивирован"
            elif expenses_count > 0:
                conn.close()
                return {"success": False, "message": "Невозможно удалить бюджет с расходами. Поместите его в архив."}
            else:
                # Жесткое удаление
                cursor.execute("DELETE FROM budgets WHERE id = ?", (budget_id,))
                message = "Бюджет удален"
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": message}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_all_budgets(include_archived=False):
        """Получение всех бюджетов"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if include_archived:
                cursor.execute("""
                    SELECT b.*, 
                           (SELECT SUM(amount) FROM expenses WHERE budget_id = b.id) as spent
                    FROM budgets b
                    WHERE b.is_deleted = 0
                    ORDER BY b.is_active DESC, b.created_at DESC
                """)
            else:
                cursor.execute("""
                    SELECT b.*, 
                           (SELECT SUM(amount) FROM expenses WHERE budget_id = b.id) as spent
                    FROM budgets b
                    WHERE b.is_deleted = 0 AND b.is_active = 1
                    ORDER BY b.created_at DESC
                """)
            
            rows = cursor.fetchall()
            conn.close()
            
            budgets = []
            for row in rows:
                spent = Money(row["spent"] if row["spent"] else 0)
                amount = Money(row["amount"])
                remaining = amount - spent
                
                budgets.append({
                    "id": row["id"],
                    "name": row["name"],
                    "amount": row["amount"],
                    "amount_obj": amount,
                    "period": row["period"],
                    "period_name": Budget.PERIODS.get(row["period"], row["period"]),
                    "start_date": row["start_date"],
                    "end_date": row["end_date"],
                    "is_active": bool(row["is_active"]),
                    "comment": row["comment"] or "",
                    "spent": str(spent),
                    "spent_obj": spent,
                    "remaining": str(remaining),
                    "remaining_obj": remaining,
                    "progress": float(spent.value / amount.value * 100) if amount.value > 0 else 0
                })
            
            return budgets
        except Exception as e:
            print(f"Ошибка получения бюджетов: {e}")
            return []
    
    @staticmethod
    def get_budget_remaining(budget_id):
        """Получение остатка бюджета"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT amount FROM budgets WHERE id = ?", (budget_id,))
            budget = cursor.fetchone()
            
            if not budget:
                conn.close()
                return Money(0)
            
            cursor.execute("SELECT SUM(amount) as spent FROM expenses WHERE budget_id = ?", (budget_id,))
            spent = cursor.fetchone()["spent"]
            
            conn.close()
            
            budget_amount = Money(budget["amount"])
            spent_amount = Money(spent if spent else 0)
            
            return budget_amount - spent_amount
        except Exception as e:
            print(f"Ошибка получения остатка бюджета: {e}")
            return Money(0)