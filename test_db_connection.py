#!/usr/bin/env python3
"""
Test MySQL database connection
Run: python test_db_connection.py
"""
import os
import sys
from urllib.parse import urlparse, quote

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_connection_string():
    """Test and validate the DATABASE_URL connection string"""
    DATABASE_URL = os.environ.get('DATABASE_URL', None)
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL environment variable is not set!")
        print("\nSet it with:")
        print("  export DATABASE_URL='mysql+pymysql://user:password@localhost:3306/database'")
        print("\nOr create a .env file with:")
        print("  DATABASE_URL=mysql+pymysql://user:password@localhost:3306/database")
        return False
    
    print(f"📋 DATABASE_URL: {DATABASE_URL}")
    print()
    
    if not DATABASE_URL.startswith('mysql+pymysql://'):
        print("❌ Connection string must start with 'mysql+pymysql://'")
        return False
    
    try:
        # Parse the URL
        parsed = urlparse(DATABASE_URL)
        
        print("🔍 Parsed components:")
        print(f"   Scheme: {parsed.scheme}")
        print(f"   Netloc: {parsed.netloc}")
        print(f"   Path: {parsed.path}")
        print()
        
        # Extract username and password
        if '@' not in parsed.netloc:
            print("❌ Invalid format: Missing '@' separator")
            print("   Expected: mysql+pymysql://username:password@host:port/database")
            return False
        
        auth_and_host = parsed.netloc
        auth_part, host_part = auth_and_host.rsplit('@', 1)
        
        if ':' not in auth_part:
            print("❌ Invalid format: Missing ':' separator in username:password")
            print("   Expected: mysql+pymysql://username:password@host:port/database")
            return False
        
        user, password = auth_part.split(':', 1)
        
        print("✅ Connection string format is valid!")
        print(f"   Username: {user}")
        print(f"   Password: {'*' * len(password)} ({len(password)} characters)")
        print(f"   Host: {host_part.split(':')[0] if ':' in host_part else host_part}")
        print(f"   Port: {host_part.split(':')[1] if ':' in host_part else '3306 (default)'}")
        print(f"   Database: {parsed.path.lstrip('/')}")
        print()
        
        # Test actual connection
        print("🔌 Testing connection...")
        try:
            import pymysql
            from urllib.parse import quote
            
            # Build connection parameters
            host = host_part.split(':')[0] if ':' in host_part else host_part
            port = int(host_part.split(':')[1]) if ':' in host_part else 3306
            database = parsed.path.lstrip('/')
            
            # URL encode password
            encoded_password = quote(password, safe='')
            
            connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,  # Use original password, not encoded
                database=database,
                connect_timeout=5
            )
            
            print("✅ Successfully connected to MySQL!")
            
            # Test query
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"   MySQL Version: {version[0]}")
            
            connection.close()
            return True
            
        except ImportError:
            print("⚠️  PyMySQL not installed. Install with: pip install PyMySQL")
            return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\nTroubleshooting:")
            print("  1. Check MySQL is running")
            print("  2. Verify username and password")
            print("  3. Check database exists")
            print("  4. Verify host and port are correct")
            return False
            
    except Exception as e:
        print(f"❌ Error parsing connection string: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("MySQL Connection String Tester")
    print("=" * 60)
    print()
    
    success = test_connection_string()
    
    print()
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed. Please fix the issues above.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

