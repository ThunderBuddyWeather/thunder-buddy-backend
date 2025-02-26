#!/bin/bash
# Test script for EC2 deploy action

# Set test variables
export INPUT_HOST="test-host.example.com"
export INPUT_USERNAME="ec2-user"
export INPUT_KEY="dummy-key-for-testing"
export INPUT_DOCKER_USERNAME="dockeruser"
export INPUT_DB_PASSWORD="testpassword"
export INPUT_WEATHERBIT_API_KEY="test-api-key"

# Create test environment
mkdir -p test-env
cd test-env

# Create test files
echo "# Test env file" > .env.ci
echo "DATABASE_URL=postgresql://thunderbuddy:\${DB_PASSWORD}@db:5432/thunderbuddy" >> .env.ci
echo "WEATHERBIT_API_KEY=\${WEATHERBIT_API_KEY}" >> .env.ci

mkdir -p static
touch static/placeholder.txt

# Create a docker-compose.yml file
cat > docker-compose.yml << EOF
services:
  app:
    build: .
    container_name: thunder-buddy
    environment:
      - WEATHERBIT_API_KEY=\${WEATHERBIT_API_KEY}
EOF

# Create a Dockerfile
cat > Dockerfile << EOF
FROM python:3.12-slim
WORKDIR /app
COPY .env.ci .env.ci
EOF

# Create a main.py file
touch main.py

# Create scripts directory
mkdir -p scripts
touch scripts/startup.sh

# Simulate the validation step
echo "Validating deployment inputs..."
if [ -z "$INPUT_HOST" ]; then
  echo "Error: SSH host is empty"
  exit 1
fi
echo "SSH host is set"

# Simulate creating environment file
echo "Creating .env.local from .env.ci template"
cp .env.ci .env.local
sed -i.bak "s/\${DB_PASSWORD}/$INPUT_DB_PASSWORD/g" .env.local
sed -i.bak "s/\${WEATHERBIT_API_KEY}/$INPUT_WEATHERBIT_API_KEY/g" .env.local
cat .env.local

# Simulate copying files
echo "Creating temporary directory for deployment files"
mkdir -p ~/deploy-temp-test
cp docker-compose.yml Dockerfile .env.local ~/deploy-temp-test/
cp -r scripts/ ~/deploy-temp-test/
cp main.py ~/deploy-temp-test/
mkdir -p ~/deploy-temp-test/static
cp -r static/ ~/deploy-temp-test/
cp .env.ci ~/deploy-temp-test/.env.ci

echo "Files that would be copied to EC2:"
ls -la ~/deploy-temp-test/

# Clean up
cd ..
rm -rf ~/deploy-temp-test
echo "Test completed. Check output for errors." 