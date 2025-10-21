# 🔧 Harness SDK

Core SDK modules for Harness Platform automation.

---

## 📁 Module Overview

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| `client.py` | HTTP client with retry logic | `HarnessClient` |
| `connectors.py` | Connector management (8 types) | `ConnectorManager` |
| `secrets.py` | Secrets management | `SecretsManager` |
| `rbac.py` | User groups & service accounts | `RBACManager` |
| `resources.py` | Environments, infra, services | `ResourceManager` |
| `pipelines.py` | Pipeline management | `PipelineManager` |
| `validators.py` | Configuration validation | `ConfigValidator` |
| `models.py` | Data models | `ResourceResult`, `HarnessConfig` |

---

## 🔌 client.py

### `HarnessClient`

HTTP client with automatic retry logic and error handling.

#### Features
- Automatic retry with exponential backoff
- 3 retry attempts on failure
- Comprehensive error logging
- JSON payload handling

#### Usage

```python
from harness_sdk import HarnessClient, HarnessConfig

config = HarnessConfig(
    account_id="YOUR_ACCOUNT_ID",
    api_key="YOUR_API_KEY",
    org_id="default"
)

client = HarnessClient(config)

# GET request
response = client.get("/ng/api/projects/my_project")

# POST request
payload = {"name": "My Resource"}
response = client.post("/ng/api/resource", payload)
```

#### Methods

- `get(endpoint)` - HTTP GET with retries
- `post(endpoint, payload)` - HTTP POST with retries
- `build_endpoint(path, **params)` - Build URL with query params

---

## 🔌 connectors.py

### `ConnectorManager`

Manages all 8 connector types.

#### Supported Connectors

1. **Kubernetes** (`K8sCluster`)
2. **AWS** (`Aws`)
3. **GCP** (`Gcp`)
4. **Azure** (`Azure`)
5. **GitHub** (`Github`)
6. **GitLab** (`Gitlab`)
7. **Bitbucket** (`Bitbucket`)
8. **Docker Registry** (`DockerRegistry`)

#### Usage

```python
from harness_sdk import ConnectorManager

connector_mgr = ConnectorManager(client, project_id)

# Create Kubernetes connector
config = {
    "name": "My K8s Cluster",
    "identifier": "my_k8s",
    "credential_type": "InheritFromDelegate",
    "delegate_selectors": ["primary"]
}
result = connector_mgr.create_kubernetes_connector(config)
```

#### Configuration Options

**Kubernetes:**
- `credential_type`: "InheritFromDelegate" or "ManualConfig"
- `delegate_selectors`: List of delegate names
- `tags`: Key-value pairs

**AWS:**
- `credential_type`: "InheritFromDelegate" or "ManualConfig"
- `access_key_ref`: Secret reference (if ManualConfig)
- `secret_key_ref`: Secret reference (if ManualConfig)
- `delegate_selectors`: List of delegates

**GitHub/GitLab/Bitbucket:**
- `url`: Repository URL
- `validation_repo`: Repo for connectivity test
- `authentication`: Auth configuration
- `api_access`: API token configuration
- `execute_on_delegate`: true/false

**Docker:**
- `registry_url`: Registry URL
- `auth_type`: "UsernamePassword" or "Anonymous"
- `username`: Docker username
- `password_ref`: Secret reference

---

## 🔐 secrets.py

### `SecretsManager`

Manages text and file secrets.

#### Secret Types

1. **Text Secrets** - Passwords, tokens, API keys
2. **File Secrets** - SSH keys, certificates, service accounts

#### Secret Manager Support

- Harness Secret Manager (built-in)
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- GCP Secret Manager

#### Usage

```python
from harness_sdk import SecretsManager

secrets_mgr = SecretsManager(client, project_id)

# Create text secret
config = {
    "name": "GitHub Token",
    "identifier": "github_token",
    "value_type": "Inline",
    "value": "<+input>",
    "secret_manager_identifier": "harnessSecretManager"
}
result = secrets_mgr.create_text_secret(config)

# Create file secret
file_config = {
    "name": "SSH Key",
    "identifier": "ssh_key",
    "secret_manager_identifier": "harnessSecretManager"
}
result = secrets_mgr.create_file_secret(file_config)
```

#### Configuration Options

**Text Secrets:**
- `value_type`: "Inline" or "Reference"
- `value`: Secret value or `<+input>` for runtime
- `secret_manager_identifier`: Which secret manager to use
- `tags`: Organization tags

**File Secrets:**
- `secret_manager_identifier`: Which secret manager to use
- `tags`: Organization tags
- **Note:** File content uploaded separately via UI

---

## 👥 rbac.py

### `RBACManager`

Manages user groups and service accounts.

#### Features

- User email → ID lookup
- Service account creation
- API token generation (optional)
- Tags and metadata

#### Usage

```python
from harness_sdk import RBACManager

rbac_mgr = RBACManager(client, project_id)

# Create user group
group_config = {
    "name": "Developers",
    "identifier": "developers",
    "description": "Development team",
    "users": ["dev1@company.com", "dev2@company.com"],
    "tags": {"team": "dev"}
}
result = rbac_mgr.create_user_group(group_config)

# Create service account
sa_config = {
    "name": "CI Pipeline",
    "identifier": "ci_pipeline",
    "email": "ci@harness.serviceaccount",
    "create_token": False,
    "tags": {"purpose": "ci"}
}
result = rbac_mgr.create_service_account(sa_config)
```

#### Configuration Options

**User Groups:**
- `users`: List of email addresses (must exist in Harness)
- `description`: Group purpose
- `tags`: Organization tags

**Service Accounts:**
- `email`: Service account email
- `create_token`: Auto-generate API token (true/false)
- `description`: Account purpose
- `tags`: Organization tags

---

## 🌍 resources.py

### `ResourceManager`

Manages environments, infrastructures, and services.

#### Resource Types

1. **Environments** - Dev, Staging, Production
2. **Infrastructures** - Kubernetes Direct
3. **Services** - Kubernetes services

#### Usage

```python
from harness_sdk import ResourceManager

resource_mgr = ResourceManager(client, project_id)

# Create environment
env_config = {
    "name": "Production",
    "identifier": "prod",
    "type": "Production",
    "tags": {"env": "prod"},
    "variables": [
        {"name": "LOG_LEVEL", "value": "WARN", "type": "String"}
    ]
}
result = resource_mgr.create_environment(env_config)

# Create infrastructure
infra_config = {
    "name": "Prod K8s",
    "identifier": "prod_k8s",
    "environment_ref": "prod",
    "type": "KubernetesDirect",
    "deployment_type": "Kubernetes",
    "config": {
        "connector_ref": "k8s_connector",
        "namespace": "production",
        "release_name": "myapp",
        "allow_simultaneous": False
    }
}
result = resource_mgr.create_infrastructure(infra_config)

# Create service
service_config = {
    "name": "Backend API",
    "identifier": "backend_api",
    "type": "Kubernetes",
    "config": {
        "manifests": [{
            "identifier": "manifests",
            "type": "K8sManifest",
            "connector_ref": "github",
            "git_details": {
                "branch": "main",
                "paths": ["k8s/"]
            }
        }],
        "artifacts": [{
            "identifier": "image",
            "type": "DockerRegistry",
            "connector_ref": "dockerhub",
            "image_path": "myorg/backend"
        }]
    }
}
result = resource_mgr.create_service(service_config)
```

#### Configuration Options

**Environments:**
- `type`: "Production" or "PreProduction"
- `variables`: List of environment variables
- `tags`: Organization tags

**Infrastructures:**
- `type`: "KubernetesDirect" (currently supported)
- `environment_ref`: Environment identifier
- `config`: Infrastructure-specific configuration
- `connector_ref`: Kubernetes connector reference
- `namespace`: K8s namespace
- `allow_simultaneous`: Allow concurrent deployments

**Services:**
- `type`: "Kubernetes" (currently supported)
- `manifests`: K8s manifest configurations
- `artifacts`: Docker image configurations
- `connector_ref`: Can use `<+input>` for runtime

---

## 🔄 pipelines.py

### `PipelineManager`

Manages template-based pipelines.

#### Usage

```python
from harness_sdk import PipelineManager

pipeline_mgr = PipelineManager(client, project_id)

# Create pipeline from template
pipeline_config = {
    "deployment": {
        "name": "Production Deployment",
        "identifier": "prod_deploy",
        "description": "Deploy to production",
        "template_ref": "deployment_template",
        "version": "v1",
        "tags": {"env": "prod"}
    }
}
result = pipeline_mgr.create_pipelines_from_config(pipeline_config)
```

#### Configuration Options

- `template_ref`: Pipeline template identifier
- `version`: Template version
- `tags`: Organization tags
- `description`: Pipeline purpose

---

## ✅ validators.py

### `ConfigValidator`

Validates configuration before API calls.

#### Validation Rules

- Identifier format: lowercase, underscores
- Required fields presence
- Email format
- Environment type values
- Service type values

#### Usage

```python
from harness_sdk import ConfigValidator

validator = ConfigValidator()

# Validate configuration
errors = validator.validate_full_config(config_dict)
if errors:
    print("Validation errors:", errors)
```

---

## 📦 models.py

### Data Models

#### `HarnessConfig`

```python
@dataclass
class HarnessConfig:
    account_id: str
    api_key: str
    org_id: str
```

#### `ResourceResult`

```python
@dataclass
class ResourceResult:
    resource_type: str
    identifier: str
    name: str
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
```

---

## 🔄 Idempotency

All managers support idempotent operations:

1. **GET Check** - Check if resource exists
2. **Create if Missing** - Only create if doesn't exist
3. **Return Success** - Return success for existing resources

### Example

```python
# First run - creates resource
result = connector_mgr.create_kubernetes_connector(config)
# Output: "✓ Connector created"

# Second run - reuses resource
result = connector_mgr.create_kubernetes_connector(config)
# Output: "✓ Connector already exists (using existing)"
```

---

## 🚨 Error Handling

### Automatic Retries

- 3 retry attempts
- Exponential backoff
- Comprehensive error logging

### Error Types

- `401 Unauthorized` - Invalid API key
- `404 Not Found` - Resource doesn't exist
- `409 Conflict` - Resource already exists (handled)
- `400 Bad Request` - Invalid payload

---

## 📚 API Reference

All methods return `ResourceResult` objects:

```python
result = ResourceResult(
    resource_type="connector",
    identifier="my_connector",
    name="My Connector",
    success=True,
    data={"status": "created"}
)
```

---

## 🔗 Dependencies

```python
import requests      # HTTP client
import yaml         # YAML parsing
import logging      # Logging
from typing import Dict, List, Optional
from dataclasses import dataclass
```

---

## 📖 Related Documentation

- **Main README**: [`../README.md`](../README.md)
- **Scripts Docs**: [`../scripts/README.md`](../scripts/README.md)
- **Examples**: [`../examples/README.md`](../examples/README.md)

---

**For implementation examples, see [`../examples/`](../examples/)**
