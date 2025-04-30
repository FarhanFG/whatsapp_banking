from psycopg2.extras import RealDictCursor
from .connection import get_db_connection

def get_user_name(phone_number):
    """Get user name from phone number"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Try with the original phone number
    cur.execute("SELECT name FROM users WHERE phone_number = %s", (phone_number,))
    result = cur.fetchone()
    
    if not result and phone_number.startswith('91'):
        # Try without the '91' prefix
        phone_without_91 = phone_number[2:]
        cur.execute("SELECT name FROM users WHERE phone_number = %s", (phone_without_91,))
        result = cur.fetchone()
    
    elif not result and not phone_number.startswith('91'):
        # Try with '91' prefix
        phone_with_91 = '91' + phone_number
        cur.execute("SELECT name FROM users WHERE phone_number = %s", (phone_with_91,))
        result = cur.fetchone()
    
    cur.close()
    conn.close()
    return result['name'] if result else "User"

def get_user_language(phone_number):
    """Get user's language preference from database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Try with original phone number
        cur.execute("SELECT language FROM users WHERE phone_number = %s", (phone_number,))
        result = cur.fetchone()
        
        if not result and phone_number.startswith('91'):
            # Try without '91' prefix
            phone_without_91 = phone_number[2:]
            cur.execute("SELECT language FROM users WHERE phone_number = %s", (phone_without_91,))
            result = cur.fetchone()
        
        elif not result and not phone_number.startswith('91'):
            # Try with '91' prefix
            phone_with_91 = '91' + phone_number
            cur.execute("SELECT language FROM users WHERE phone_number = %s", (phone_with_91,))
            result = cur.fetchone()
        
        return result[0] if result else 'ENGLISH'
    except Exception as e:
        print(f"Error getting user language: {e}")
        return 'ENGLISH'
    finally:
        cur.close()
        conn.close()

def update_user_language(phone_number, new_lang):
    """Update user's language preference"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Try with the original phone number
        cur.execute("UPDATE users SET language = %s WHERE phone_number = %s", (new_lang, phone_number))
        
        if cur.rowcount == 0 and phone_number.startswith('91'):
            # Try without the '91' prefix
            phone_without_91 = phone_number[2:]
            cur.execute("UPDATE users SET language = %s WHERE phone_number = %s", (new_lang, phone_without_91))
            
        elif cur.rowcount == 0 and not phone_number.startswith('91'):
            # Try with '91' prefix
            phone_with_91 = '91' + phone_number
            cur.execute("UPDATE users SET language = %s WHERE phone_number = %s", (new_lang, phone_with_91))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating language: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def get_user_balance(phone_number):
    """Get user's account balance"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT balance FROM users WHERE phone_number = %s", (phone_number,))
        result = cur.fetchone()
        return result[0] if result else None
    finally:
        cur.close()
        conn.close()

def update_user_balance(phone_number, new_balance):
    """Update user's account balance"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("UPDATE users SET balance = %s WHERE phone_number = %s", 
                   (new_balance, phone_number))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating balance: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def store_otp(phone_number, otp):
    """Store OTP for a user"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("UPDATE users SET latest_otp = %s WHERE phone_number = %s", 
                   (otp, phone_number))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error storing OTP: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def verify_otp(phone_number, otp):
    """Verify OTP for a user"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT latest_otp, balance FROM users WHERE phone_number = %s", 
                   (phone_number,))
        result = cur.fetchone()
        
        if result and result[0] == otp:
            return True, result[1]  # OTP valid, return balance
        return False, None
    finally:
        cur.close()
        conn.close()

def get_language_counts():
    """Get counts of users by language preference"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT language, COUNT(*) as count 
            FROM users 
            GROUP BY language 
            ORDER BY count DESC
        """)
        
        results = cur.fetchall()
        return results
    finally:
        cur.close()
        conn.close()

def get_age_group_utilization():
    """Get counts of users by age group"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                CASE 
                    WHEN age BETWEEN 18 AND 30 THEN '18-30'
                    WHEN age BETWEEN 31 AND 40 THEN '31-40'
                    WHEN age BETWEEN 41 AND 50 THEN '41-50'
                    WHEN age BETWEEN 51 AND 60 THEN '51-60'
                    WHEN age > 60 THEN 'above 60'
                    ELSE 'unknown'
                END as age_group,
                COUNT(*) as count
            FROM users
            GROUP BY 
                CASE 
                    WHEN age BETWEEN 18 AND 30 THEN '18-30'
                    WHEN age BETWEEN 31 AND 40 THEN '31-40'
                    WHEN age BETWEEN 41 AND 50 THEN '41-50'
                    WHEN age BETWEEN 51 AND 60 THEN '51-60'
                    WHEN age > 60 THEN 'above 60'
                    ELSE 'unknown'
                END
        """)
        
        results = cur.fetchall()
        return results
    finally:
        cur.close()
        conn.close()
        

def get_table_details(table_name):
    """Get details about a database table"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get column information
        cur.execute("""
            SELECT column_name, data_type, character_maximum_length, 
                   column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cur.fetchall()
        
        # Get row count
        cur.execute(f"SELECT COUNT(*) as row_count FROM {table_name}")
        row_count = cur.fetchone()['row_count']
        
        # Get sample data (first 5 rows)
        cur.execute(f"SELECT * FROM {table_name} LIMIT 5")
        sample_data = cur.fetchall()
        
        # Get primary key information
        cur.execute("""
            SELECT a.attname as column_name
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary
        """, (table_name,))
        
        primary_keys = [row['column_name'] for row in cur.fetchall()]
        
        return {
            "table_name": table_name,
            "row_count": row_count,
            "columns": columns,
            "primary_keys": primary_keys,
            "sample_data": sample_data
        }
    
    except Exception as e:
        print(f"Error getting table details: {e}")
        return {"error": str(e)}
    
    finally:
        cur.close()
        conn.close()


        
