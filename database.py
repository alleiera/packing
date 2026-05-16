import sqlite3
import os

DB_NAME = "packing_list.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            size TEXT,
            meter_per_box REAL
        )
    ''')

    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Packing Lists table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packing_lists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_no TEXT,
            date TEXT,
            consignee_company TEXT,
            consignee_address TEXT,
            consignee_tel TEXT,
            shipper_company TEXT,
            shipper_address TEXT,
            shipper_tel TEXT,
            remarks TEXT,
            incoterms TEXT,
            port_of_loading TEXT,
            place_of_delivery TEXT,
            origin_country TEXT,
            gtip_code TEXT,
            total_boxes_manual INTEGER,
            total_pallets_manual INTEGER
        )
    ''')

    # Packing List Items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packing_list_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            packing_list_id INTEGER,
            product_code TEXT,
            product_name TEXT,
            size TEXT,
            total_meter REAL,
            boxes INTEGER,
            box_weight REAL,
            net_weight REAL,
            gross_weight REAL,
            FOREIGN KEY (packing_list_id) REFERENCES packing_lists (id) ON DELETE CASCADE
        )
    ''')

    # Default settings
    default_settings = [
        ('company_name', 'HSC PLASTİK İNŞAAT ORMAN ÜRÜNLERİ SAN VE TİC.LTD.ŞTİ'),
        ('company_address', 'ULUS MAH 136 SK NO 10 KOYUNDERE MENEMEN İZMİR'),
        ('company_tel', '0 232 833 42 98'),
        ('logo_path', ''),
        ('empty_box_weight', '0.5'),
        ('empty_pallet_weight', '15.0'),
        ('language', 'tr')
    ]

    for key, value in default_settings:
        cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
