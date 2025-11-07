import mysql.connector
import os
from typing import Dict, Any, Optional


class DatabaseManager:
    """Database manager class for handling MySQL operations with auto table creation."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DatabaseManager.

        Args:
            config: Optional database configuration. If None, uses environment variables.
        """
        if config is None:
            self.config = {
                "host": os.environ.get("DB_HOST", "localhost"),
                "port": int(os.environ.get("DB_PORT", 3306)),
                "user": os.environ.get("DB_USER", "root"),
                "password": os.environ.get("DB_PASSWORD", "yourpassword"),
                "database": os.environ.get("DB_NAME", "leads_db_local"),
            }
        else:
            self.config = config

    def get_connection(self):
        """Get a database connection."""
        return mysql.connector.connect(**self.config)

    def table_exists(self, cursor, table_name: str) -> bool:
        """Check if a table exists in the database."""
        cursor.execute(
            """
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = %s
        """,
            (table_name,),
        )
        return cursor.fetchone()[0] > 0

    def infer_mysql_type(self, value) -> str:
        """Infer MySQL column type from Python value."""
        if value is None:
            return "TEXT"
        elif isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, int):
            return "INT"
        elif isinstance(value, float):
            return "DECIMAL(15,2)"
        elif isinstance(value, str):
            if len(value) <= 255:
                return "VARCHAR(255)"
            else:
                return "TEXT"
        elif isinstance(value, (dict, list)):
            return "JSON"
        else:
            return "TEXT"

    def create_table_from_data(self, cursor, table_name: str, data: dict):
        """Create a table based on the data dictionary structure."""
        columns = []

        columns.append("id INT AUTO_INCREMENT PRIMARY KEY")

        for key, value in data.items():
            column_type = self.infer_mysql_type(value)
            columns.append(f"`{key}` {column_type}")

        columns.append("created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        columns.append(
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        )

        sql = f"CREATE TABLE `{table_name}` ({', '.join(columns)})"
        cursor.execute(sql)

    def store_data(self, table: str, data: dict):
        """Store data in the specified table, creating the table if it doesn't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if not self.table_exists(cursor, table):
                print(f"Table '{table}' does not exist. Creating it...")
                self.create_table_from_data(cursor, table, data)
                print(f"Table '{table}' created successfully.")

            placeholders = ", ".join(["%s"] * len(data))
            columns = ", ".join([f"`{col}`" for col in data.keys()])
            sql = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"

            cursor.execute(sql, list(data.values()))
            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"Error storing data in table '{table}': {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def execute_query(
        self, query: str, params: Optional[tuple] = None, fetch_all: bool = True
    ):
        """Execute a custom query and return results."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(query, params or ())

            if query.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
                return cursor.fetchall() if fetch_all else cursor.fetchone()
            else:
                conn.commit()
                return cursor.rowcount

        except Exception as e:
            conn.rollback()
            print(f"Error executing query: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
