from database import get_db_connection
from models import Money
from datetime import datetime

class TransferService:
    @staticmethod
    def add_transfer(date_str, from_account, to_account, amount, transfer_type="income", comment=""):
        """Добавление перевода"""
        try:
            if not date_str:
                raise ValueError("Дата не указана")
            if from_account == to_account:
                raise ValueError("Счета должны быть разными")
            
            money = Money(amount)
            if money.value <= 0:
                raise ValueError("Сумма должна быть положительной")
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO transfers (date, from_account, to_account, amount, transfer_type, comment, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (date_str, from_account, to_account, str(money.value), transfer_type, comment,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            transfer_id = cursor.lastrowid
            conn.close()
            
            return {"success": True, "id": transfer_id, "message": "Перевод добавлен"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def delete_transfer(transfer_id):
        """Удаление перевода"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transfers WHERE id = ?", (transfer_id,))
            conn.commit()
            conn.close()
            return {"success": True, "message": "Перевод удален"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    @staticmethod
    def get_all_transfers():
        """Получение всех переводов"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT t.*, 
                       a1.name as from_name, a2.name as to_name
                FROM transfers t
                LEFT JOIN income_accounts a1 ON t.from_account = a1.id
                LEFT JOIN income_accounts a2 ON t.to_account = a2.id
                WHERE (a1.is_deleted = 0 OR a1.is_deleted IS NULL)
                  AND (a2.is_deleted = 0 OR a2.is_deleted IS NULL)
                ORDER BY t.date DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            transfers = []
            for row in rows:
                transfers.append({
                    "id": row["id"],
                    "date": row["date"],
                    "from_account": row["from_account"],
                    "from_name": row["from_name"] if row["from_name"] else "Удален",
                    "to_account": row["to_account"],
                    "to_name": row["to_name"] if row["to_name"] else "Удален",
                    "amount": row["amount"],
                    "transfer_type": row["transfer_type"],
                    "comment": row["comment"] or "",
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            return transfers
        except Exception as e:
            print(f"Ошибка получения переводов: {e}")
            return []