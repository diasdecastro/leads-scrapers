import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "youruser",
    "password": "yourpassword",
    "database": "leads_scraper",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS businesses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            industry VARCHAR(100),
            url VARCHAR(512),
            address VARCHAR(255),
            phone VARCHAR(64),
            UNIQUE KEY unique_business (name, address)
        )
    """
    )
    conn.commit()
    cursor.close()
    conn.close()


def insert_business(business):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT IGNORE INTO businesses (name, industry, url, address, phone)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(
        sql,
        (
            business.get("name"),
            business.get("industry"),
            business.get("url"),
            business.get("address"),
            business.get("phone"),
        ),
    )
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
