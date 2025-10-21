# 📚 Configuration Examples

This directory contains comprehensive examples for all supported Harness resources.

---

## 📁 Example Files

| File | Description | Resources | Complexity |
|------|-------------|-----------|------------|
| `basic-project.yaml` | Simple project setup | 1 | ⭐ Beginner |
| `connectors-all-types.yaml` | All 8 connector types | 15 | ⭐⭐ Intermediate |
| `secrets.yaml` | Secret management | 13 | ⭐⭐ Intermediate |
| `rbac-access-control.yaml` | User groups & service accounts | 7 | ⭐⭐ Intermediate |
| `complete-deployment.yaml` | Full deployment pipeline | 15 | ⭐⭐⭐ Advanced |
| `COMPLETE_EXAMPLE.yaml` | Everything in one file | 48 | ⭐⭐⭐⭐ Expert |

---

## 🚀 Quick Start

### 1. Basic Project (Beginner)

Start here if you're new:

```bash
python3 scripts/create_resources.py --config examples/basic-project.yaml
```

**Creates:**
- 1 Project with tags

**Perfect for:** First-time users

---

### 2. Connectors (Intermediate)

Learn all connector types:

```bash
python3 scripts/create_resources.py --config examples/connectors-all-types.yaml
```

**Creates:**
- 2 Kubernetes connectors
- 2 AWS connectors
- 1 GCP connector
- 1 Azure connector
- 3 Source control connectors (GitHub, GitLab, Bitbucket)
- 3 Docker registries

**Perfect for:** Setting up integrations

---

### 3. Secrets (Intermediate)

Learn secret management:

```bash
python3 scripts/create_resources.py --config examples/secrets.yaml
```

**Creates:**
- 6 text secrets (tokens, passwords, API keys)
- 3 file secrets (SSH keys, certificates)

**Perfect for:** Understanding credential management

**Important:** Shows how to use different secret managers (Harness, Vault, AWS SM, etc.)

---

### 4. RBAC (Intermediate)

Learn access control:

```bash
python3 scripts/create_resources.py --config examples/rbac-access-control.yaml
```

**Creates:**
- 4 user groups (Platform, Dev, Ops, QA)
- 4 service accounts (CI, CD, Monitoring, Terraform)

**Perfect for:** Team and automation setup

---

### 5. Complete Deployment (Advanced)

Full application deployment:

```bash
python3 scripts/create_resources.py --config examples/complete-deployment.yaml
```

**Creates:**
- 3 environments (Dev, Staging, Prod)
- 3 infrastructures (K8s clusters)
- 2 services (Backend, Frontend)
- 3 pipelines (Dev, Staging, Prod deployments)

**Perfect for:** Real-world deployments

---

### 6. Complete Example (Expert)

Everything at once:

```bash
python3 scripts/create_resources.py --config examples/COMPLETE_EXAMPLE.yaml
```

**Creates:** 48 resources total
- 1 Project
- 13 Connectors
- 13 Secrets
- 6 RBAC resources
- 3 Environments
- 4 Infrastructures
- 4 Services
- 4 Pipelines

**Perfect for:** Comprehensive testing

---

## 📋 Configuration Reference

### Required Section

```yaml
harness:
  account_id: "YOUR_ACCOUNT_ID"  # Get from Harness UI
  api_key: "YOUR_API_KEY"        # Create in Account Settings
  org_id: "default"              # Usually "default"

project:
  repo_name: "my_project"        # Lowercase, underscores
  description: "My project"      # Description
```

### Optional Sections

All other sections are optional:

```yaml
# Connectors
connectors:
  kubernetes: []
  aws: []
  gcp: []
  azure: []
  github: []
  gitlab: []
  bitbucket: []
  docker: []

# Secrets
secrets:
  text_secrets: []
  file_secrets: []

# RBAC
access_control:
  user_groups: []
  service_accounts: []

# CD Resources
environments: []
infrastructures: []
services: []

# Pipelines
pipelines: {}
```

---

## 🎛️ Configuration Options

### Connectors

#### Kubernetes
```yaml
kubernetes:
  - name: "Cluster Name"
    identifier: "cluster_id"
    credential_type: "InheritFromDelegate"  # or ManualConfig
    delegate_selectors: ["delegate1"]
    tags:
      environment: "prod"
```

#### AWS
```yaml
aws:
  - name: "AWS Account"
    identifier: "aws_id"
    credential_type: "InheritFromDelegate"  # or ManualConfig
    # If ManualConfig:
    access_key_ref: "aws_access_key"
    secret_key_ref: "aws_secret_key"
    delegate_selectors: ["aws-delegate"]
```

#### GitHub
```yaml
github:
  - name: "GitHub Org"
    identifier: "github_id"
    url: "https://github.com/myorg"
    validation_repo: "myorg/repo"
    authentication:
      type: "Http"
      spec_type: "UsernameToken"
      username: "git"
      token_ref: "github_token"
    api_access:
      type: "Token"
      token_ref: "github_token"
```

#### Docker
```yaml
docker:
  - name: "Docker Hub"
    identifier: "dockerhub"
    registry_url: "https://index.docker.io/v2/"
    auth_type: "UsernamePassword"  # or Anonymous
    username: "myusername"
    password_ref: "docker_password"
```

### Secrets

#### Text Secret
```yaml
text_secrets:
  - name: "API Token"
    identifier: "api_token"
    value_type: "Inline"              # or Reference
    value: "<+input>"                 # or actual value
    secret_manager_identifier: "harnessSecretManager"  # or custom
    tags:
      type: "token"
```

**Secret Manager Options:**
- `harnessSecretManager` - Built-in (default)
- `my_vault` - HashiCorp Vault
- `aws_secrets_manager` - AWS Secrets Manager
- `azure_key_vault` - Azure Key Vault
- `gcp_secret_manager` - GCP Secret Manager

#### File Secret
```yaml
file_secrets:
  - name: "SSH Key"
    identifier: "ssh_key"
    secret_manager_identifier: "harnessSecretManager"
    tags:
      type: "ssh"
```

### RBAC

#### User Group
```yaml
user_groups:
  - name: "Team Name"
    identifier: "team_id"
    description: "Team description"
    users:
      - user1@company.com
      - user2@company.com
    tags:
      team: "platform"
```

#### Service Account
```yaml
service_accounts:
  - name: "CI Account"
    identifier: "ci_account"
    email: "ci@harness.serviceaccount"
    create_token: false  # true to auto-generate API token
    tags:
      purpose: "ci"
```

### Environments

```yaml
environments:
  - name: "Production"
    identifier: "prod"
    type: "Production"  # or PreProduction
    tags:
      env: "prod"
    variables:
      - name: "LOG_LEVEL"
        value: "WARN"
        type: "String"
```

### Infrastructures

```yaml
infrastructures:
  - name: "Prod K8s"
    identifier: "prod_k8s"
    environment_ref: "prod"
    type: "KubernetesDirect"
    deployment_type: "Kubernetes"
    config:
      connector_ref: "k8s_connector"  # or <+input>
      namespace: "production"
      release_name: "myapp"
      allow_simultaneous: false
```

### Services

```yaml
services:
  - name: "Backend"
    identifier: "backend"
    type: "Kubernetes"
    config:
      manifests:
        - identifier: "manifests"
          type: "K8sManifest"
          connector_ref: "github"
          git_details:
            branch: "main"
            paths: ["k8s/"]
      artifacts:
        - identifier: "image"
          type: "DockerRegistry"
          connector_ref: "dockerhub"
          image_path: "myorg/backend"
```

### Pipelines

```yaml
pipelines:
  deployment:
    name: "Deploy Pipeline"
    identifier: "deploy"
    template_ref: "template_id"
    version: "v1"
    tags:
      type: "deployment"
```

---

## 🔧 Customization Guide

### 1. Replace Credentials

```yaml
harness:
  account_id: "YOUR_ACCOUNT_ID"  # ← Replace this
  api_key: "YOUR_API_KEY"        # ← Replace this
  org_id: "default"              # ← Usually stays "default"
```

### 2. Update User Emails

```yaml
access_control:
  user_groups:
    - name: "My Team"
      users:
        - actual.user@company.com  # ← Real email addresses
```

### 3. Configure Connectors

Update connector details:
- URLs for GitHub/GitLab/Bitbucket
- Delegate selectors
- Secret references

### 4. Adjust Resources

Modify environments, namespaces, and deployment settings to match your infrastructure.

---

## 🎯 Common Patterns

### Pattern 1: Multi-Environment Setup

```yaml
environments:
  - name: "Dev"
    identifier: "dev"
    type: "PreProduction"
  - name: "Staging"
    identifier: "staging"
    type: "PreProduction"
  - name: "Prod"
    identifier: "prod"
    type: "Production"
```

### Pattern 2: Shared Secrets

```yaml
secrets:
  text_secrets:
    - name: "GitHub Token"
      identifier: "github_token"
      ...

connectors:
  github:
    - name: "GitHub"
      authentication:
        token_ref: "github_token"  # ← References secret
```

### Pattern 3: Runtime Input

```yaml
services:
  - name: "My Service"
    config:
      manifests:
        - connector_ref: "<+input>"  # ← Prompt at runtime
```

---

## 🚨 Important Notes

### Security

- **Never commit real API keys** to version control
- Use environment variables for sensitive data
- Rotate API keys regularly

### Prerequisites

- Harness account with API access
- Valid API key (Account Settings → API Keys)
- Users must exist before adding to groups
- Delegates must be running for connectors
- Templates must exist for pipelines

### Limitations

- File secrets require manual file upload after creation
- Custom roles not supported (use Harness UI)
- Resource groups not supported (use Harness UI)

---

## 🧪 Testing Your Configuration

### Step 1: Dry Run

```bash
python3 scripts/create_resources.py --config your-config.yaml --dry-run
```

Validates configuration without creating resources.

### Step 2: Minimal Test

Start with just a project:

```yaml
harness:
  account_id: "YOUR_ACCOUNT_ID"
  api_key: "YOUR_API_KEY"
  org_id: "default"

project:
  repo_name: "test_project"
  description: "Test project"
```

### Step 3: Add Resources Gradually

Add one resource type at a time to debug issues.

---

## 📊 Resource Dependencies

```
Project (required)
  ├── Connectors (optional)
  │   └── Used by: Services, Infrastructures
  ├── Secrets (optional)
  │   └── Used by: Connectors
  ├── User Groups (optional)
  ├── Service Accounts (optional)
  ├── Environments (optional)
  │   └── Used by: Infrastructures
  ├── Infrastructures (optional)
  │   └── Requires: Environment, Connector
  ├── Services (optional)
  │   └── Requires: Connectors (for manifests/artifacts)
  └── Pipelines (optional)
      └── Requires: Template to exist
```

---

## 💡 Tips & Tricks

### Tip 1: Use Consistent Naming

```yaml
name: "Production Kubernetes"    # Human-readable
identifier: "prod_k8s"          # Machine-readable (lowercase, underscores)
```

### Tip 2: Tag Everything

```yaml
tags:
  environment: "prod"
  team: "platform"
  managed_by: "automation"
```

### Tip 3: Start Small

Begin with `basic-project.yaml` and add complexity gradually.

### Tip 4: Use Runtime Input

```yaml
connector_ref: "<+input>"  # Prompt user at deployment time
```

### Tip 5: Reuse Configurations

Copy and modify examples rather than starting from scratch.

---

## 🔗 Related Documentation

- **Main README**: [`../README.md`](../README.md)
- **Scripts Docs**: [`../scripts/README.md`](../scripts/README.md)
- **SDK Docs**: [`../harness_sdk/README.md`](../harness_sdk/README.md)
- **Feature Guide**: [`../ALL_FEATURES_DOCUMENTATION.md`](../ALL_FEATURES_DOCUMENTATION.md)

---

## 🎓 Learning Path

1. **Start**: `basic-project.yaml` - Create your first project
2. **Connectors**: `connectors-all-types.yaml` - Set up integrations
3. **Secrets**: `secrets.yaml` - Manage credentials
4. **RBAC**: `rbac-access-control.yaml` - Configure access
5. **Deploy**: `complete-deployment.yaml` - Full deployment
6. **Everything**: `COMPLETE_EXAMPLE.yaml` - Master all features

---

**Happy Configuring! 🚀**
