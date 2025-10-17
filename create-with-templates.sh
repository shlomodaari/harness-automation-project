#!/bin/bash

##############################################################################
# Harness Automation with Org-Level Templates
# Creates reusable templates at org level, then projects that use them
##############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Harness Template-Based Project Creator           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Check arguments
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 <config-file.yaml> [--create-templates]"
    echo ""
    echo -e "${YELLOW}Flags:${NC}"
    echo "  --create-templates    Create org-level templates (do once)"
    echo ""
    echo -e "${YELLOW}Example:${NC}"
    echo "  # First time: Create templates at org level"
    echo "  $0 test-run-config.yaml --create-templates"
    echo ""
    echo "  # Subsequent projects: Use existing templates"
    echo "  $0 test-run-config.yaml"
    exit 1
fi

CONFIG_FILE="$1"
CREATE_TEMPLATES=""

if [ "$2" == "--create-templates" ]; then
    CREATE_TEMPLATES="--create-templates"
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}✗ Config file not found: $CONFIG_FILE${NC}"
    exit 1
fi

# Extract info
PROJECT_NAME=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['project']['repo_name'])" 2>/dev/null || echo "Unknown")
ORG_ID=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['harness']['org_id'])" 2>/dev/null || echo "default")

echo -e "${GREEN}Configuration:${NC} $CONFIG_FILE"
echo -e "${GREEN}Organization:${NC} $ORG_ID"
echo -e "${GREEN}Project:${NC} $PROJECT_NAME"
echo ""

if [ -n "$CREATE_TEMPLATES" ]; then
    echo -e "${YELLOW}⚠️  CREATE TEMPLATES MODE${NC}"
    echo ""
    echo "This will create TWO org-level templates:"
    echo "  • nonprod_deployment_pipeline (org.$ORG_ID)"
    echo "  • prod_deployment_pipeline (org.$ORG_ID)"
    echo ""
    echo "These templates can be reused across ALL projects!"
    echo ""
    echo -e "${RED}Only do this ONCE per organization!${NC}"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
else
    echo -e "${YELLOW}This will create:${NC}"
    echo "  • Project: $PROJECT_NAME"
    echo "  • 2 Pipelines (referencing org-level templates)"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Starting Template-Based Creation...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
echo ""

# Run the script
python3 scripts/create_with_templates.py \
    --config-file "$CONFIG_FILE" \
    $CREATE_TEMPLATES

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✓ SUCCESS!                            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [ -n "$CREATE_TEMPLATES" ]; then
        echo -e "${GREEN}Org-Level Templates Created:${NC}"
        echo "  ✓ nonprod_deployment_pipeline"
        echo "  ✓ prod_deployment_pipeline"
        echo ""
        echo -e "${YELLOW}Next Steps:${NC}"
        echo "  1. Go to Harness: https://app.harness.io"
        echo "  2. Organization → Templates"
        echo "  3. See your 2 pipeline templates"
        echo ""
        echo -e "${YELLOW}Now create projects using these templates:${NC}"
        echo "  $0 $CONFIG_FILE"
        echo "  (without --create-templates flag)"
    else
        echo -e "${GREEN}Project Created:${NC}"
        echo "  ✓ Project: $PROJECT_NAME"
        echo "  ✓ 2 Pipelines (from org templates)"
        echo ""
        echo -e "${YELLOW}Next Steps:${NC}"
        echo "  1. Login to Harness: https://app.harness.io"
        echo "  2. Go to Projects → $PROJECT_NAME"
        echo "  3. Go to Pipelines"
        echo "  4. Notice: Pipelines show 'Template' badge!"
        echo "  5. Update the org template → all pipelines update!"
    fi
else
    echo -e "${RED}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║              ✗ FAILED                              ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Check the logs above for errors."
fi

exit $EXIT_CODE
