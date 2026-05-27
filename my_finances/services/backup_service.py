import json
import sqlite3
from pathlib import Path
from datetime import datetime
from database import get_db_connection, DB_PATH

class BackupService:
    @staticmethod
    def export_to_json(filepath):
        """Экспорт всех данных в JSON"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Получаем все данные из всех таблиц
            tables = [
                "income_accounts", "incomes", "budgets", "budget_history",
                "expenses", "transfers", "settings", "currencies"
            ]
            
            backup_data = {
                "version": 1,
                "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": {}
            }
            
            for table in tables:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                backup_data["data"][table] = [dict(row) for row in rows]
            
            conn.close()
            
            # Сохраняем в файл
            file_path = Path(filepath)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
            
            # Логируем бэкап
            BackupService.log_backup(str(file_path))
            
            return {"success": True, "message": f"Бэкап сохранен: {file_path}"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка экспорта: {str(e)}"}
    
    @staticmethod
    def import_from_json(filepath):
        """Импорт данных из JSON"""
        try:
            file_path = Path(filepath)
            if not file_path.exists():
                return {"success": False, "message": "Файл не найден"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Проверка версии
            if backup_data.get("version") != 1:
                return {"success": False, "message": "Неверная версия бэкапа"}
            
            # Создаем резервную копию текущей БД
            backup_path = DB_PATH.parent / f"backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            conn_src = sqlite3.connect(str(DB_PATH))
            conn_dst = sqlite3.connect(str(backup_path))
            conn_src.backup(conn_dst)
            conn_src.close()
            conn_dst.close()
            
            # Импортируем данные
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Очищаем таблицы
            tables = ["transfers", "expenses", "incomes", "budget_history", 
                     "budgets", "income_accounts", "currencies", "settings"]
            
            for table in tables:
                cursor.execute(f"DELETE FROM {table}")
            
            # Восстанавливаем данные
            for table, rows in backup_data["data"].items():
                if table in tables and rows:
                    for row in rows:
                        columns = ', '.join(row.keys())
                        placeholders = ', '.join(['?'] * len(row))
                        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                        cursor.execute(query, list(row.values()))
            
            conn.commit()
            conn.close()
            
            # Логируем восстановление
            BackupService.log_backup(f"RESTORE from {filepath}")
            
            return {"success": True, "message": "Данные восстановлены из бэкапа"}
        except Exception as e:
            return {"success": False, "message": f"Ошибка импорта: {str(e)}"}
    
    @staticmethod
    def log_backup(path):
        """Логирование операций бэкапа"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO backups_log (path, created_at)
                VALUES (?, ?)
            """, (path, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Ошибка логирования бэкапа: {e}")
    
    @staticmethod
    def get_backup_history():
        """Получение истории бэкапов"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM backups_log 
                ORDER BY created_at DESC 
                LIMIT 20
            """)
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Ошибка получения истории бэкапов: {e}")
            return []