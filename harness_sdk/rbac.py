"""
RBAC Manager - Manages Role-Based Access Control
Handles: Users, User Groups, Service Accounts, Resource Groups, Roles
Based on official Harness API documentation
"""

import logging
import json
from typing import Dict, List, Optional
from .client import HarnessClient
from .models import ResourceResult

logger = logging.getLogger(__name__)


class RBACManager:
    """
    Manages all RBAC resources in Harness
    Reference: https://apidocs.harness.io/tag/User-Group
               https://apidocs.harness.io/tag/Service-Accounts
               https://apidocs.harness.io/tag/Resource-Groups
               https://apidocs.harness.io/tag/Roles
    """
    
    def __init__(self, client: HarnessClient, project_id: str):
        self.client = client
        self.project_id = project_id
    
    def lookup_user_ids(self, emails: List[str]) -> Dict[str, Optional[str]]:
        """
        Look up Harness user IDs from email addresses
        
        Args:
            emails: List of email addresses
            
        Returns:
            Dictionary mapping email to user ID (None if not found)
        """
        user_mapping = {}
        
        for email in emails:
            try:
                endpoint = self.client.build_endpoint(
                    "/ng/api/user/aggregate",
                    searchTerm=email
                )
                
                result = self.client.post(endpoint, {"filterType": "USER"})
                
                if result and 'data' in result and 'content' in result['data']:
                    users = result['data']['content']
                    if users and len(users) > 0:
                        user_id = users[0].get('user', {}).get('uuid')
                        if user_id:
                            user_mapping[email] = user_id
                            logger.info(f"  ✓ Found user: {email}")
                            continue
                
                logger.warning(f"  ⚠ User not found: {email}")
                user_mapping[email] = None
                
            except Exception as e:
                logger.error(f"  ✗ Error looking up {email}: {e}")
                user_mapping[email] = None
        
        return user_mapping
    
    def create_user_group(self, config: Dict) -> ResourceResult:
        """
        Create user group
        
        Args:
            config: User group configuration containing:
                - name: Group name
                - identifier: Unique identifier
                - description: Optional description
                - users: List of user emails
                - tags: Optional tags
                
        Returns:
            ResourceResult object
        """
        name = config.get("name")
        identifier = config.get("identifier")
        description = config.get("description", "")
        
        # Check if user group exists first
        try:
            get_endpoint = f"/ng/api/user-groups/{identifier}?accountIdentifier={self.client.config.account_id}&orgIdentifier={self.client.config.org_id}&projectIdentifier={self.project_id}"
            existing = self.client.get(get_endpoint)
            if existing and existing.get("data"):
                logger.info(f"✓ User group already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="user_group",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"user_count": len(config.get("users", [])), "status": "existing"}
                )
        except:
            # User group doesn't exist, continue to create
            pass
        
        logger.info(f"Creating user group: {name}")
        
        # Convert email addresses to user IDs
        user_emails = config.get("users", [])
        user_ids = []
        
        if user_emails:
            logger.info(f"  Looking up {len(user_emails)} user(s)...")
            user_mapping = self.lookup_user_ids(user_emails)
            user_ids = [uid for uid in user_mapping.values() if uid is not None]
            
            if len(user_ids) < len(user_emails):
                logger.warning(f"  ⚠ Only found {len(user_ids)}/{len(user_emails)} users")
        
        endpoint = self.client.build_endpoint(
            "/ng/api/user-groups",
            project_id=self.project_id
        )
        
        payload = {
            "identifier": identifier,
            "name": name,
            "description": description,
            "tags": config.get("tags", {}),
            "users": user_ids,
            "notificationConfigs": []
        }
        
        try:
            result = self.client.post(endpoint, payload)
            
            if result.get("status") == "already_exists":
                logger.info(f"✓ User group already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="user_group",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"user_count": len(user_ids), "status": "existing"}
                )
            
            logger.info(f"✓ User group created: {name} with {len(user_ids)} user(s)")
            
            return ResourceResult(
                resource_type="user_group",
                identifier=identifier,
                name=name,
                success=True,
                data={"user_count": len(user_ids), "status": "created"}
            )
        except Exception as e:
            if "409" in str(e) or "already exists" in str(e).lower():
                logger.info(f"✓ User group already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="user_group",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"user_count": len(user_ids), "status": "existing"}
                )
            
            logger.error(f"✗ Failed to create user group {name}: {e}")
            return ResourceResult(
                resource_type="user_group",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
    
    def create_service_account(self, config: Dict) -> ResourceResult:
        """
        Create service account for automation
        
        Args:
            config: Service account configuration
            
        Returns:
            ResourceResult object
        """
        name = config.get("name")
        identifier = config.get("identifier")
        description = config.get("description", "")
        email = config.get("email", f"{identifier}@harness.serviceaccount")
        
        # Check if service account exists first
        try:
            get_endpoint = f"/ng/api/serviceaccount/{identifier}?accountIdentifier={self.client.config.account_id}&orgIdentifier={self.client.config.org_id}&projectIdentifier={self.project_id}"
            existing = self.client.get(get_endpoint)
            if existing and existing.get("data"):
                logger.info(f"✓ Service account already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="service_account",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"email": email, "status": "existing"}
                )
        except:
            # Service account doesn't exist, continue to create
            pass
        
        logger.info(f"Creating service account: {name}")
        
        # Build endpoint with query parameters
        endpoint = self.client.build_endpoint(
            "/ng/api/serviceaccount",
            project_id=self.project_id
        )
        
        # Payload - just the service account details
        payload = {
            "identifier": identifier,
            "name": name,
            "email": email,
            "description": description,
            "tags": config.get("tags", {}),
            "accountIdentifier": self.client.config.account_id,
            "orgIdentifier": self.client.config.org_id,
            "projectIdentifier": self.project_id
        }
        
        try:
            result = self.client.post(endpoint, payload)
            logger.info(f"✓ Service account created: {name}")
            
            # Create API token if requested
            token_data = None
            if config.get("create_token", False):
                token_data = self.create_service_account_token(identifier, name)
            
            return ResourceResult(
                resource_type="service_account",
                identifier=identifier,
                name=name,
                success=True,
                data={"email": email, "token": token_data}
            )
            
        except Exception as e:
            logger.error(f"✗ Failed to create service account {name}: {e}")
            return ResourceResult(
                resource_type="service_account",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
    
    def create_service_account_token(self, sa_identifier: str, sa_name: str) -> Optional[Dict]:
        """
        Create API token for service account
        
        Args:
            sa_identifier: Service account identifier
            sa_name: Service account name
            
        Returns:
            Token data or None if failed
        """
        logger.info(f"  Creating API token for: {sa_name}")
        
        endpoint = self.client.build_endpoint(
            f"/ng/api/service-accounts/{sa_identifier}/tokens"
        )
        
        payload = {
            "identifier": f"{sa_identifier}_token",
            "name": f"{sa_name} Token",
            "apiKeyType": "SERVICE_ACCOUNT",
            "parentIdentifier": sa_identifier,
            "apiKeyIdentifier": sa_identifier,
            "accountIdentifier": self.client.config.account_id,
            "orgIdentifier": self.client.config.org_id,
            "projectIdentifier": self.project_id
        }
        
        try:
            result = self.client.post(endpoint, payload)
            logger.info(f"  ✓ API token created")
            return result
        except Exception as e:
            logger.error(f"  ✗ Failed to create API token: {e}")
            return None
    
    def create_resource_group(self, config: Dict) -> ResourceResult:
        """
        Create resource group for permission management
        
        Args:
            config: Resource group configuration
            
        Returns:
            ResourceResult object
        """
        name = config.get("name")
        identifier = config.get("identifier")
        description = config.get("description", "")
        
        logger.info(f"Creating resource group: {name}")
        
        # Build endpoint with query parameters
        endpoint = self.client.build_endpoint(
            "/resourcegroup/api/v2/resourcegroup",
            project_id=self.project_id
        )
        
        # Build resource filter - simpler structure
        resources = []
        for scope in config.get("included_scopes", []):
            resources.append({
                "resourceType": scope.get("resource_type"),
                "identifiers": scope.get("identifiers", [])
            })
        
        payload = {
            "identifier": identifier,
            "name": name,
            "description": description,
            "tags": config.get("tags", {}),
            "color": config.get("color", "#0063F7"),
            "accountIdentifier": self.client.config.account_id,
            "orgIdentifier": self.client.config.org_id,
            "projectIdentifier": self.project_id,
            "resourceFilter": {
                "includeAllResources": config.get("include_all_resources", False),
                "resources": resources
            }
        }
        
        try:
            result = self.client.post(endpoint, payload)
            
            if result.get("status") == "already_exists":
                logger.info(f"✓ Resource group already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="resource_group",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing"}
                )
            
            logger.info(f"✓ Resource group created: {name}")
            
            return ResourceResult(
                resource_type="resource_group",
                identifier=identifier,
                name=name,
                success=True,
                data={"status": "created"}
            )
            
        except Exception as e:
            if "409" in str(e) or "already exists" in str(e).lower():
                logger.info(f"✓ Resource group already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="resource_group",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing"}
                )
            
            logger.error(f"✗ Failed to create resource group {name}: {e}")
            return ResourceResult(
                resource_type="resource_group",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
    
    def create_role(self, config: Dict) -> ResourceResult:
        """
        Create custom role
        
        Args:
            config: Role configuration
            
        Returns:
            ResourceResult object
        """
        name = config.get("name")
        identifier = config.get("identifier")
        description = config.get("description", "")
        
        logger.info(f"Creating role: {name}")
        
        endpoint = self.client.build_endpoint(
            "/authz/api/roles",
            project_id=self.project_id
        )
        
        # Build permissions
        permissions = []
        for perm in config.get("permissions", []):
            permissions.append({
                "resourceType": perm.get("resource_type"),
                "permission": perm.get("actions", [])
            })
        
        payload = {
            "identifier": identifier,
            "name": name,
            "description": description,
            "tags": config.get("tags", {}),
            "permissions": permissions,
            "allowedScopeLevels": config.get("allowed_scope_levels", ["project"])
        }
        
        try:
            result = self.client.post(endpoint, payload)
            
            if result.get("status") == "already_exists":
                logger.info(f"✓ Role already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="role",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"permissions_count": len(permissions), "status": "existing"}
                )
            
            logger.info(f"✓ Role created: {name}")
            
            return ResourceResult(
                resource_type="role",
                identifier=identifier,
                name=name,
                success=True,
                data={"permissions_count": len(permissions), "status": "created"}
            )
            
        except Exception as e:
            if "409" in str(e) or "already exists" in str(e).lower():
                logger.info(f"✓ Role already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="role",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"permissions_count": len(permissions), "status": "existing"}
                )
            
            logger.error(f"✗ Failed to create role {name}: {e}")
            return ResourceResult(
                resource_type="role",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
    
    def create_rbac_from_config(self, access_control_config: Dict) -> Dict[str, List[ResourceResult]]:
        """
        Create all RBAC resources from configuration
        
        Args:
            access_control_config: Access control configuration
            
        Returns:
            Dictionary mapping resource types to lists of results
        """
        results = {
            "user_groups": [],
            "service_accounts": [],
            "resource_groups": [],
            "roles": []
        }
        
        # Create roles first (may be referenced by groups)
        if "roles" in access_control_config:
            logger.info(f"\n{'=' * 80}\nCreating Custom Roles\n{'=' * 80}")
            for role_config in access_control_config["roles"]:
                result = self.create_role(role_config)
                results["roles"].append(result)
        
        # Create resource groups (may be referenced by groups)
        if "resource_groups" in access_control_config:
            logger.info(f"\n{'=' * 80}\nCreating Resource Groups\n{'=' * 80}")
            for rg_config in access_control_config["resource_groups"]:
                result = self.create_resource_group(rg_config)
                results["resource_groups"].append(result)
        
        # Create service accounts
        if "service_accounts" in access_control_config:
            logger.info(f"\n{'=' * 80}\nCreating Service Accounts\n{'=' * 80}")
            for sa_config in access_control_config["service_accounts"]:
                result = self.create_service_account(sa_config)
                results["service_accounts"].append(result)
        
        # Create user groups
        if "user_groups" in access_control_config:
            logger.info(f"\n{'=' * 80}\nCreating User Groups\n{'=' * 80}")
            for ug_config in access_control_config["user_groups"]:
                result = self.create_user_group(ug_config)
                results["user_groups"].append(result)
        
        return results
