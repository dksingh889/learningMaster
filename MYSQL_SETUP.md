# MySQL Database Setup Guide

This guide will help you configure your Learning Master blog to use MySQL instead of SQLite.

## 📋 Prerequisites

1. **MySQL Server** installed and running
2. **Python 3.7+** installed
3. **Virtual environment** activated

## 🔧 Step 1: Install MySQL Server

### macOS
```bash
# Using Homebrew
brew install mysql
brew services start mysql
```

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

### Windows
Download and install from: https://dev.mysql.com/downloads/mysql/

## 🔧 Step 2: Create MySQL Database

1. **Login to MySQL**:
   ```bash
   mysql -u root -p
   ```

2. **Create database and user**:
   ```sql
   -- Create database
   CREATE DATABASE learningmaster CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   -- Create user (replace 'your_password' with a strong password)
   CREATE USER 'bloguser'@'localhost' IDENTIFIED BY 'your_password';
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON learningmaster.* TO 'bloguser'@'localhost';
   FLUSH PRIVILEGES;
   
   -- Exit MySQL
   EXIT;
   ```

## 🔧 Step 3: Install Python Dependencies

Install the MySQL driver for Python:

```bash
# Make sure you're in your virtual environment
source myenv/bin/activate  # On macOS/Linux
# or
myenv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

This will install `PyMySQL` which is the MySQL driver we're using.

## 🔧 Step 4: Configure Database Connection

You have **two options** to configure the MySQL connection:

### Option A: Environment Variable (Recommended)

Set the `DATABASE_URL` environment variable:

**macOS/Linux:**
```bash
export DATABASE_URL="mysql+pymysql://bloguser:your_password@localhost:3306/learningmaster"
```

**Windows (Command Prompt):**
```cmd
set DATABASE_URL=mysql+pymysql://bloguser:your_password@localhost:3306/learningmaster
```

**Windows (PowerShell):**
```powershell
$env:DATABASE_URL="mysql+pymysql://bloguser:your_password@localhost:3306/learningmaster"
```

**For permanent setup**, add to your `.env` file or shell profile:
- macOS/Linux: `~/.bashrc` or `~/.zshrc`
- Windows: System Environment Variables

### Option B: Direct Configuration in app.py

Edit `app.py` and change the default database URL:

```python
# Change this line in app.py:
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://bloguser:your_password@localhost:3306/learningmaster'
```

**⚠️ Warning:** Don't commit passwords to version control! Use environment variables instead.

## 🔧 Step 5: Database Connection String Format

The MySQL connection string format is:
```
mysql+pymysql://username:password@host:port/database_name
```

**Examples:**

- **Local MySQL:**
  ```
  mysql+pymysql://bloguser:password@localhost:3306/learningmaster
  ```

- **Remote MySQL:**
  ```
  mysql+pymysql://bloguser:password@192.168.1.100:3306/learningmaster
  ```

- **With SSL (Production):**
  ```
  mysql+pymysql://bloguser:password@host:3306/learningmaster?ssl_ca=/path/to/ca.pem
  ```

## 🔧 Step 6: Create Tables

Run your Flask app to create the database tables:

```bash
python app.py
```

The first time you run it, SQLAlchemy will automatically create all tables.

Or manually create tables:
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## 🔧 Step 7: Import Existing Posts (If Any)

If you have existing posts in SQLite, you can:

1. **Export from SQLite** (optional - if you want to migrate data)
2. **Re-import from JSON**:
   ```bash
   python import_posts.py
   ```

## ✅ Verify Connection

Test the connection:

```bash
python -c "from app import app, db; app.app_context().push(); from app import Post; print(f'Posts: {Post.query.count()}')"
```

## 🔍 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pymysql'"
**Solution:** Install PyMySQL:
```bash
pip install PyMySQL
```

### Error: "Access denied for user"
**Solution:** 
- Check username and password
- Verify user has privileges: `GRANT ALL PRIVILEGES ON learningmaster.* TO 'bloguser'@'localhost';`

### Error: "Can't connect to MySQL server"
**Solution:**
- Check MySQL is running: `sudo systemctl status mysql` (Linux) or `brew services list` (macOS)
- Verify host and port (default is localhost:3306)
- Check firewall settings

### Error: "Unknown database"
**Solution:**
- Create the database: `CREATE DATABASE learningmaster;`

### Character Encoding Issues
**Solution:**
- Make sure database uses utf8mb4:
  ```sql
  ALTER DATABASE learningmaster CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```

## 🔐 Security Best Practices

1. **Use Strong Passwords**: Don't use default or weak passwords
2. **Limit User Privileges**: Only grant necessary permissions
3. **Use Environment Variables**: Never hardcode passwords in code
4. **Enable SSL in Production**: Use SSL connections for remote databases
5. **Regular Backups**: Set up automated database backups

## 📊 Database Management

### View Tables
```sql
USE learningmaster;
SHOW TABLES;
```

### View Posts
```sql
SELECT id, title, slug, author, published_date FROM post LIMIT 10;
```

### Backup Database
```bash
mysqldump -u bloguser -p learningmaster > backup.sql
```

### Restore Database
```bash
mysql -u bloguser -p learningmaster < backup.sql
```

## 🚀 Production Deployment

For production:

1. **Use Environment Variables**:
   ```bash
   export DATABASE_URL="mysql+pymysql://user:pass@host:3306/dbname"
   ```

2. **Enable Connection Pooling** (already configured in app.py):
   - `pool_recycle`: Recycles connections after 1 hour
   - `pool_pre_ping`: Checks connections before using

3. **Use SSL**:
   ```
   mysql+pymysql://user:pass@host:3306/dbname?ssl_ca=/path/to/ca.pem
   ```

4. **Set up Backups**: Regular automated backups

## 📝 Connection String Examples

### Local Development
```
mysql+pymysql://bloguser:password@localhost:3306/learningmaster
```

### Remote Server
```
mysql+pymysql://bloguser:password@db.example.com:3306/learningmaster
```

### With SSL
```
mysql+pymysql://bloguser:password@db.example.com:3306/learningmaster?ssl_ca=/path/to/ca.pem&ssl_cert=/path/to/cert.pem&ssl_key=/path/to/key.pem
```

### Cloud Databases (AWS RDS, etc.)
```
mysql+pymysql://username:password@your-rds-endpoint.region.rds.amazonaws.com:3306/learningmaster
```

---

**Your blog is now ready to use MySQL!** 🎉

If you encounter any issues, check the troubleshooting section above or review the MySQL error logs.

