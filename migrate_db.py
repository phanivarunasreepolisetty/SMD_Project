import sqlite3
import os
import sys

# Use absolute path to be sure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'medicine_dispenser.db')

def add_column(cursor, table, col_name, col_type, default_val):
    try:
        # Check columns
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        if col_name not in columns:
            print(f"Adding '{col_name}'...", flush=True)
            sql = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type} DEFAULT '{default_val}'"
            cursor.execute(sql)
            print("Done.", flush=True)
        else:
            print(f"'{col_name}' exists.", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

def main():
    print(f"Checking DB at: {DB_PATH}", flush=True)
    
    if not os.path.exists(DB_PATH):
        print("DB not found!", flush=True)
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    add_column(cursor, 'medicines', 'morning_time', 'TIME', '08:00:00')
    add_column(cursor, 'medicines', 'afternoon_time', 'TIME', '13:00:00')
    add_column(cursor, 'medicines', 'evening_time', 'TIME', '18:00:00')
    add_column(cursor, 'medicines', 'night_time', 'TIME', '21:00:00')

    conn.commit()
    conn.close()
    print("Migration finished.", flush=True)

if __name__ == "__main__":
    main()
