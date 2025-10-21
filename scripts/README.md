# 📜 Scripts Directory

This directory contains the main automation scripts for creating Harness resources.

---

## 📁 Files

### `create_resources.py`

**Main orchestration script for creating all Harness resources.**

#### Usage

```bash
python3 create_resources.py --config <config-file> [options]
```

#### Options

| Option | Description | Required |
|--------|-------------|----------|
| `--config PATH` | Path to YAML configuration file | Yes |
| `--dry-run` | Validate configuration without creating resources | No |
| `--verbose` | Enable detailed debug logging | No |

#### Examples

```bash
# Create all resources
python3 create_resources.py --config ../examples/complete-deployment.yaml

# Dry run (validation only)
python3 create_resources.py --config myconfig.yaml --dry-run

# With verbose logging
python3 create_resources.py --config myconfig.yaml --verbose
```

---

## 🔧 Technical Details

### Execution Flow

The script follows this order:

1. **Load Configuration** - Parse YAML file
2. **Validate** - Check all required fields
3. **Initialize Client** - Set up Harness API client
4. **Create Project** - Create or reuse project
5. **Create Connectors** - Set up all connectors
6. **Create Secrets** - Store sensitive data
7. **Create RBAC** - User groups & service accounts
8. **Create Environments** - Dev, Staging, Prod
9. **Create Infrastructures** - K8s clusters
10. **Create Services** - Application services
11. **Create Pipelines** - Deployment pipelines
12. **Save Results** - Export JSON with all resource IDs

### Error Handling

- **Retries**: Automatic retry with exponential backoff (3 attempts)
- **Idempotency**: Checks for existing resources before creation
- **Validation**: Pre-flight validation before any API calls
- **Logging**: Comprehensive logging to console and file

### Output Files

#### `harness_resources_<project>_<timestamp>.json`

Contains all created resource IDs and metadata:

```json
{
  "project": {
    "identifier": "my_project",
    "name": "My Project"
  },
  "connectors": [
    {
      "identifier": "k8s_connector",
      "name": "Kubernetes Cluster",
      "status": "created"
    }
  ]
}
```

#### `harness_resources.log`

Detailed execution log with timestamps and debug information.

---

## 🎛️ Configuration Format

### Required Sections

```yaml
harness:
  account_id: "YOUR_ACCOUNT_ID"
  api_key: "YOUR_API_KEY"
  org_id: "default"

project:
  repo_name: "project_identifier"
  description: "Project description"
```

### Optional Sections

All other sections are optional and can be mixed:

- `connectors` - Connector definitions
- `secrets` - Secret definitions
- `access_control` - RBAC configuration
- `environments` - Environment definitions
- `infrastructures` - Infrastructure definitions
- `services` - Service definitions
- `pipelines` - Pipeline definitions

---

## 🔍 Validation Rules

### Project Validation

- `repo_name`: Required, lowercase, underscores allowed
- `description`: Optional string

### Connector Validation

- `name`: Required display name
- `identifier`: Required unique ID
- Type-specific fields vary by connector type

### Environment Validation

- `name`: Required
- `identifier`: Required
- `type`: Must be "Production" or "PreProduction"

### Service Validation

- `name`: Required
- `identifier`: Required
- `type`: Must be "Kubernetes" (currently)

---

## 🚨 Error Messages

### Common Errors

**`Configuration validation failed`**
- Check required fields in YAML
- Verify identifier format (lowercase, underscores)

**`401 Unauthorized`**
- Invalid API key
- Check account_id and api_key

**`409 Conflict`**
- Resource already exists
- This is handled automatically (idempotent)

**`400 Bad Request`**
- Invalid payload structure
- Check connector configuration
- Verify secret references exist

**`User not found`**
- Email address doesn't exist in Harness
- Add user to Harness first

---

## 🔐 Security Best Practices

### API Key Management

```bash
# Use environment variables
export HARNESS_API_KEY="your_api_key"

# Reference in config
harness:
  api_key: ${HARNESS_API_KEY}
```

### Secrets in Configuration

- Use `<+input>` for runtime prompts
- Reference existing secrets by identifier
- Never hardcode sensitive values

---

## ⚡ Performance

### Execution Time

| Resources | Average Time |
|-----------|--------------|
| 1-10 | 30-60 seconds |
| 10-25 | 1-2 minutes |
| 25-50 | 2-3 minutes |
| 50+ | 3-5 minutes |

### Optimization Tips

1. **Batch Similar Resources** - Group connectors together
2. **Use Same Project** - Avoid creating multiple projects
3. **Minimize Secrets** - Reuse secrets across connectors
4. **Parallel Safe** - Script handles concurrency internally

---

## 🧪 Testing

### Dry Run Mode

```bash
python3 create_resources.py --config test.yaml --dry-run
```

**What it does:**
- ✅ Validates YAML syntax
- ✅ Checks required fields
- ✅ Verifies identifier formats
- ❌ Does NOT create resources
- ❌ Does NOT call Harness API

### Idempotency Test

```bash
# Run twice
python3 create_resources.py --config test.yaml
python3 create_resources.py --config test.yaml

# Second run should reuse all resources
```

---

## 📊 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - all resources created |
| 1 | Validation error |
| 1 | API error |
| 2 | Keyboard interrupt (Ctrl+C) |

---

## 🔄 Idempotency Details

### How It Works

1. **GET Check** - Try to fetch resource by identifier
2. **If exists** - Log "already exists" and continue
3. **If not** - Create the resource
4. **409 Handling** - Catch conflicts and mark as existing

### Resources with GET Check

- Projects
- Connectors
- Secrets
- User Groups
- Service Accounts

### Resources with 409 Handling

- Environments
- Infrastructures
- Services
- Pipelines

---

## 🐛 Debugging

### Enable Verbose Logging

```bash
python3 create_resources.py --config test.yaml --verbose
```

### Check Logs

```bash
tail -f harness_resources.log
```

### Common Debug Steps

1. Run with `--dry-run` first
2. Enable `--verbose` logging
3. Check `harness_resources.log`
4. Verify API key permissions
5. Test with minimal config first

---

## 📚 Related Documentation

- **Main README**: [`../README.md`](../README.md)
- **SDK Documentation**: [`../harness_sdk/README.md`](../harness_sdk/README.md)
- **Examples**: [`../examples/README.md`](../examples/README.md)
- **Feature Docs**: [`../ALL_FEATURES_DOCUMENTATION.md`](../ALL_FEATURES_DOCUMENTATION.md)

---

## 🎯 Quick Reference

```bash
# Most common usage
python3 scripts/create_resources.py --config examples/complete-deployment.yaml

# Test configuration
python3 scripts/create_resources.py --config myconfig.yaml --dry-run

# Debug issues
python3 scripts/create_resources.py --config myconfig.yaml --verbose

# View results
cat harness_resources_*.json | jq .
```

---

**For more help, see the main [README](../README.md)**
