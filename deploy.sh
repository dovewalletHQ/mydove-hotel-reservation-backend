#!/bin/bash
#
# MyDove Kamal Deployment Helper Script
#
# This script automatically loads environment variables and deploys with Kamal
# Usage: ./deploy.sh [kamal-command]
# Examples:
#   ./deploy.sh deploy      # Deploy application
#   ./deploy.sh setup       # First-time setup
#   ./deploy.sh app logs    # View logs

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== MyDove Kamal Deployment ===${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Please create .env file with all required variables"
    exit 1
fi

# Load environment variables
echo -e "${YELLOW}Loading environment variables from .env...${NC}"
set -a  # automatically export all variables
source .env
set +a

# Verify critical variables
if [ -z "$DOVE_KAMAL_REGISTRY_PASSWORD" ]; then
    echo -e "${RED}ERROR: KAMAL_REGISTRY_PASSWORD is not set!${NC}"
    echo "Please set KAMAL_REGISTRY_PASSWORD in your .env file"
    exit 1
fi

if [ -z "MONGO_DSN" ]; then
    echo -e "${RED}ERROR: DATABASE_URL is not set!${NC}"
    echo "Please set DATABASE_URL in your .env file"
    exit 1
fi

#if [ -z "$JWT_SECRET" ]; then
#    echo -e "${RED}ERROR: JWT_SECRET is not set!${NC}"
#    echo "Please set JWT_SECRET in your .env file"
#    exit 1
#fi

echo -e "${GREEN}✓ Environment loaded successfully${NC}"
echo -e "${GREEN}✓ KAMAL_REGISTRY_PASSWORD: ${KAMAL_REGISTRY_PASSWORD:0:10}...${NC}"
echo -e "${GREEN}✓ DATABASE_URL: ${MONGO_DSN:0:20}...${NC}"
echo ""

# Run kamal with provided arguments (or default to 'deploy')
COMMAND="${@:-deploy}"
echo -e "${YELLOW}Running: kamal $COMMAND${NC}"
echo ""

kamal $COMMAND
