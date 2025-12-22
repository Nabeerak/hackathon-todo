#!/bin/bash
# Chatbot diagnostic script

echo "=== Chatbot Diagnostic ==="
echo ""

echo "1. Checking .env configuration..."
if grep -q "^OPENAI_API_KEY=sk-" /home/nabeera/hackathon-todo/.env; then
    echo "   ✅ OpenAI API key is configured"
else
    echo "   ❌ OpenAI API key is missing or invalid"
fi

if grep -q "^AI_FEATURES_ENABLED=true" /home/nabeera/hackathon-todo/.env; then
    echo "   ✅ AI features are enabled"
else
    echo "   ⚠️  AI_FEATURES_ENABLED not set (adding it now...)"
    echo "AI_FEATURES_ENABLED=true" >> /home/nabeera/hackathon-todo/.env
    echo "   ✅ Added AI_FEATURES_ENABLED=true to .env"
fi

echo ""
echo "2. Checking backend server..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is responding"
else
    echo "   ❌ Backend is not responding"
    exit 1
fi

echo ""
echo "3. Backend configuration..."
cd /home/nabeera/hackathon-todo/backend
python3 << 'PYEOF'
import sys
sys.path.insert(0, 'src')
from config import settings

print(f"   OpenAI Model: {settings.openai_model}")
print(f"   AI Features: {'Enabled' if settings.ai_features_enabled else 'Disabled'}")
print(f"   API Key Set: {'Yes' if settings.openai_api_key else 'No'}")
print(f"   Rate Limit: {settings.ai_rate_limit_per_day}/day")
PYEOF

echo ""
echo "4. Testing chat endpoint (requires authentication)..."
echo "   Note: This will fail if not logged in - test in browser instead"
echo ""

echo "=== Next Steps ==="
echo "1. If you changed .env, restart the backend:"
echo "   cd backend && uv run uvicorn src.main:app --reload"
echo ""
echo "2. Open browser console (F12) and check for errors"
echo ""
echo "3. Try sending a test message in the chat"
echo ""
echo "4. Check Network tab for failed API requests"
