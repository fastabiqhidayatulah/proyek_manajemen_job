#!/bin/bash

# ============================================================================
# SETUP NGROK - AUTO GUIDE
# ============================================================================
# File ini menunjukkan langkah-langkah setup Ngrok untuk MacOS/Linux
# Untuk Windows: Lihat setup_ngrok.ps1 atau NGROK_SETUP_GUIDE.md

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         NGROK SETUP GUIDE - MacOS/Linux                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if ngrok installed
if ! command -v ngrok &> /dev/null
then
    echo "❌ ERROR: Ngrok tidak ditemukan!"
    echo ""
    echo "Solusi:"
    echo "1. Brew: brew install ngrok"
    echo "2. Atau download dari: https://ngrok.com/download"
    echo ""
    exit 1
fi

echo "✅ Ngrok found!"
echo ""
echo "▶️  Starting Ngrok..."
ngrok http 4321 &
NGROK_PID=$!

echo "⏳ Waiting 5 seconds..."
sleep 5

# Get URL from API
echo ""
echo "📡 Getting Ngrok public URL..."

NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | cut -d'"' -f4 | head -1)

if [ -z "$NGROK_URL" ]; then
    echo "⚠️  Auto-detection failed. Please manually copy URL from Ngrok output."
    echo ""
    read -p "Enter Ngrok URL (https://...): " NGROK_URL
fi

echo ""
echo "✅ URL: $NGROK_URL"
echo ""

# Set environment variable
echo "🔧 Setting DJANGO_PUBLIC_URL..."
export DJANGO_PUBLIC_URL="$NGROK_URL"
echo "export DJANGO_PUBLIC_URL='$NGROK_URL'" >> ~/.bash_profile

echo "✅ Done!"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  NEXT STEPS                                                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "1. Open new terminal (keep Ngrok running)"
echo "   cd /path/to/proyek_management_job"
echo "   python manage.py runserver 0.0.0.0:4321"
echo ""
echo "2. Test: Open browser"
echo "   $NGROK_URL"
echo ""
echo "✅ Setup complete!"
echo ""
