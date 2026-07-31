import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('DB_HOST', '127.0.0.1')
port = int(os.getenv('DB_PORT', '3306'))
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', '')
db_name = os.getenv('DB_NAME', 'ai_sdr_db')

print(f"Connecting to MySQL server at {host}:{port} as user '{user}'...")

try:
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        charset='utf8mb4'
    )
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"Database '{db_name}' ensured successfully!")
    connection.close()
except Exception as e:
    print(f"MySQL Connection Warning/Info: {e}")
