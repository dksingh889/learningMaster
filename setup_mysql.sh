#!/bin/bash
# MySQL Setup Script for Learning Master Blog

echo "=========================================="
echo "Learning Master - MySQL Setup"
echo "=========================================="
echo ""

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "❌ MySQL is not installed."
    echo "Install MySQL first:"
    echo "  macOS: brew install mysql"
    echo "  Ubuntu: sudo apt-get install mysql-server"
    exit 1
fi

echo "✅ MySQL is installed"
echo ""

# Get database credentials
read -p "Enter MySQL root password: " -s ROOT_PASSWORD
echo ""
read -p "Enter database name (default: learningmaster): " DB_NAME
DB_NAME=${DB_NAME:-learningmaster}

read -p "Enter database user (default: bloguser): " DB_USER
DB_USER=${DB_USER:-bloguser}

read -p "Enter database password: " -s DB_PASSWORD
echo ""

# Create database and user
echo ""
echo "Creating database and user..."

mysql -u root -p"$ROOT_PASSWORD" <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

if [ $? -eq 0 ]; then
    echo "✅ Database and user created successfully!"
    echo ""
    echo "=========================================="
    echo "Next Steps:"
    echo "=========================================="
    echo ""
    echo "1. Set the DATABASE_URL environment variable:"
    echo ""
    echo "   export DATABASE_URL=\"mysql+pymysql://${DB_USER}:${DB_PASSWORD}@localhost:3306/${DB_NAME}\""
    echo ""
    echo "2. Or add to your ~/.bashrc or ~/.zshrc for permanent setup:"
    echo ""
    echo "   echo 'export DATABASE_URL=\"mysql+pymysql://${DB_USER}:${DB_PASSWORD}@localhost:3306/${DB_NAME}\"' >> ~/.zshrc"
    echo ""
    echo "3. Run your Flask app:"
    echo ""
    echo "   python app.py"
    echo ""
else
    echo "❌ Error creating database. Please check your MySQL root password."
    exit 1
fi

