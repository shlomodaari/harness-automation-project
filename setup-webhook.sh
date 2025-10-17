#!/bin/bash

set -e

echo "🚀 Setting up Harness Automation Webhook Handler"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Jenkins Configuration
JENKINS_URL=http://jenkins:8080
JENKINS_USER=admin
JENKINS_TOKEN=your_jenkins_api_token
JENKINS_JOB=harness-automation

# Webhook Secrets
GITHUB_SECRET=your_github_webhook_secret
GITLAB_TOKEN=your_gitlab_token

# Harness Configuration
HARNESS_ACCOUNT_ID=your_harness_account_id
HARNESS_API_KEY=your_harness_api_key
HARNESS_ORG=default

# Logging
LOG_LEVEL=INFO
EOL
    echo "✅ Created .env file. Please edit with your actual credentials."
    echo ""
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create logs directory
mkdir -p webhook-logs

echo "Building webhook handler Docker image..."
docker build -t harness-webhook -f Dockerfile.webhook .

echo ""
echo "🔄 Starting webhook handler..."

# Check which docker compose command is available
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.webhook.yml up -d
else
    docker compose -f docker-compose.webhook.yml up -d
fi

echo ""
echo "✅ Webhook handler is running!"
echo ""
echo "📝 Next Steps:"
echo "1. Configure GitHub webhook: http://your-server:5000/webhook/github"
echo "2. Configure GitLab webhook: http://your-server:5000/webhook/gitlab"
echo ""
echo "📋 To view logs:"
echo "docker logs $(docker ps -qf \"name=harness-automation_webhook-handler\")"
echo ""
echo "🛑 To stop the webhook handler:"
echo "docker-compose -f docker-compose.webhook.yml down"
echo ""
