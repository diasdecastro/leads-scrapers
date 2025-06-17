import mysql.connector
import os

# TODO: Denk darüber nach, ob die DB-Konfiguration eine Klasse sein sollte,

COLUMNS = {
    "name": "VARCHAR(255)",
    "search_query": "VARCHAR(255)",
    "url": "VARCHAR(512)",
    "address": "VARCHAR(255)",
    "phone": "VARCHAR(64)",
    "source": "VARCHAR(100)",
}

ENRICHED_COLUMNS = {
    "company_id": "INT PRIMARY KEY",  # FK to raw_companies.id
    "url": "VARCHAR(512)",
    "mitarbeiter": "INT",
    "umsatz": "DECIMAL(10,2)",
    "bilanzsumme": "DECIMAL(10,2)",
    "rechtsform": "VARCHAR(50)",
    "publikationsdatum": "DATE",
    "sitz": "VARCHAR(100)",
    "branche": "VARCHAR(255)",
    "wz_code": "VARCHAR(20)",
    "geschaeftsfuehrer": "TEXT",
    "eigentuemer": "TEXT",
    "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
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


def create_raw_companies_table():
    conn = get_connection()
    cursor = conn.cursor()
    columns_sql = ",\n".join([f"{col} {typ}" for col, typ in COLUMNS.items()])
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS raw_companies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            {columns_sql},
            UNIQUE KEY unique_business (name, address)
        )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


def insert_raw_company(business, conn=None, cursor=None):
    close_conn = False
    if conn is None or cursor is None:
        conn = get_connection()
        cursor = conn.cursor()
        close_conn = True
    create_raw_companies_table()
    keys = list(COLUMNS.keys())
    values = [business.get(k) for k in keys]
    placeholders = ", ".join(["%s"] * len(keys))
    columns_sql = ", ".join(keys)
    sql = f"""
        INSERT IGNORE INTO raw_companies ({columns_sql})
        VALUES ({placeholders})
    """
    cursor.execute(sql, values)
    if close_conn:
        conn.commit()
        cursor.close()
        conn.close()


def get_all_raw_companies():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM raw_companies")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def create_enriched_companies_table():
    conn = get_connection()
    cursor = conn.cursor()
    columns_sql = ",\n".join([f"{col} {typ}" for col, typ in ENRICHED_COLUMNS.items()])
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS enriched_companies (
            {columns_sql},
            CONSTRAINT fk_enriched_company FOREIGN KEY (company_id)
                REFERENCES raw_companies(id)
                ON DELETE CASCADE
        )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()


def insert_enriched_company(enrichment, conn=None, cursor=None):
    close_conn = False
    if conn is None or cursor is None:
        conn = get_connection()
        cursor = conn.cursor()
        close_conn = True

    create_enriched_companies_table()

    keys = list(ENRICHED_COLUMNS.keys())
    # Remove TIMESTAMP-Felder (werden automatisch gesetzt)
    keys = [
        k
        for k in keys
        if not k.startswith("created_at") and not k.startswith("updated_at")
    ]
    values = [enrichment.get(k) for k in keys]
    placeholders = ", ".join(["%s"] * len(keys))
    columns_sql = ", ".join(keys)

    sql = f"""
        INSERT INTO enriched_companies ({columns_sql})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE
            {", ".join([f"{k}=VALUES({k})" for k in keys if k != "company_id"])}
    """
    cursor.execute(sql, values)
    if close_conn:
        conn.commit()
        cursor.close()
        conn.close()


def get_company_name_by_id(company_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM raw_companies WHERE id = %s", (company_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    return None


def get_company_id_by_name(company_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM raw_companies WHERE name = %s", (company_name,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    return None


def get_all_company_names():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM raw_companies")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id": row[0], "name": row[1]} for row in results]
