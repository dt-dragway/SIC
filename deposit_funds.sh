#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"
EMAIL="admin@sic.com"
PASS="y2k38*"

# 1. Login
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASS" | jq -r .access_token)

echo "Token: ${TOKEN:0:10}..."

# 2. Deposit All Cryptos ($5 each)
echo "Depositing $5 in major cryptos..."
curl -s -X POST "$BASE_URL/practice/deposit-all-cryptos" \
  -H "Authorization: Bearer $TOKEN" | jq .
