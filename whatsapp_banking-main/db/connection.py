import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

def get_db_connection():
    """Create and return a database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def create_users_table():
    """Create users table if it doesn't exist"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create table with language column and latest_otp
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(15) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            language VARCHAR(50) DEFAULT 'ENGLISH',
            latest_otp VARCHAR(4),
            balance FLOAT DEFAULT 10000.0,
            age INTEGER
        )
    """)
    
    # Insert default user
    cur.execute("""
        INSERT INTO users (phone_number, name, language)
        VALUES ('919035576651', 'Farhan', 'ENGLISH')
        ON CONFLICT (phone_number) DO UPDATE 
        SET language = 'ENGLISH'
    """)
    
    conn.commit()
    cur.close()
    conn.close()
