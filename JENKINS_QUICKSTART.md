# Jenkins Integration - Quick Start Guide

This guide provides a quick way to set up Jenkins integration with the Harness Automation project.

## 📋 Option 1: Simple Jenkins Job (15-30 minutes)

### Step 1: Create Jenkins Pipeline Job

1. Go to Jenkins → New Item
2. Enter name: `harness-automation`
3. Select: Pipeline
4. Click: OK
5. Configure:
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: Your Git repository URL
   - **Branch**: `main` (or your branch)
   - **Script Path**: `Jenkinsfile`
6. Click: Save

### Step 2: Set Up Credentials (Optional, but recommended)

1. Go to: Jenkins → Manage Jenkins → Manage Credentials
2. Add credentials for Harness:
   - **Kind**: Secret text
   - **Scope**: Global
   - **Secret**: Your Harness API key
   - **ID**: `harness-api-key`
   - **Description**: Harness API Key

3. Similarly, add credential for `harness-account-id`

### Step 3: Run Your First Job

1. Go to your `harness-automation` job
2. Click: Build with Parameters
3. Enter the required information:
   ```
   ACTION: create-project
   PROJECT_NAME: jenkins-demo-1
   HARNESS_ACCOUNT_ID: your-account-id
   HARNESS_API_KEY: your-api-key
   ```
4. Click: Build

## 📋 Option 2: Webhook Integration (1-2 hours)

### Step 1: Deploy Webhook Handler

```bash
# Build the Docker image
docker build -t harness-webhook -f Dockerfile.webhook .

# Run the container
docker run -d -p 5000:5000 \
  -e JENKINS_URL=http://jenkins:8080 \
  -e JENKINS_USER=your_jenkins_user \
  -e JENKINS_TOKEN=your_jenkins_token \
  -e JENKINS_JOB=harness-automation \
  harness-webhook
```

### Step 2: Configure GitHub Webhook

1. Go to your GitHub repository
2. Settings → Webhooks → Add webhook
3. Set:
   - **Payload URL**: `http://your-server:5000/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: Create a secret and use the same in webhook-config.yaml
   - **Events**: Repository events
4. Click: Add webhook

### Step 3: Test the Integration

Create a new repository in GitHub and watch the webhook trigger the Jenkins job automatically!

## 🔧 Troubleshooting

### Jenkins Job Fails

Check:
- Correct Harness API key and Account ID
- Network connectivity to Harness API
- Correct template references in config

### Webhook Not Triggering

Check:
- Webhook handler logs: `docker logs harness-webhook`
- Jenkins URL and credentials
- GitHub/GitLab webhook configuration
- Network connectivity and firewall rules

## 🎯 Configuration Reference

### Jenkins Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `ACTION` | Action to perform | `create-project`, `create-templates`, `dry-run` |
| `PROJECT_NAME` | Name of project to create | `my-awesome-project` |
| `HARNESS_ACCOUNT_ID` | Harness account ID | `H18sdO-ETQS9O3oO9Ksu0A` |
| `HARNESS_API_KEY` | Harness API key | `pat.H18sdO-ETQS9O3oO9Ksu0A.68f28f3c...` |
| `DEVELOPER_EMAILS` | Comma-separated developer emails | `dev1@company.com,dev2@company.com` |
| `APPROVER_EMAILS` | Comma-separated approver emails | `manager@company.com` |
| `CREATE_RBAC` | Whether to create RBAC | `true` or `false` |
| `TEMPLATE_REF` | Pipeline template reference | `mytemplate` |
| `TEMPLATE_VERSION` | Pipeline template version | `v1` |

For more detailed instructions, see [JENKINS_SETUP_GUIDE.md](JENKINS_SETUP_GUIDE.md).
