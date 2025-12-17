# Quick MySQL Setup Guide

## 🚀 Quick Start

### Step 1: Install MySQL (if not installed)

**macOS:**
```bash
brew install mysql
brew services start mysql
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql
```

### Step 2: Create Database and User

**Option A: Use the setup script (Easiest)**
```bash
./setup_mysql.sh
```

**Option B: Manual setup**
```bash
mysql -u root -p
```

Then run:
```sql
CREATE DATABASE learningmaster CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bloguser'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON learningmaster.* TO 'bloguser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Set Environment Variable

**For current session:**
```bash
export DATABASE_URL="mysql+pymysql://bloguser:your_password@localhost:3306/learningmaster"
```

**For permanent setup (add to ~/.zshrc or ~/.bashrc):**
```bash
echo 'export DATABASE_URL="mysql+pymysql://bloguser:your_password@localhost:3306/learningmaster"' >> ~/.zshrc
source ~/.zshrc
```

### Step 4: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run Your App

```bash
python app.py
```

## ⚠️ Important: Password with Special Characters

If your MySQL password contains special characters, you need to **URL encode** them:

| Character | Encoded |
|-----------|---------|
| `@` | `%40` |
| `#` | `%23` |
| `$` | `%24` |
| `%` | `%25` |
| `&` | `%26` |
| `+` | `%2B` |
| `=` | `%3D` |
| `?` | `%3F` |
| `/` | `%2F` |
| `:` | `%3A` |
| ` ` (space) | `%20` |

**Example:**
- Password: `my@pass#123`
- Encoded: `my%40pass%23123`
- Connection string: `mysql+pymysql://bloguser:my%40pass%23123@localhost:3306/learningmaster`

**Or use Python to encode:**
```python
from urllib.parse import quote_plus
password = "my@pass#123"
encoded = quote_plus(password)
print(encoded)  # my%40pass%23123
```

## 🔍 Verify Connection

Test your connection:
```bash
python -c "from app import app, db; app.app_context().push(); from app import Post; print(f'Connected! Posts: {Post.query.count()}')"
```

## 🐛 Troubleshooting

### Error: "Can't connect to MySQL server"
- Check MySQL is running: `brew services list` (macOS) or `sudo systemctl status mysql` (Linux)
- Verify username, password, and database name
- Check if password needs URL encoding

### Error: "Access denied"
- Verify user has privileges: `GRANT ALL PRIVILEGES ON learningmaster.* TO 'bloguser'@'localhost';`
- Check password is correct

### Error: "Unknown database"
- Create the database: `CREATE DATABASE learningmaster;`

## 📝 Connection String Format

```
mysql+pymysql://username:password@host:port/database_name
```

**Examples:**
- Local: `mysql+pymysql://bloguser:password@localhost:3306/learningmaster`
- Remote: `mysql+pymysql://bloguser:password@192.168.1.100:3306/learningmaster`
- With special chars: `mysql+pymysql://bloguser:my%40pass@localhost:3306/learningmaster`

## 🔐 Security Tips

1. **Don't commit passwords to git** - Use environment variables
2. **Use strong passwords** - Mix of letters, numbers, and symbols
3. **Limit user privileges** - Only grant necessary permissions
4. **Use .env file** (optional) - See below

## 📄 Using .env File (Optional)

Create a `.env` file in your project root:

```bash
# .env
DATABASE_URL=mysql+pymysql://bloguser:password@localhost:3306/learningmaster
SECRET_KEY=your-secret-key-here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And add to `app.py` (at the top):
```python
from dotenv import load_dotenv
load_dotenv()
```

**Note:** Make sure `.env` is in your `.gitignore` file!

---

**Need more help?** See `MYSQL_SETUP.md` for detailed instructions.

