from database import get_db_connection
from models import IncomeAccount
from datetime import datetime

class AccountService:
    @staticmethod
    def add_account(name, comment="", is_active=True):
        """Добавление счета"""
        try:
            if not name:
                raise ValueError("Название не указано")
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO income_accounts (name, comment, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (name, comment, 1 if is_active else 0,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            account_id = cursor.lastrowid
            conn.close()
            
            return {"success": True, "id": account_id, "message": "Счет добавлен"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def update_account(account_id, name=None, comment=None, is_active=None):
        """Обновление счета"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            
            if comment is not None:
                updates.append("comment = ?")
                params.append(comment)
            
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)
            
            if updates:
                updates.append("updated_at = ?")
                params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                params.append(account_id)
                
                query = f"UPDATE income_accounts SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Счет обновлен"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def delete_account(account_id):
        """Удаление счета (с проверкой операций)"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Проверяем, есть ли доходы по этому счету
            cursor.execute("SELECT COUNT(*) as count FROM incomes WHERE account_id = ?", (account_id,))
            incomes_count = cursor.fetchone()["count"]
            
            if incomes_count > 0:
                conn.close()
                return {"success": False, "message": "Невозможно удалить счет с доходами. Поместите его в архив."}
            
            # Мягкое удаление
            cursor.execute("UPDATE income_accounts SET is_deleted = 1, updated_at = ? WHERE id = ?",
                          (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), account_id))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Счет удален"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_all_accounts(include_archived=False):
        """Получение всех счетов"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if include_archived:
                cursor.execute("""
                    SELECT * FROM income_accounts 
                    WHERE is_deleted = 0
                    ORDER BY is_active DESC, name
                """)
            else:
                cursor.execute("""
                    SELECT * FROM income_accounts 
                    WHERE is_deleted = 0 AND is_active = 1
                    ORDER BY name
                """)
            
            rows = cursor.fetchall()
            conn.close()
            
            accounts = []
            for row in rows:
                accounts.append({
                    "id": row["id"],
                    "name": row["name"],
                    "comment": row["comment"] or "",
                    "is_active": bool(row["is_active"]),
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            return accounts
        except Exception as e:
            print(f"Ошибка получения счетов: {e}")
            return []