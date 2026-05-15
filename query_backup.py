import mysql.connector
from mysql.connector import Error
import os



vm_name = os.getenv("vm_name")
def run_query():
    try:
        # Connect to the MySQL database using hardcoded credentials
        connection = mysql.connector.connect(
            host='db-prd-ace02.broadcom.net',
            user='cohesity_rusr',
            password='C0hesity_rusr',
            database='cohesity'
        )

        if connection.is_connected():
            print("Connected to MySQL database")

            # buffered cursor prevents "Unread result found"
            cursor = connection.cursor(dictionary=True, buffered=True)
            query = "SELECT * FROM backup_status WHERE hostname=%s"
            cursor.execute(query, (vm_name,))

            result = cursor.fetchall()
            print("Query Result:")
            if result:
                for row in result:
                    print(row)
            else:
                print("No rows found for hostname:", vm_name)

    except Error as e:
        print("Error while connecting to MySQL:", e)

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    run_query()
