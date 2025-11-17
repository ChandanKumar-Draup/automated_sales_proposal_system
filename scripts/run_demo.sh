#!/bin/bash
# Automated Sales Proposal System - Demo Runner
# This script makes it easy to run different demo scenarios

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Sales Proposal System - Demo Runner${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if server is running
echo -e "${YELLOW}Checking if API server is running...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API server is running${NC}\n"
else
    echo -e "${RED}❌ API server is not running${NC}"
    echo -e "${YELLOW}Please start the server first:${NC}"
    echo -e "  python main.py\n"
    exit 1
fi

# Check if embeddings are loaded
echo -e "${YELLOW}Checking embeddings...${NC}"
if [ -f "resources/vector_store/index.faiss" ]; then
    echo -e "${GREEN}✅ Vector store found${NC}\n"
else
    echo -e "${RED}❌ Vector store not found${NC}"
    echo -e "${YELLOW}Please run embeddings first:${NC}"
    echo -e "  python scripts/create_embeddings.py\n"
    exit 1
fi

# Create output directory
mkdir -p demo_outputs

# Show menu
echo -e "${BLUE}Available Demo Scenarios:${NC}\n"
echo "  1. Quick Proposal - Technology/SaaS Company"
echo "  2. Quick Proposal - Healthcare Company"
echo "  3. Quick Proposal - Financial Services"
echo "  4. RFP Processing - Basic Technical RFP"
echo "  5. RFP Processing - Complex Healthcare RFP"
echo "  6. Knowledge Base Search"
echo "  7. Client-Specific Content Search"
echo "  8. Run ALL Scenarios"
echo ""

# Get user choice
if [ -z "$1" ]; then
    read -p "Select a scenario (1-8): " choice
else
    choice=$1
fi

# Run selected scenario
case $choice in
    1)
        echo -e "\n${GREEN}Running: Quick Proposal - SaaS${NC}"
        python scripts/demo_workflows.py --scenario quick-saas
        ;;
    2)
        echo -e "\n${GREEN}Running: Quick Proposal - Healthcare${NC}"
        python scripts/demo_workflows.py --scenario quick-healthcare
        ;;
    3)
        echo -e "\n${GREEN}Running: Quick Proposal - Finance${NC}"
        python scripts/demo_workflows.py --scenario quick-finance
        ;;
    4)
        echo -e "\n${GREEN}Running: RFP Processing - Basic${NC}"
        python scripts/demo_workflows.py --scenario rfp-basic
        ;;
    5)
        echo -e "\n${GREEN}Running: RFP Processing - Healthcare${NC}"
        python scripts/demo_workflows.py --scenario rfp-healthcare
        ;;
    6)
        echo -e "\n${GREEN}Running: Knowledge Base Search${NC}"
        python scripts/demo_workflows.py --scenario knowledge-search
        ;;
    7)
        echo -e "\n${GREEN}Running: Client-Specific Search${NC}"
        python scripts/demo_workflows.py --scenario client-search
        ;;
    8)
        echo -e "\n${GREEN}Running: ALL Scenarios${NC}"
        python scripts/demo_workflows.py --scenario all
        ;;
    *)
        echo -e "${RED}Invalid choice. Please select 1-8.${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Demo Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nGenerated proposals can be found in: ${BLUE}demo_outputs/${NC}\n"
