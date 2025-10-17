#!/bin/bash

##############################################################################
# Complete Harness Project Creator
# Creates EVERYTHING: Project, Service, Environments, Pipelines, User Groups
# Uses org-level templates (specify in config file)
##############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Complete Harness Project Creator              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 <config-file.yaml>"
    echo ""
    echo -e "${YELLOW}Example:${NC}"
    echo "  $0 my-project-config.yaml"
    echo ""
    echo -e "${YELLOW}What it creates:${NC}"
    echo "  ✓ Project"
    echo "  ✓ Service (Kubernetes)"
    echo "  ✓ Environments (staging, production)"
    echo "  ✓ Infrastructures"
    echo "  ✓ Pipelines (from org templates)"
    echo "  ✓ User Groups"
    exit 1
fi

CONFIG_FILE="$1"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}✗ Config file not found: $CONFIG_FILE${NC}"
    exit 1
fi

# Extract info
PROJECT_NAME=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['project']['repo_name'])" 2>/dev/null || echo "Unknown")
NONPROD_TEMPLATE=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE')).get('templates', {}).get('nonprod', {}).get('template_ref', 'N/A'))" 2>/dev/null || echo "N/A")
NONPROD_VERSION=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE')).get('templates', {}).get('nonprod', {}).get('version', 'v1'))" 2>/dev/null || echo "v1")

echo -e "${GREEN}Configuration:${NC} $CONFIG_FILE"
echo -e "${GREEN}Project:${NC} $PROJECT_NAME"
echo -e "${GREEN}NonProd Template:${NC} $NONPROD_TEMPLATE (version $NONPROD_VERSION)"
echo ""

echo -e "${YELLOW}This will create:${NC}"
echo "  • Project: $PROJECT_NAME"
echo "  • Service: ${PROJECT_NAME}_service"
echo "  • Environments: staging, production"
echo "  • Infrastructures: 2"
echo "  • Pipelines: 2 (using org-level templates)"
echo "  • User Groups: 3"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Creating Complete Project...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
echo ""

# Run the script
python3 scripts/create_complete_project.py --config-file "$CONFIG_FILE"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✓ SUCCESS!                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Complete Project Created:${NC}"
    echo "  ✓ Project: $PROJECT_NAME"
    echo "  ✓ Service, Environments, Infrastructures"
    echo "  ✓ Pipelines (from org templates)"
    echo "  ✓ User Groups"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Login to Harness: https://app.harness.io"
    echo "  2. Go to Projects → $PROJECT_NAME"
    echo "  3. Check Pipelines - see Template badges!"
    echo "  4. Run a pipeline to test"
else
    echo -e "${RED}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ✗ FAILED                              ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════╝${NC}"
fi

exit $EXIT_CODE
