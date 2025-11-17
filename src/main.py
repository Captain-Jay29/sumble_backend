import os
import psycopg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_connection():
    """Create and return a database connection."""
    return psycopg.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        dbname=os.getenv('POSTGRES_DB', 'sumble_db'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'postgres')
    )


def test_connection():
    """Test database connection."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT NOW()')
        result = cursor.fetchone()
        print('✅ Database connected successfully!')
        print(f'Current time: {result[0]}')
        cursor.close()
        conn.close()
    except Exception as e:
        print(f'❌ Database connection error: {e}')
        exit(1)


if __name__ == '__main__':
    print('🚀 Starting application...')
    test_connection()
    print('✨ Application ready!')

