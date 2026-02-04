#!/bin/bash
set -euo pipefail

SONAR_URL="${SONAR_HOST_URL:-http://sonarqube:9000}"
SONAR_ADMIN_USER="${SONAR_ADMIN_USER:-admin}"
SONAR_ADMIN_PASSWORD="${SONAR_ADMIN_PASSWORD:-admin}"
SONAR_NEW_PASSWORD="${SONAR_NEW_PASSWORD:-@dmin@123!}"
SONAR_PROJECT_KEY="${SONAR_PROJECT_KEY:-demo-multilang}"
SONAR_TOKEN_NAME="${SONAR_TOKEN_NAME:-demo-token}"

echo "=== SonarQube Init Script ==="
echo "Waiting for SonarQube to be ready..."

# Đợi SonarQube sẵn sàng (tối đa 2 phút)
max_attempts=120
attempt=0
while [ $attempt -lt $max_attempts ]; do
  if curl -fsSL -u "$SONAR_ADMIN_USER:$SONAR_ADMIN_PASSWORD" "$SONAR_URL/api/system/status" > /dev/null 2>&1; then
    echo "SonarQube is ready!"
    break
  fi
  attempt=$((attempt + 1))
  echo "Waiting for SonarQube... ($attempt/$max_attempts)"
  sleep 1
done

if [ $attempt -eq $max_attempts ]; then
  echo "ERROR: SonarQube did not become ready in time."
  exit 1
fi

# Đổi password admin từ mặc định sang password mới
echo "Changing admin password..."
curl -fsSL -X POST \
  -u "$SONAR_ADMIN_USER:$SONAR_ADMIN_PASSWORD" \
  "$SONAR_URL/api/users/change_password" \
  -d "login=$SONAR_ADMIN_USER" \
  -d "password=$SONAR_NEW_PASSWORD" \
  -d "previousPassword=$SONAR_ADMIN_PASSWORD" \
  || echo "Password change may have already been done or failed (non-critical)."

# Tạo project nếu chưa tồn tại
echo "Creating project $SONAR_PROJECT_KEY if not exists..."
curl -fsSL -X POST \
  -u "$SONAR_ADMIN_USER:$SONAR_NEW_PASSWORD" \
  "$SONAR_URL/api/projects/create" \
  -d "project=$SONAR_PROJECT_KEY" \
  -d "name=Demo Multi-language Project" \
  || echo "Project may already exist (non-critical)."

# Tạo token cho project
echo "Creating token $SONAR_TOKEN_NAME for project $SONAR_PROJECT_KEY..."
TOKEN_RESPONSE=$(curl -fsSL -X POST \
  -u "$SONAR_ADMIN_USER:$SONAR_NEW_PASSWORD" \
  "$SONAR_URL/api/user_tokens/generate" \
  -d "name=$SONAR_TOKEN_NAME" \
  -d "type=PROJECT_ANALYSIS_TOKEN" \
  -d "projectKey=$SONAR_PROJECT_KEY" \
  2>/dev/null || echo "")

if [ -n "$TOKEN_RESPONSE" ]; then
  TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4 || echo "")
  if [ -n "$TOKEN" ]; then
    echo "=== SonarQube Token Created ==="
    echo "Token: $TOKEN"
    echo "$TOKEN" > /workspace/sonar_token.txt
    echo "Token saved to /workspace/sonar_token.txt"
  else
    echo "WARNING: Could not extract token from response."
  fi
else
  echo "WARNING: Token creation may have failed (token may already exist)."
fi

echo "=== SonarQube Init Complete ==="
echo "Admin user: $SONAR_ADMIN_USER"
echo "Admin password: $SONAR_NEW_PASSWORD"
echo "Project key: $SONAR_PROJECT_KEY"
