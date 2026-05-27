import sqlite3
import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from kivymd.uix.picker import MDDatePicker  # Добавьте в начало файла

DB_PATH = Path(__file__).parent / "data.db"
DB_VERSION = 3

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def get_db_version():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'db_version'")
        row = cursor.fetchone()
        conn.close()
        if row:
            return int(row['value'])
        return 0
    except:
        return 0

def set_db_version(version):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('db_version', ?)", (str(version),))
    conn.commit()
    conn.close()

def migrate_v1_to_v2(conn):
    """Миграция: добавление индексов и soft-delete"""
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE income_accounts ADD COLUMN is_deleted INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE budgets ADD COLUMN is_deleted INTEGER DEFAULT 0")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incomes_date ON incomes(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transfers_date ON transfers(date)")

def migrate_v2_to_v3(conn):
    """Миграция: добавление валюты и логов"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS currencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            rate REAL NOT NULL,
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO currencies (code, rate) VALUES ('RUB', 1.0)")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS balance_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id INTEGER,
            old_amount TEXT,
            new_amount TEXT,
            changed_at TEXT DEFAULT (datetime('now'))
        )
    """)

def init_db():
    """Инициализация базы данных с миграциями"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    current_version = get_db_version()
    
    if current_version == 0:
        # Создание базы с нуля
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Таблицы
        cursor.executescript("""
            CREATE TABLE income_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                comment TEXT,
                is_active INTEGER DEFAULT 1,
                is_deleted INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                account_id INTEGER,
                amount TEXT NOT NULL,
                comment TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (account_id) REFERENCES income_accounts(id) ON DELETE SET NULL
            );
            
            CREATE TABLE budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount TEXT NOT NULL,
                period TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                is_active INTEGER DEFAULT 1,
                is_deleted INTEGER DEFAULT 0,
                comment TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE budget_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                budget_id INTEGER,
                amount TEXT,
                changed_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE CASCADE
            );
            
            CREATE TABLE expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                budget_id INTEGER,
                amount TEXT NOT NULL,
                comment TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE SET NULL
            );
            
            CREATE TABLE transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                from_account INTEGER,
                to_account INTEGER,
                amount TEXT NOT NULL,
                comment TEXT,
                transfer_type TEXT DEFAULT 'income',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            
            CREATE TABLE backups_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE currencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                rate REAL NOT NULL,
                updated_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE balance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id INTEGER,
                old_amount TEXT,
                new_amount TEXT,
                changed_at TEXT DEFAULT (datetime('now'))
            );
        """)
        
        # Создание индексов
        cursor.executescript("""
            CREATE INDEX idx_incomes_date ON incomes(date);
            CREATE INDEX idx_incomes_account ON incomes(account_id);
            CREATE INDEX idx_expenses_date ON expenses(date);
            CREATE INDEX idx_expenses_budget ON expenses(budget_id);
            CREATE INDEX idx_transfers_date ON transfers(date);
            CREATE INDEX idx_budgets_active ON budgets(is_active);
        """)
        
        # Начальные данные
        cursor.execute("INSERT OR IGNORE INTO currencies (code, rate) VALUES ('RUB', 1.0)")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('theme', 'Light')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('auto_backup', 'weekly')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('db_version', '3')")
        
        conn.commit()
        conn.close()
    
    elif current_version < DB_VERSION:
        conn = get_db_connection()
        if current_version < 2:
            migrate_v1_to_v2(conn)
        if current_version < 3:
            migrate_v2_to_v3(conn)
        set_db_version(DB_VERSION)
        conn.close()

def get_setting(key, default=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else default

def set_setting(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()