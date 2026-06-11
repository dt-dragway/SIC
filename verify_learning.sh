#!/bin/bash
# Script to verify AI Learning Loop integration
# 1. Login
# 2. Reset Wallet
# 3. Buy BTC
# 4. Sell BTC (triggers learning)
# 5. Check AI Memory file

BASE_URL="http://localhost:8001/api/v1"
EMAIL="admin@sic.com"
PASS="Admin123!"

echo "1. Logging in..."
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASS" | jq -r .access_token)

echo "Token obtained (first 10 chars): ${TOKEN:0:10}..."

echo "2. Resetting Wallet..."
curl -s -X POST "$BASE_URL/practice/reset" \
  -H "Authorization: Bearer $TOKEN" | jq .

echo "3. Buying BTC..."
curl -s -X POST "$BASE_URL/practice/order" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "quantity": 0.001
  }' | jq .order

echo "Wait 2 seconds..."
sleep 2

echo "4. Selling BTC (Triggering Learning)..."
curl -s -X POST "$BASE_URL/practice/order" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "SELL",
    "type": "MARKET",
    "quantity": 0.001
  }' | jq .order

echo "5. Verifying AI Memory File..."
cat /DATA/Desarrollos\ \ /SIC/backend/app/ml/agent_memory.json | jq .total_trades
