"""
Secrets Manager - Manages Harness secrets
Based on official Harness API documentation
"""

import logging
from typing import Dict
from .client import HarnessClient
from .models import ResourceResult

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    Manages Harness secrets: Text Secrets, File Secrets, SSH Keys
    Reference: https://apidocs.harness.io/tag/Secrets
    """
    
    def __init__(self, client: HarnessClient, project_id: str):
        self.client = client
        self.project_id = project_id
    
    def create_text_secret(self, config: Dict) -> ResourceResult:
        """
        Create text secret
        
        Args:
            config: Secret configuration containing:
                - name: Secret name
                - identifier: Unique identifier
                - description: Optional description
                - value: Secret value (or value_type for input)
                - secret_manager_identifier: Secret manager to use
                
        Returns:
            ResourceResult object
        """
        name = config.get("name")
        identifier = config.get("identifier")
        description = config.get("description", "")
        value = config.get("value", "")
        value_type = config.get("value_type", "Inline")  # Inline or Reference
        secret_manager_id = config.get("secret_manager_identifier", "harnessSecretManager")
        
        # Check if secret exists first
        try:
            get_endpoint = f"/ng/api/v2/secrets/{identifier}?accountIdentifier={self.client.config.account_id}&orgIdentifier={self.client.config.org_id}&projectIdentifier={self.project_id}"
            existing = self.client.get(get_endpoint)
            if existing and existing.get("data"):
                logger.info(f"✓ Secret already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="secret",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing", "type": "SecretText"}
                )
        except:
            # Secret doesn't exist, continue to create
            pass
        
        logger.info(f"Creating text secret: {name}")
        
        # Build secret YAML
        secret_yaml = f"""secret:
  type: SecretText
  name: {name}
  identifier: {identifier}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  description: {description}
  tags: {{}}
  spec:
    secretManagerIdentifier: {secret_manager_id}
    valueType: {value_type}
"""
        
        if value_type == "Inline" and value:
            secret_yaml += f"    value: {value}\n"
        
        endpoint = self.client.build_endpoint(
            "/ng/api/v2/secrets",
            project_id=self.project_id
        )
        
        # Wrap YAML in JSON payload
        payload = {
            "secret": {
                "type": "SecretText",
                "name": name,
                "identifier": identifier,
                "orgIdentifier": self.client.config.org_id,
                "projectIdentifier": self.project_id,
                "description": description,
                "tags": config.get("tags", {}),
                "spec": {
                    "secretManagerIdentifier": secret_manager_id,
                    "valueType": value_type
                }
            }
        }
        
        if value_type == "Inline" and value:
            payload["secret"]["spec"]["value"] = value
        
        try:
            result = self.client.post(endpoint, payload)
            
            if result.get("status") == "already_exists":
                logger.info(f"✓ Secret already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="secret",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing", "type": "SecretText"}
                )
            
            logger.info(f"✓ Secret created: {name}")
            
            return ResourceResult(
                resource_type="secret",
                identifier=identifier,
                name=name,
                success=True,
                data={"status": "created", "type": "SecretText"}
            )
        except Exception as e:
            if "409" in str(e) or "already exists" in str(e).lower():
                logger.info(f"✓ Secret already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="secret",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing", "type": "SecretText"}
                )
            
            logger.error(f"✗ Failed to create secret {name}: {e}")
            return ResourceResult(
                resource_type="secret",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
    
    def create_file_secret(self, config: Dict) -> ResourceResult:
        """
        Create file secret
        
        Args:
            config: Secret configuration
                
        Returns:
            ResourceResult object
        """
        name = config.get("name")
        identifier = config.get("identifier")
        description = config.get("description", "")
        secret_manager_id = config.get("secret_manager_identifier", "harnessSecretManager")
        
        # Check if secret exists first
        try:
            get_endpoint = f"/ng/api/v2/secrets/{identifier}?accountIdentifier={self.client.config.account_id}&orgIdentifier={self.client.config.org_id}&projectIdentifier={self.project_id}"
            existing = self.client.get(get_endpoint)
            if existing and existing.get("data"):
                logger.info(f"✓ File secret already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="secret",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing", "type": "SecretFile"}
                )
        except:
            pass
        
        logger.info(f"Creating file secret: {name}")
        
        endpoint = self.client.build_endpoint(
            "/ng/api/v2/secrets",
            project_id=self.project_id
        )
        
        payload = {
            "secret": {
                "type": "SecretFile",
                "name": name,
                "identifier": identifier,
                "orgIdentifier": self.client.config.org_id,
                "projectIdentifier": self.project_id,
                "description": description,
                "tags": config.get("tags", {}),
                "spec": {
                    "secretManagerIdentifier": secret_manager_id
                }
            }
        }
        
        try:
            result = self.client.post(endpoint, payload)
            
            if result.get("status") == "already_exists":
                logger.info(f"✓ File secret already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="secret",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing", "type": "SecretFile"}
                )
            
            logger.info(f"✓ File secret created: {name}")
            
            return ResourceResult(
                resource_type="secret",
                identifier=identifier,
                name=name,
                success=True,
                data={"status": "created", "type": "SecretFile"}
            )
        except Exception as e:
            if "409" in str(e) or "already exists" in str(e).lower():
                logger.info(f"✓ File secret already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="secret",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing", "type": "SecretFile"}
                )
            
            logger.error(f"✗ Failed to create file secret {name}: {e}")
            return ResourceResult(
                resource_type="secret",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
