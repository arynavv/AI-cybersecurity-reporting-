import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

dbname = os.getenv('DB_NAME', 'cybercrime_db')
user = os.getenv('DB_USER', 'postgres')
password = os.getenv('DB_PASSWORD', '')
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', '5432')

try:
    # Connect to default 'postgres' database to create the new db
    con = psycopg2.connect(dbname='postgres', user=user, host=host, password=password, port=port)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    
    # Check if db exists
    cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
    exists = cur.fetchone()
    
    if not exists:
        print(f"Creating database {dbname}...")
        cur.execute(f"CREATE DATABASE {dbname}")
        print("Database created successfully.")
    else:
        print(f"Database {dbname} already exists.")
        
    cur.close()
    con.close()

except Exception as e:
    print(f"Error: {e}")
