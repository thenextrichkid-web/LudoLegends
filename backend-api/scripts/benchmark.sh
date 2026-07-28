#!/bin/bash
# Performance benchmark script for Ludo Legends API
# Usage: ./benchmark.sh [users] [duration]

USERS=${1:-100}
DURATION=${2:-30}
BASE_URL="http://35.193.127.84:8000"

echo "=========================================="
echo "  Ludo Legends API Performance Benchmark"
echo "=========================================="
echo "Target:     $BASE_URL"
echo "Users:      $USERS"
echo "Duration:   ${DURATION}s"
echo ""

if ! command -v ab &> /dev/null; then
    echo "Installing Apache Bench..."
    apt-get update -qq && apt-get install -y -qq apache2-utils > /dev/null 2>&1
fi

echo "--- [1/5] Health Endpoint (no auth) ---"
ab -n $((USERS * 10)) -c $USERS -q "$BASE_URL/health"
echo ""

echo "--- [2/5] Feature Flags Public (auth required) ---"
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/otp/request" -H "Content-Type: application/json" -d '{"phone":"+910000000000"}' > /dev/null && curl -s -X POST "$BASE_URL/api/auth/otp/verify" -H "Content-Type: application/json" -d '{"phone":"+910000000000","otp":"123456"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "ERROR: Could not get auth token"
    exit 1
fi

ab -n $((USERS * 5)) -c $USERS -q -H "Authorization: Bearer $TOKEN" "$BASE_URL/api/admin/feature-flags/public"
echo ""

echo "--- [3/5] OpenAPI Docs ---"
ab -n $((USERS * 10)) -c $USERS -q "$BASE_URL/docs"
echo ""

echo "--- [4/5] Concurrent OTP Requests ($USERS users) ---"
ab -n $((USERS * 3)) -c $USERS -q -p /dev/null -T "application/json" \
    -d '{"phone":"+919999999999"}' "$BASE_URL/api/auth/otp/request"
echo ""

echo "--- [5/5] Readiness Check ---"
ab -n $((USERS * 2)) -c $USERS -q "$BASE_URL/ready"
echo ""

echo "=========================================="
echo "  Benchmark Complete"
echo "=========================================="
