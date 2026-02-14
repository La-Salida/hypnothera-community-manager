#!/bin/bash
set -e

echo "🚀 Deploying Hypnothera Community Manager..."

# Create app directory
mkdir -p /opt/hypnothera-community
cd /opt/hypnothera-community

# Clone/update repo
if [ -d .git ]; then
    git pull origin main
else
    git clone https://github.com/La-Salida/hypnothera-community-manager.git .
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install selenium webdriver-manager

# Create .env file template if not exists
if [ ! -f .env ]; then
    cat > .env << 'EOF'
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
PACKETSTREAM_PROXY=your_proxy_url
EOF
    echo "⚠️  Created .env file - please edit with your credentials"
fi

# Install Chrome if not present
if ! command -v google-chrome &> /dev/null; then
    echo "📦 Installing Google Chrome..."
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb
    apt-get update
    apt-get install -y /tmp/chrome.deb || apt-get install -y -f
fi

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Edit /opt/hypnothera-community/.env with your credentials"
echo "2. Run: python3 hypnothera_community_manager.py --dry-run"
echo "3. Test with: python3 hypnothera_community_manager.py"
