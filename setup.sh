#!/bin/bash

# Jordan E-commerce Store - Automated Setup Script
# This script automates the local development setup process

echo "🇯🇴 Jordan E-commerce Store - Setup Script"
echo "============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    echo "   Download from: https://python.org"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOL
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///ecommerce.db
FLASK_ENV=development
FLASK_DEBUG=True
WHATSAPP_NUMBER=+962791301413
STORE_NAME=متجر الأردن الإلكتروني
ADMIN_EMAIL=admin@yourstore.com
EOL
    echo "✅ .env file created with default values"
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p static/uploads
mkdir -p logs

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Activate virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo ""
echo "2. Start the application:"
echo "   python app.py"
echo ""
echo "3. Open your browser and visit:"
echo "   🌐 Main Website: http://localhost:5000"
echo "   🔐 Admin Panel: http://localhost:5000/admin/login"
echo ""
echo "4. Default admin credentials:"
echo "   👤 Username: admin"
echo "   🔑 Password: admin123"
echo ""
echo "⚠️  Important: Change the admin password after first login!"
echo ""
echo "📖 For deployment instructions, see DEPLOYMENT.md"
echo "📚 For detailed documentation, see README.md"
echo ""
echo "🚀 Happy coding!"

