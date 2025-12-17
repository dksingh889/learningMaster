#!/bin/bash
# AWS EC2 Deployment Script for Learning Master
# Usage: Run this script on your EC2 instance

set -e

echo "🚀 Deploying Learning Master to AWS EC2..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed. Please log out and log back in, then run this script again."
    exit 0
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
fi

# Create project directory
PROJECT_DIR="$HOME/learningmaster"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📁 Creating project directory..."
    mkdir -p "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
MYSQL_USER=bloguser
MYSQL_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/" | cut -c1-16)
MYSQL_DATABASE=learningmaster
DATABASE_URL=mysql+pymysql://bloguser:\${MYSQL_PASSWORD}@localhost:3306/learningmaster
EOF
    echo "✅ .env file created. Please update DATABASE_URL with your MySQL credentials."
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Pull latest code (if using git)
if [ -d .git ]; then
    echo "📥 Pulling latest code..."
    git pull || echo "⚠️  Git pull failed or not a git repository"
fi

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose up -d --build

# Wait for containers to start
echo "⏳ Waiting for services to start..."
sleep 5

# Check container status
if docker ps | grep -q learningmaster-web; then
    echo "✅ Application is running!"
    echo ""
    echo "📋 Container status:"
    docker-compose ps
    echo ""
    echo "📋 Application logs (last 20 lines):"
    docker-compose logs --tail=20 web
    echo ""
    echo "✅ Deployment completed!"
    echo ""
    echo "🌐 Your application should be available at:"
    echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5000"
    echo ""
    echo "📝 Useful commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop: docker-compose down"
    echo "   Restart: docker-compose restart"
else
    echo "❌ Container failed to start. Check logs:"
    docker-compose logs web
    exit 1
fi

