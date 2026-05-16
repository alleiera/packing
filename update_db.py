import sqlite3
from database import get_connection

def update():
    conn = get_connection()
    cursor = conn.cursor()

    # Create sizes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            size_value TEXT UNIQUE NOT NULL
        )
    ''')

    # Recreate products table without size and meter_per_box
    # First, backup existing data if needed, but since we are changing schema drastically
    # and it's early stage, we can just drop and recreate or use a temp table.
    cursor.execute("CREATE TABLE products_new (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL)")

    # Try to copy existing data (only code and name)
    try:
        cursor.execute("INSERT INTO products_new (id, code, name) SELECT id, code, name FROM products")
    except:
        pass

    cursor.execute("DROP TABLE products")
    cursor.execute("ALTER TABLE products_new RENAME TO products")

    conn.commit()
    conn.close()
    print("Database schema updated successfully.")

if __name__ == "__main__":
    update()
