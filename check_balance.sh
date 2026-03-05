#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"
EMAIL="admin@sic.com"
PASS="y2k38*"

# 1. Login
TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASS" | jq -r .access_token)

# 2. Get Wallet
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/practice/wallet" | jq .balances
