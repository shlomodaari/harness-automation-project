# 🚀 Quick Start Guide - Complete Example

## Overview

The `COMPLETE_EXAMPLE.yaml` demonstrates **EVERYTHING** the Harness SDK can do in a single configuration file.

## What Gets Created

### 📊 Summary
- **48 Total Resources** created with one command
- **100% Idempotent** - safe to run multiple times
- **Production Ready** - follows best practices

### 📦 Resource Breakdown

| Category | Count | Details |
|----------|-------|---------|
| **Project** | 1 | comprehensive_test |
| **Connectors** | 13 | All cloud providers + SCM + Docker |
| **Secrets** | 13 | 10 text + 3 file secrets |
| **User Groups** | 3 | Platform, Dev, Ops teams |
| **Service Accounts** | 3 | CI, CD, Monitoring |
| **Environments** | 3 | Dev, Staging, Production |
| **Infrastructures** | 4 | Dev, Staging, Prod (Primary + DR) |
| **Services** | 4 | Backend, Frontend, Worker, User Service |
| **Pipelines** | 4 | Dev, Staging, Prod, Rollback |
| **TOTAL** | **48** | Complete setup! |

---

## 🎯 Quick Start

### 1. Review the Configuration

```bash
cd /Users/shlomodaari/armory/spinnaker-armory-services/harness-automation
cat COMPLETE_EXAMPLE.yaml
```

### 2. Run the Complete Example

```bash
python3 scripts/create_resources.py --config COMPLETE_EXAMPLE.yaml
```

### 3. Expected Output

```
✅ SUCCESS! All resources created

✓ Project: comprehensive_test
✓ Connectors: 13/13 created
  ✓ Production Kubernetes
  ✓ Development Kubernetes
  ✓ AWS Production Account
  ✓ AWS Development Account
  ✓ GCP Production Project
  ✓ GCP Development Project
  ✓ Azure Production Subscription
  ✓ Azure Development Subscription
  ✓ GitHub Organization
  ✓ GitHub Microservices
  ✓ GitLab Enterprise
  ✓ Bitbucket Cloud
  ✓ Docker Hub Public
  ... and more

✓ Secrets: 13/13 created
✓ Access Control:
  - user_groups: 3/3 created
  - service_accounts: 3/3 created
✓ Resources:
  - environments: 3/3 created
  - infrastructures: 4/4 created
  - services: 4/4 created
✓ Pipelines: 4/4 created
```

### 4. Run Again (Idempotency Test)

```bash
# Run the same command again
python3 scripts/create_resources.py --config COMPLETE_EXAMPLE.yaml
```

**Expected:** All resources show as "already exists (using existing)" ✅

---

## 📋 What's Included

### 🔌 Connectors (13 Total)

#### Cloud Providers (8)
- **2 Kubernetes:** Production + Development clusters
- **2 AWS:** Production (InheritFromDelegate) + Dev (ManualConfig)
- **2 GCP:** Production (InheritFromDelegate) + Dev (ManualConfig)
- **2 Azure:** Production (InheritFromDelegate) + Dev (ManualConfig)

#### Source Control (4)
- **2 GitHub:** Organization + Microservices repos
- **1 GitLab:** Enterprise repositories
- **1 Bitbucket:** Cloud repositories

#### Artifact Repositories (3)
- **Docker Hub:** Public images
- **Private Registry:** Company registry
- **Anonymous Docker:** Public anonymous access

### 🔐 Secrets (13 Total)

#### Text Secrets (10)
- GitHub Personal Access Token
- GitLab Access Token
- Bitbucket App Password
- Docker Hub Password
- Private Registry Password
- AWS Dev Access Key
- AWS Dev Secret Key
- Azure Dev Secret
- External API Key
- Production Database Password

#### File Secrets (3)
- GCP Dev Service Account (JSON key)
- SSH Private Key
- TLS Certificate

### 👥 Access Control (6 Total)

#### User Groups (3)
- **Platform Engineering Team** - Full admin access
- **Development Team** - Developer access
- **Operations Team** - Operator access

#### Service Accounts (3)
- **CI Pipeline Service Account** - For CI automation
- **CD Pipeline Service Account** - For CD automation
- **Monitoring Service Account** - For monitoring integrations

### 🌍 Environments (3)

1. **Development**
   - Type: PreProduction
   - Variables: DEBUG logging, 2 replicas
   
2. **Staging**
   - Type: PreProduction
   - Variables: INFO logging, 3 replicas
   
3. **Production**
   - Type: Production
   - Variables: WARN logging, 5 replicas, high SLA

### 🏗️ Infrastructures (4)

1. **Development Kubernetes** → Dev environment
2. **Staging Kubernetes** → Staging environment
3. **Production Kubernetes Primary** → Prod (primary cluster)
4. **Production Kubernetes DR** → Prod (disaster recovery)

### 🚢 Services (4)

1. **Backend API**
   - Type: Kubernetes
   - Language: Java
   - Manifests from GitHub
   - Docker image from Docker Hub

2. **Frontend Web**
   - Type: Kubernetes
   - Language: React
   - Manifests from GitHub
   - Docker image from Docker Hub

3. **Background Worker**
   - Type: Kubernetes
   - Language: Python
   - Manifests from GitHub
   - Docker image from Private Registry

4. **User Microservice**
   - Type: Kubernetes
   - Domain: User management
   - Manifests from GitHub
   - Docker image from Docker Hub

### 🔄 Pipelines (4)

1. **Development Deployment** - Automated deployment to dev
2. **Staging Deployment** - With approval gates
3. **Production Deployment** - Canary deployment with approvals
4. **Emergency Rollback** - Critical priority rollback

---

## 🛠️ Customization

### Update Account Information

```yaml
harness:
  account_id: "YOUR_ACCOUNT_ID"
  api_key: "YOUR_API_KEY"
  org_id: "YOUR_ORG_ID"
```

### Add Your Email

```yaml
access_control:
  user_groups:
    - name: "Platform Engineering Team"
      users:
        - your.email@company.com  # ← Change this
```

### Adjust Resources

You can remove sections you don't need:
- Comment out connector types you don't use
- Remove environments (e.g., staging)
- Adjust service counts
- Modify pipeline configurations

---

## 📊 Verification

### Check in Harness UI

1. **Projects** → Find `comprehensive_test`
2. **Connectors** → See all 13 connectors
3. **Secrets** → View all secrets
4. **Access Control** → Check user groups & service accounts
5. **Environments** → See Dev, Staging, Prod
6. **Services** → View all 4 services
7. **Pipelines** → Check all 4 pipelines

### Check Results File

```bash
cat harness_resources_comprehensive_test_*.json
```

---

## 🎓 Learning Path

### Beginner
Start with simpler examples:
```bash
python3 scripts/create_resources.py --config test-final-complete.yaml
```

### Intermediate
Use the connector-focused example:
```bash
python3 scripts/create_resources.py --config test-all-connector-types.yaml
```

### Advanced
Use the complete example:
```bash
python3 scripts/create_resources.py --config COMPLETE_EXAMPLE.yaml
```

---

## 🐛 Troubleshooting

### Issue: "Project already exists"
**Solution:** This is normal! The SDK is idempotent. It will reuse the existing project.

### Issue: "Connector creation failed"
**Solution:** 
1. Check if delegates are running
2. Verify secret references exist
3. Check API key permissions

### Issue: "Secret not found"
**Solution:** Secrets are created before connectors. Check if the secret creation succeeded.

### Issue: "User not found"
**Solution:** Update the email addresses in user_groups to match actual Harness users.

---

## 🔄 Cleanup (Optional)

To remove all resources:
1. Go to Harness UI
2. Delete project: `comprehensive_test`
3. This removes all resources in the project

---

## 💡 Best Practices

1. **Test with one project** to avoid clutter
2. **Use unique identifiers** for each resource
3. **Tag everything** for easy management
4. **Use `<+input>`** for runtime values
5. **Create secrets first** before connectors
6. **Run multiple times** to verify idempotency

---

## 📚 Additional Resources

- **`ALL_FEATURES_DOCUMENTATION.md`** - Complete API reference
- **`FINAL_WORKING_STATUS.md`** - Current status and features
- **`IDEMPOTENT_SUMMARY.md`** - Idempotency details

---

## ✅ Success Criteria

After running the complete example, you should have:

- ✅ 1 Project created
- ✅ 13 Connectors configured
- ✅ 13 Secrets stored
- ✅ 6 RBAC resources configured
- ✅ 3 Environments set up
- ✅ 4 Infrastructures defined
- ✅ 4 Services configured
- ✅ 4 Pipelines created

**Total: 48 resources ready for deployment!** 🎉

---

**Ready to try it? Run the command and watch the magic happen!** 🚀
