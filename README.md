# 🚀 Harness Automation - Complete Project Setup

Automated creation of complete Harness CD projects with pipelines, services, environments, and RBAC using org-level pipeline templates.

[![Harness](https://img.shields.io/badge/Harness-CI%2FCD-00AEEF?logo=harness)](https://harness.io)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python)](https://python.org)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Usage](#detailed-usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

This automation solution provides a **complete, production-ready** system for creating Harness projects with all necessary resources:

- **Org-Level Templates**: Create reusable pipeline templates at organization level
- **Complete Projects**: Automated creation of projects with all resources
- **Template-Based Pipelines**: Pipelines reference org templates (update once, affect all)
- **Full RBAC**: User groups with proper access controls
- **One-Command Execution**: Simple configuration file + one command = complete project

### What Gets Created

```
Single Command Creates:
├── Project
├── Service (Kubernetes)
├── Environments (staging, production)
├── Infrastructures (2)
├── Pipelines (2) ← References org-level templates
└── User Groups (3) ← With users assigned
```

---

## ✨ Features

### 1. Org-Level Template Management

- ✅ Create reusable pipeline templates at organization level
- ✅ All projects reference the same templates
- ✅ Update template once → all pipelines update automatically
- ✅ Version control for templates
- ✅ Centralized maintenance

### 2. Complete Project Automation

- ✅ **Project**: Automatically created with proper configuration
- ✅ **Service**: Kubernetes service with artifact and manifest configuration
- ✅ **Environments**: Staging (PreProduction) and Production
- ✅ **Infrastructures**: Kubernetes infrastructures with namespaces
- ✅ **Pipelines**: NonProd and Prod pipelines from chosen templates
- ✅ **User Groups**: Developers, Approvers, Operators with users assigned

### 3. Pipeline Templates

#### NonProd Pipeline Template
```
Stages:
├── Build and Test (CI)
│   ├── Build step
│   ├── Unit Tests
│   └── Docker Build & Push
└── Deploy to Staging (CD)
    ├── Rolling Deployment
    └── Health Check
```

#### Production Pipeline Template
```
Stages:
├── Pre-Production Validation
│   ├── Image validation
│   └── Smoke tests
├── Approval Gate (Conditional)
│   └── Manual Approval
├── Deploy to Production
│   ├── Canary Deployment (1 instance)
│   ├── Canary Health Check
│   ├── Canary Verification (5 min)
│   ├── Rolling Deployment (full)
│   └── Production Health Check
└── Post-Deployment
    └── Update Documentation
```

### 4. Configuration-Driven

- ✅ Everything configurable via YAML
- ✅ Choose which templates to use
- ✅ Specify template versions
- ✅ Configure connectors, users, notifications
- ✅ Feature flags for optional components

---

## 🏗️ Architecture

### Template-Based Approach

```
┌─────────────────────────────────────────┐
│   Organization Level                    │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Template: nonprod_deployment_   │  │
│  │           pipeline               │  │
│  │ Version: v1760729233            │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │ Template: prod_deployment_      │  │
│  │           pipeline               │  │
│  │ Version: v1760729233            │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
              ↓ ↓ ↓ References
┌─────────────────────────────────────────┐
│   Project A                             │
│   ├── nonprod_pipeline ───→ Template   │
│   └── prod_pipeline ───────→ Template   │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│   Project B                             │
│   ├── nonprod_pipeline ───→ Template   │
│   └── prod_pipeline ───────→ Template   │
└─────────────────────────────────────────┘
```

**Benefit**: Update org template → ALL projects get the update!

---

## 📦 Prerequisites

### 1. Harness Account
- Active Harness account with CD module
- Org-level permissions to create templates
- Project creation permissions

### 2. Local Environment
```bash
# Python 3.7+
python3 --version

# Required packages
pip3 install pyyaml requests
```

### 3. Harness API Key
1. Login to Harness: https://app.harness.io
2. Go to **Profile** → **My API Keys**
3. Create new API key with appropriate permissions
4. Copy the key (starts with `pat.`)

### 4. Account Information
- **Account ID**: Found in Account Settings
- **Organization ID**: Usually `default` or your org identifier

---

## 🚀 Quick Start

### Step 1: Clone Repository

```bash
git clone git@github.com:shlomodaari/harness-automation-project.git
cd harness-automation-project
```

### Step 2: Install Dependencies

```bash
pip3 install pyyaml requests
```

### Step 3: Create Org-Level Templates (One-Time Setup)

```bash
# Copy example config
cp example-project-config.yaml my-config.yaml

# Edit with your credentials
nano my-config.yaml
# - Add your account_id
# - Add your api_key
# - Keep org_id as "default"

# Create org-level templates (do this ONCE)
./create-with-templates.sh my-config.yaml --create-templates
```

**Result**: Two reusable templates created at org level!

### Step 4: Create Your First Project

```bash
# Edit config for your project
nano my-config.yaml
# - Change repo_name to your project name
# - Update users lists
# - Adjust template versions if needed

# Create complete project
./create-project.sh my-config.yaml
```

**Result**: Complete project with everything! 🎉

### Step 5: Verify in Harness

1. Login to https://app.harness.io
2. **Organization** → **Templates** → See your templates
3. **Projects** → Your Project → **Pipelines**
4. Click pipeline → See **"Template"** badge! 🏷️

---

## 📖 Detailed Usage

### Creating Org-Level Templates

Templates should be created **once per organization**. All projects will reference these templates.

```bash
./create-with-templates.sh config.yaml --create-templates
```

**What it does:**
1. Reads your pipeline template YAMLs
2. Processes placeholders (`PROJECT_NAME`, etc. → `<+input>`)
3. Creates Harness Template entities at org level
4. Templates are now available to ALL projects

**When to recreate:**
- Updating template logic
- Adding new stages/steps
- Fixing template issues
- Creating new versions

**Version Management:**
- Each creation gets a unique version (timestamp-based)
- Update config files with new version number
- Pipelines can choose which version to use

### Creating Projects

After templates exist, create as many projects as needed:

```bash
./create-project.sh project-config.yaml
```

**What it creates:**
1. **Project**: With proper naming and tags
2. **Service**: Kubernetes service definition
3. **Environments**: staging (PreProduction), production (Production)
4. **Infrastructures**: Kubernetes infra definitions
5. **Pipelines**: References your chosen templates and versions
6. **User Groups**: With users assigned from config

**Each project gets:**
- Its own pipelines (that reference org templates)
- Its own service, environments, infrastructures
- Its own user groups with appropriate permissions

---

## ⚙️ Configuration

### Configuration File Format

```yaml
harness:
  account_id: "YOUR_ACCOUNT_ID"    # Required
  api_key: "YOUR_API_KEY"          # Required
  org_id: "default"                # Required
  base_url: "https://app.harness.io"

project:
  repo_name: "my-project"          # Your project name
  description: "Project description"

connectors:
  cluster_connector: "<+input>"    # Or connector ID
  docker_connector: "<+input>"
  docker_registry_connector: "<+input>"
  docker_registry: "docker.io"
  git_connector: "<+input>"

users:
  developers:                      # Dev team members
    - dev1@company.com
    - dev2@company.com
  approvers:                       # Prod approvers
    - manager@company.com
  operators:                       # Ops team
    - ops@company.com

notifications:
  slack_webhook: "<+input>"
  email_domain: "company.com"

features:
  git_experience: false
  create_rbac: true
  create_pipelines: true

# Template configuration - KEY SECTION!
templates:
  nonprod:
    template_ref: "nonprod_deployment_pipeline"  # Template identifier
    version: "v1760729233"                       # Template version
  prod:
    template_ref: "prod_deployment_pipeline"
    version: "v1760729233"
```

### Configuration Options

| Section | Key | Description | Example |
|---------|-----|-------------|---------|
| `harness` | `account_id` | Harness account ID | `"abc123xyz"` |
| | `api_key` | Harness API key | `"pat.xxx.yyy.zzz"` |
| | `org_id` | Organization identifier | `"default"` |
| `project` | `repo_name` | Project name | `"my-app"` |
| | `description` | Project description | `"My application"` |
| `connectors` | `cluster_connector` | K8s cluster connector | `"<+input>"` or `"my_cluster"` |
| | `docker_registry` | Docker registry URL | `"docker.io"` |
| `users` | `developers` | Developer emails | `["dev@co.com"]` |
| | `approvers` | Approver emails | `["mgr@co.com"]` |
| `templates` | `nonprod.template_ref` | NonProd template ID | `"nonprod_deployment_pipeline"` |
| | `nonprod.version` | Template version | `"v1760729233"` |

---

## 📁 Project Structure

```
harness-automation/
├── README.md                                # This file
├── create-project.sh                        # ⭐ Main script - creates complete project
├── create-with-templates.sh                 # Template creation script
├── quick-create.sh                          # Quick wrapper
│
├── scripts/
│   ├── create_complete_project.py           # ⭐ Complete automation (use this!)
│   ├── create_with_templates.py             # Template creation logic
│   ├── harness_setup_automation.py          # Original standalone approach
│   └── local_test.sh                        # Local testing wrapper
│
├── templates/
│   ├── pipeline-template-nonprod.yaml       # ⭐ NonProd pipeline template
│   ├── pipeline-template-prod.yaml          # ⭐ Prod pipeline template
│   └── rbac-template.yaml                   # RBAC configuration
│
├── example-project-config.yaml              # ⭐ Example configuration
├── test-run-config.yaml                     # Test configuration
│
└── docs/
    ├── START_HERE.md                        # Quick start guide
    ├── TEMPLATE_APPROACH_GUIDE.md           # Template approach details
    ├── RUN_PIPELINE_GUIDE.md                # Pipeline execution guide
    ├── GIT_EXPERIENCE_GUIDE.md              # Git Experience setup
    ├── SOLUTION_SUMMARY.md                  # Complete solution overview
    ├── TEST_RESULTS.md                      # Test results
    └── CHANGES_LOG.md                       # Change history
```

### Key Files

| File | Purpose |
|------|---------|
| `create-project.sh` | Main entry point - creates everything |
| `scripts/create_complete_project.py` | Core automation logic |
| `templates/pipeline-template-*.yaml` | Pipeline template definitions |
| `example-project-config.yaml` | Configuration template |

---

## 💡 Examples

### Example 1: Standard Project Setup

```yaml
# my-app-config.yaml
harness:
  account_id: "abc123"
  api_key: "pat.abc.123.xyz"
  org_id: "default"

project:
  repo_name: "customer-portal"
  description: "Customer Portal Application"

users:
  developers:
    - john@company.com
    - jane@company.com
  approvers:
    - manager@company.com

templates:
  nonprod:
    template_ref: "nonprod_deployment_pipeline"
    version: "v1760729233"
  prod:
    template_ref: "prod_deployment_pipeline"
    version: "v1760729233"
```

```bash
./create-project.sh my-app-config.yaml
```

### Example 2: Multiple Projects (Same Templates)

```bash
# Project A
./create-project.sh project-a-config.yaml

# Project B  
./create-project.sh project-b-config.yaml

# Project C
./create-project.sh project-c-config.yaml

# All use the same org-level templates!
```

### Example 3: Using Different Template Versions

```yaml
# Use older stable version for production
templates:
  nonprod:
    version: "v1760729233"  # Latest
  prod:
    version: "v1760728000"  # Older stable version
```

### Example 4: Custom Connectors

```yaml
connectors:
  cluster_connector: "prod_k8s_cluster"  # Specific connector
  docker_registry_connector: "dockerhub_connector"
  docker_registry: "myregistry.company.com"
```

---

## 🔧 Troubleshooting

### Issue: "Template already exists"

**Solution**: Templates are being recreated. Either:
- Use existing templates (don't use `--create-templates` flag)
- Script will auto-increment version (timestamp-based)

### Issue: "Template not found"

**Cause**: Pipeline references a template/version that doesn't exist

**Solution**:
1. Check org templates: Organization → Templates
2. Update config with correct `template_ref` and `version`
3. Or create templates: `./create-with-templates.sh config.yaml --create-templates`

### Issue: "Project already exists"

**Solution**: Change `project.repo_name` in config to a unique value

### Issue: "Invalid credentials"

**Checklist**:
- [ ] Account ID correct? (Check Account Settings)
- [ ] API key valid? (Check Profile → My API Keys)
- [ ] API key has permissions? (Need project creation rights)
- [ ] Org ID correct? (Usually `default`)

### Issue: "Connector not found"

**Solution**:
- Use `"<+input>"` for runtime selection
- Or create connector first in Harness UI
- Or specify existing connector ID

### Issue: "Pipeline fails to run"

**Common causes**:
1. **Connectors not configured**: Use `<+input>` and provide at runtime
2. **Service/Environment mismatch**: Check if service references exist
3. **Infrastructure missing**: Ensure infrastructures are created

### Issue: "User groups empty"

**Cause**: Users in config don't exist in Harness

**Solution**:
- Users must exist in Harness first
- Or add users manually after creation
- Or use empty lists and add later

---

## 🎓 Best Practices

### Template Management

1. **Version Control**: Always use versioned templates
2. **Testing**: Test template changes in a dev org first
3. **Documentation**: Document template changes
4. **Communication**: Notify teams before updating templates

### Project Creation

1. **Naming Convention**: Use consistent project names
2. **User Groups**: Keep user lists updated
3. **Connectors**: Create connectors before projects (or use `<+input>`)
4. **Testing**: Test in non-prod environment first

### Security

1. **API Keys**: Never commit API keys to git
2. **Environment Variables**: Use env vars for sensitive data
3. **Rotate Keys**: Regularly rotate API keys
4. **Least Privilege**: Use minimal required permissions

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the `docs/` directory
- **Harness Docs**: https://developer.harness.io

---

## 🎉 Success!

You now have a complete, production-ready Harness automation system!

**What you can do:**
- ✅ Create unlimited projects with one command
- ✅ All projects use centralized templates
- ✅ Update templates → all pipelines benefit
- ✅ Full RBAC and user management
- ✅ Complete CI/CD automation

**Happy Deploying!** 🚀
