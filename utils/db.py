import mysql.connector
import os

COLUMNS = {
    "name": "VARCHAR(255)",
    "search_query": "VARCHAR(255)",
    "url": "VARCHAR(512)",
    "address": "VARCHAR(255)",
    "phone": "VARCHAR(64)",
    "source": "VARCHAR(100)",
}


def get_connection():
    DB_CONFIG = {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", 3306)),
        "user": os.environ.get("DB_USER", "youruser"),
        "password": os.environ.get("DB_PASSWORD", "yourpassword"),
        "database": os.environ.get("DB_NAME", "leads_scraper"),
    }

    return mysql.connector.connect(**DB_CONFIG)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    columns_sql = ",\n".join([f"{col} {typ}" for col, typ in COLUMNS.items()])
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS businesses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            {columns_sql},
            UNIQUE KEY unique_business (name, address)
        )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


def insert_business(business, conn=None, cursor=None):
    close_conn = False
    if conn is None or cursor is None:
        conn = get_connection()
        cursor = conn.cursor()
        close_conn = True
    create_table()
    keys = list(COLUMNS.keys())
    values = [business.get(k) for k in keys]
    placeholders = ", ".join(["%s"] * len(keys))
    columns_sql = ", ".join(keys)
    sql = f"""
        INSERT IGNORE INTO businesses ({columns_sql})
        VALUES ({placeholders})
    """
    cursor.execute(sql, values)
    if close_conn:
        conn.commit()
        cursor.close()
        conn.close()


def get_all_businesses():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM businesses")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
