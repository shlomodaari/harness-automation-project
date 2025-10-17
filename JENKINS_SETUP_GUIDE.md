# 🔧 Jenkins Integration Setup Guide

Complete guide to integrate Jenkins with Harness automation for automated project creation.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Setup (Simple)](#quick-setup-simple)
- [Advanced Setup (Webhook-Based)](#advanced-setup-webhook-based)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Two integration options available:

### **Option 1: Simple Jenkins Job** (Recommended)
- ⏱️ **Setup Time**: 15-30 minutes
- 🎯 **Use Case**: Manual project creation via Jenkins UI
- ✅ **Pros**: Simple, easy to test, no external services
- ❌ **Cons**: Manual trigger required

### **Option 2: Webhook-Based Automation** (Advanced)
- ⏱️ **Setup Time**: 1-2 hours
- 🎯 **Use Case**: Auto-create Harness project when new repo created
- ✅ **Pros**: Fully automated, no manual intervention
- ❌ **Cons**: Requires webhook handler service, more complex

---

## 📦 Prerequisites

### Required:
- ✅ Jenkins installed and running
- ✅ Python 3.7+ installed on Jenkins agent
- ✅ Git plugin installed in Jenkins
- ✅ Harness account with API key
- ✅ Access to this repository

### Optional (for webhooks):
- ✅ Public endpoint for webhook handler
- ✅ GitHub/GitLab webhook access

---

## 🚀 Quick Setup (Simple)

### Step 1: Create Jenkins Job

1. **Login to Jenkins**: http://your-jenkins-url:8080

2. **Create New Job**:
   - Click "New Item"
   - Name: `harness-automation`
   - Type: **Pipeline**
   - Click OK

3. **Configure Job**:
   
   **General Settings:**
   - ✅ Check "This project is parameterized" (parameters are in Jenkinsfile)
   - Description: "Automated Harness project creation"

   **Pipeline Configuration:**
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/shlomodaari/harness-automation-project.git`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`

4. **Save** the job

### Step 2: Configure Credentials (Secure Method)

**Option A: Jenkins Credentials Store** (Recommended)

1. Go to **Manage Jenkins** → **Manage Credentials**
2. Click **(global)** → **Add Credentials**
3. Add these credentials:
   - **ID**: `harness-account-id`
   - **Kind**: Secret text
   - **Secret**: Your Harness account ID
   
   - **ID**: `harness-api-key`
   - **Kind**: Secret text
   - **Secret**: Your Harness API key

4. Update Jenkinsfile to use credentials:
```groovy
environment {
    HARNESS_ACCOUNT_ID = credentials('harness-account-id')
    HARNESS_API_KEY = credentials('harness-api-key')
}
```

**Option B: Job Parameters** (Simpler, less secure)
- Use the parameters in the Jenkinsfile (already configured)
- Enter credentials when running the job

### Step 3: Test the Job

1. **Go to job**: `harness-automation`
2. **Click**: "Build with Parameters"
3. **Fill in**:
   ```
   ACTION: create-project
   PROJECT_NAME: test-jenkins-project
   PROJECT_DESCRIPTION: Testing Jenkins integration
   HARNESS_ACCOUNT_ID: your_account_id
   HARNESS_API_KEY: your_api_key
   DEVELOPER_EMAILS: dev@example.com
   APPROVER_EMAILS: manager@example.com
   ```
4. **Click**: "Build"
5. **Watch**: Console Output
6. **Verify**: Check Harness UI for new project!

### Step 4: Create Templates (First Time Only)

Before creating projects, create org-level templates once:

1. **Build with Parameters**
2. **Set ACTION**: `create-templates`
3. **Fill in**: Harness credentials
4. **Build**
5. Templates are now available for all projects!

---

## 🔗 Advanced Setup (Webhook-Based)

### Architecture

```
GitHub/GitLab → Webhook → Handler Service → Jenkins → Harness Automation
```

### Step 1: Deploy Webhook Handler

**Option A: Docker (Recommended)**

```bash
# Build Docker image
docker build -t harness-webhook-handler -f Dockerfile.webhook .

# Run container
docker run -d \
  -p 5000:5000 \
  -e JENKINS_URL=http://jenkins:8080 \
  -e JENKINS_USER=admin \
  -e JENKINS_TOKEN=your_jenkins_token \
  -e JENKINS_JOB_NAME=harness-automation \
  -e GITHUB_WEBHOOK_SECRET=your_webhook_secret \
  --name harness-webhook \
  harness-webhook-handler
```

**Option B: Python Virtual Environment**

```bash
# Install dependencies
pip3 install flask requests pyyaml

# Set environment variables
export JENKINS_URL=http://localhost:8080
export JENKINS_USER=admin
export JENKINS_TOKEN=your_jenkins_token
export JENKINS_JOB_NAME=harness-automation
export GITHUB_WEBHOOK_SECRET=your_secret

# Run handler
python3 scripts/jenkins_webhook_handler.py
```

### Step 2: Configure GitHub Webhook

1. **Go to GitHub**: Repository → Settings → Webhooks
2. **Add webhook**:
   - Payload URL: `http://your-server:5000/webhook/github`
   - Content type: `application/json`
   - Secret: `your_webhook_secret`
   - Events: **Repository** (check "Repositories")
3. **Save**

### Step 3: Configure GitLab Webhook

1. **Go to GitLab**: Project → Settings → Webhooks
2. **Add webhook**:
   - URL: `http://your-server:5000/webhook/gitlab`
   - Secret Token: `your_webhook_token`
   - Trigger: **Project events**
3. **Add webhook**

### Step 4: Test Webhook

**Manual Test:**
```bash
curl -X POST http://your-server:5000/webhook/manual \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "test-webhook-project",
    "description": "Testing webhook integration"
  }'
```

**GitHub Test:**
- Create a new repository in GitHub
- Watch webhook handler logs
- Jenkins job should trigger automatically!

---

## 💡 Usage Examples

### Example 1: Create Simple Project

**Via Jenkins UI:**
```
ACTION: create-project
PROJECT_NAME: customer-portal
PROJECT_DESCRIPTION: Customer Portal Application
DEVELOPER_EMAILS: dev1@company.com, dev2@company.com
APPROVER_EMAILS: manager@company.com
NONPROD_TEMPLATE_REF: nonprod_deployment_pipeline
NONPROD_TEMPLATE_VERSION: v1760729233
```

### Example 2: Create Templates

**Via Jenkins UI:**
```
ACTION: create-templates
(Other parameters don't matter for template creation)
```

### Example 3: Dry Run (Test)

**Via Jenkins UI:**
```
ACTION: dry-run
PROJECT_NAME: test-project
(Fill in other params for validation)
```

### Example 4: Custom Template Versions

**Via Jenkins UI:**
```
ACTION: create-project
PROJECT_NAME: legacy-app
NONPROD_TEMPLATE_REF: custom_pipeline
NONPROD_TEMPLATE_VERSION: v1
PROD_TEMPLATE_REF: custom_pipeline_prod
PROD_TEMPLATE_VERSION: v2
```

### Example 5: Webhook Trigger

**Create new GitHub repo** → Automatic Harness project creation!

---

## 🔧 Jenkinsfile Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ACTION` | `create-project` | Action to perform: create-project, create-templates, dry-run |
| `PROJECT_NAME` | `my-new-project` | Project name (lowercase, hyphen-separated) |
| `PROJECT_DESCRIPTION` | `Automated project` | Project description |
| `HARNESS_ACCOUNT_ID` | *(empty)* | Your Harness account ID |
| `HARNESS_API_KEY` | *(empty)* | Your Harness API key (use credentials!) |
| `HARNESS_ORG_ID` | `default` | Harness organization ID |
| `DEVELOPER_EMAILS` | `dev@example.com` | Comma-separated developer emails |
| `APPROVER_EMAILS` | `manager@example.com` | Comma-separated approver emails |
| `OPERATOR_EMAILS` | `ops@example.com` | Comma-separated operator emails |
| `NONPROD_TEMPLATE_REF` | `nonprod_deployment_pipeline` | NonProd template identifier |
| `NONPROD_TEMPLATE_VERSION` | `v1760729233` | NonProd template version |
| `PROD_TEMPLATE_REF` | `prod_deployment_pipeline` | Prod template identifier |
| `PROD_TEMPLATE_VERSION` | `v1760729233` | Prod template version |
| `CREATE_RBAC` | `true` | Create RBAC (user groups) |

---

## 🐛 Troubleshooting

### Issue: Jenkins can't find Python

**Solution:**
```groovy
environment {
    PYTHON_VERSION = '/usr/bin/python3'  // Use full path
}
```

### Issue: Permission denied on scripts

**Solution:**
```bash
# In Jenkins job, before running:
sh "chmod +x scripts/*.py"
```

### Issue: pip packages not found

**Solution:**
```groovy
sh """
    pip3 install --user pyyaml requests
    export PATH=\$PATH:\$HOME/.local/bin
"""
```

### Issue: Webhook handler connection refused

**Checklist:**
- [ ] Handler service is running: `curl http://localhost:5000/health`
- [ ] Firewall allows port 5000
- [ ] Jenkins can reach handler: `curl -v http://handler-host:5000/health`
- [ ] Environment variables set correctly

### Issue: Jenkins job fails with authentication error

**Solution:**
- Verify Harness API key is correct
- Check account ID matches your Harness account
- Ensure API key has proper permissions

### Issue: Templates not found

**Solution:**
1. Run template creation first: `ACTION=create-templates`
2. Verify templates exist: Harness UI → Organization → Templates
3. Check template version in parameters matches created version

---

## 📊 Monitoring & Logs

### Jenkins Logs
- **Console Output**: Click on build → "Console Output"
- **Build History**: View all past runs
- **Artifacts**: Download result JSON files

### Webhook Handler Logs
```bash
# Docker
docker logs -f harness-webhook

# Python
tail -f webhook-handler.log
```

### Harness Logs
- Login to Harness
- Go to Audit Trail for creation events
- Check pipeline execution logs

---

## 🎯 Best Practices

### Security
1. ✅ **Use Jenkins Credentials Store** for API keys
2. ✅ **Enable webhook signature verification**
3. ✅ **Use HTTPS** for webhook handler
4. ✅ **Rotate API keys** regularly
5. ✅ **Limit Jenkins job permissions**

### Operations
1. ✅ **Create templates once** at org level
2. ✅ **Test with dry-run** before actual creation
3. ✅ **Archive artifacts** for troubleshooting
4. ✅ **Monitor Jenkins disk space** (logs can grow)
5. ✅ **Set up notifications** (email/Slack on failure)

### Development
1. ✅ **Use version control** for Jenkinsfile changes
2. ✅ **Test locally first** with Python script
3. ✅ **Document custom parameters**
4. ✅ **Keep templates in sync** across environments

---

## 📚 Additional Resources

- **Jenkins Pipeline Syntax**: https://jenkins.io/doc/book/pipeline/syntax/
- **Harness API Docs**: https://apidocs.harness.io/
- **GitHub Webhooks**: https://docs.github.com/en/webhooks
- **GitLab Webhooks**: https://docs.gitlab.com/ee/user/project/integrations/webhooks.html

---

## ✅ Quick Checklist

**Before First Run:**
- [ ] Jenkins installed and running
- [ ] Python 3.7+ on Jenkins agent
- [ ] Repository cloned/accessible
- [ ] Harness account ID obtained
- [ ] Harness API key created
- [ ] Jenkins job created
- [ ] Jenkinsfile in repository

**For Template Creation:**
- [ ] Run once: `ACTION=create-templates`
- [ ] Verify in Harness: Organization → Templates
- [ ] Note template versions for future use

**For Project Creation:**
- [ ] Templates exist (see above)
- [ ] Project name unique
- [ ] User emails valid
- [ ] Template versions correct
- [ ] Run job
- [ ] Verify in Harness UI

**For Webhook Integration:**
- [ ] Webhook handler deployed
- [ ] Environment variables set
- [ ] Webhooks configured in GitHub/GitLab
- [ ] Test with manual trigger
- [ ] Monitor logs

---

## 🎉 Success!

Once set up, you can:
- ✅ Create Harness projects from Jenkins UI (1 click!)
- ✅ Auto-create projects when repos are created (webhooks)
- ✅ Manage templates centrally
- ✅ Scale to unlimited projects

**Enjoy automated Harness project creation!** 🚀
