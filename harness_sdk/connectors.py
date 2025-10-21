"""
Connector Manager - Manages all Harness connector types
Based on official Harness API documentation
Supports: Cloud providers, Git, Docker, Artifacts, CI/CD, Monitoring, Notifications
"""

import yaml
import json
import logging
from typing import Dict, List
from .client import HarnessClient
from .models import ResourceResult, ConnectorType

logger = logging.getLogger(__name__)


class ConnectorManager:
    """
    Manages all Harness connector types
    Reference: https://apidocs.harness.io/tag/Connectors
    """
    
    def __init__(self, client: HarnessClient, project_id: str):
        self.client = client
        self.project_id = project_id
    
    def _create_connector(self, connector_yaml: str, name: str, identifier: str) -> ResourceResult:
        """Generic connector creation method (idempotent)"""
        # Check if connector exists first
        try:
            get_endpoint = f"/ng/api/connectors/{identifier}?accountIdentifier={self.client.config.account_id}&orgIdentifier={self.client.config.org_id}&projectIdentifier={self.project_id}"
            existing = self.client.get(get_endpoint)
            if existing and existing.get("data"):
                logger.info(f"✓ Connector already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="connector",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing"}
                )
        except:
            # Connector doesn't exist, continue to create
            pass
        
        endpoint = self.client.build_endpoint("/ng/api/connectors")
        
        try:
            # Parse YAML and create connector
            connector_dict = yaml.safe_load(connector_yaml)
            payload = {"connector": connector_dict["connector"]}
            
            result = self.client.post(endpoint, payload)
            
            # Check if already exists
            if result.get("status") == "already_exists":
                logger.info(f"✓ Connector already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="connector",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing"}
                )
            
            logger.info(f"✓ Connector created: {name}")
            
            return ResourceResult(
                resource_type="connector",
                identifier=identifier,
                name=name,
                success=True,
                data={"status": "created"}
            )
        except Exception as e:
            # Handle 409 conflict
            if "409" in str(e) or "already exists" in str(e).lower():
                logger.info(f"✓ Connector already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="connector",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing"}
                )
            
            logger.error(f"✗ Failed to create connector {name}: {e}")
            return ResourceResult(
                resource_type="connector",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
    
    def create_kubernetes_connector(self, config: Dict) -> ResourceResult:
        """
        Create Kubernetes cluster connector
        Type: K8sCluster
        """
        name = config.get("name")
        identifier = config.get("identifier")
        
        logger.info(f"Creating Kubernetes connector: {name}")
        
        delegate_selectors = config.get('delegate_selectors', [])
        
        connector_yaml = f"""connector:
  name: {name}
  identifier: {identifier}
  description: {config.get('description', '')}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  type: K8sCluster
  tags: {{}}
  spec:
    credential:
      type: {config.get('credential_type', 'InheritFromDelegate')}
"""
        
        # Add delegate selectors as proper YAML list
        if delegate_selectors:
            connector_yaml += "    delegateSelectors:\n"
            for selector in delegate_selectors:
                connector_yaml += f"      - {selector}\n"
        
        return self._create_connector(connector_yaml, name, identifier)
    
    def create_github_connector(self, config: Dict) -> ResourceResult:
        """
        Create GitHub connector
        Type: Github
        """
        name = config.get("name")
        identifier = config.get("identifier")
        auth = config.get('authentication', {})
        api_access = config.get('api_access', {})
        
        logger.info(f"Creating GitHub connector: {name}")
        
        delegate_selectors = config.get('delegate_selectors', [])
        execute_on_delegate = config.get('execute_on_delegate', False)
        
        connector_yaml = f"""connector:
  name: {name}
  identifier: {identifier}
  description: {config.get('description', '')}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  type: Github
  tags: {{}}
  spec:
    url: {config.get('url')}
    validationRepo: {config.get('validation_repo', '')}
    authentication:
      type: {auth.get('type', 'Http')}
      spec:
        type: {auth.get('spec_type', 'UsernameToken')}
        spec:
          username: {auth.get('username', '')}
          tokenRef: {auth.get('token_ref', '<+input>')}
    apiAccess:
      type: {api_access.get('type', 'Token')}
      spec:
        tokenRef: {api_access.get('token_ref', '<+input>')}
"""
        
        # Add delegate selectors as proper YAML list
        if delegate_selectors:
            connector_yaml += "    delegateSelectors:\n"
            for selector in delegate_selectors:
                connector_yaml += f"      - {selector}\n"
        
        connector_yaml += f"    executeOnDelegate: {str(execute_on_delegate).lower()}\n"
        
        return self._create_connector(connector_yaml, name, identifier)
    
    def create_gitlab_connector(self, config: Dict) -> ResourceResult:
        """Create GitLab connector"""
        name = config.get("name")
        identifier = config.get("identifier")
        auth = config.get('authentication', {})
        api_access = config.get('api_access', {})
        
        logger.info(f"Creating GitLab connector: {name}")
        
        delegate_selectors = config.get('delegate_selectors', [])
        
        connector_yaml = f"""connector:
  name: {name}
  identifier: {identifier}
  description: {config.get('description', '')}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  type: Gitlab
  tags: {{}}
  spec:
    url: {config.get('url')}
    validationRepo: {config.get('validation_repo', '')}
    authentication:
      type: {auth.get('type', 'Http')}
      spec:
        type: {auth.get('spec_type', 'UsernameToken')}
        spec:
          username: {auth.get('username', '')}
          tokenRef: {auth.get('token_ref', '<+input>')}
    apiAccess:
      type: {api_access.get('type', 'Token')}
      spec:
        tokenRef: {api_access.get('token_ref', '<+input>')}
"""
        
        # Add delegate selectors as proper YAML list
        if delegate_selectors:
            connector_yaml += "    delegateSelectors:\n"
            for selector in delegate_selectors:
                connector_yaml += f"      - {selector}\n"
        
        connector_yaml += "    executeOnDelegate: false\n"
        
        return self._create_connector(connector_yaml, name, identifier)
    
    def create_aws_connector(self, config: Dict) -> ResourceResult:
        """Create AWS connector"""
        name = config.get("name")
        identifier = config.get("identifier")
        credential_type = config.get('credential_type', 'InheritFromDelegate')
        tags = config.get('tags', {})
        delegate_selectors = config.get('delegate_selectors', [])
        
        logger.info(f"Creating AWS connector: {name}")
        
        # Build proper YAML structure
        connector_yaml = f"""connector:
  name: {name}
  identifier: {identifier}
  description: {config.get('description', '')}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  type: Aws
  tags: {{}}
  spec:
    credential:
      type: {credential_type}
"""
        
        # Add credential spec based on type
        if credential_type == 'ManualConfig':
            access_key = config.get('access_key_ref', '<+input>')
            secret_key = config.get('secret_key_ref', '<+input>')
            connector_yaml += f"""      spec:
        accessKey: {access_key}
        secretKeyRef: {secret_key}
"""
        
        # Add delegate selectors as proper YAML list
        if delegate_selectors:
            connector_yaml += "    delegateSelectors:\n"
            for selector in delegate_selectors:
                connector_yaml += f"      - {selector}\n"
        
        connector_yaml += "    executeOnDelegate: true\n"
        
        return self._create_connector(connector_yaml, name, identifier)
    
    def create_gcp_connector(self, config: Dict) -> ResourceResult:
        """Create GCP connector"""
        name = config.get("name")
        identifier = config.get("identifier")
        credential_type = config.get('credential_type', 'InheritFromDelegate')
        delegate_selectors = config.get('delegate_selectors', [])
        
        logger.info(f"Creating GCP connector: {name}")
        
        connector_yaml = f"""connector:
  name: {name}
  identifier: {identifier}
  description: {config.get('description', '')}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  type: Gcp
  tags: {{}}
  spec:
    credential:
      type: {credential_type}
"""
        
        # Add credential spec based on type
        if credential_type == 'ManualConfig':
            secret_key_ref = config.get('secret_key_ref', '<+input>')
            connector_yaml += f"""      spec:
        secretKeyRef: {secret_key_ref}
"""
        
        # Add delegate selectors as proper YAML list
        if delegate_selectors:
            connector_yaml += "    delegateSelectors:\n"
            for selector in delegate_selectors:
                connector_yaml += f"      - {selector}\n"
        
        connector_yaml += "    executeOnDelegate: true\n"
        
        return self._create_connector(connector_yaml, name, identifier)
    
    def create_azure_connector(self, config: Dict) -> ResourceResult:
        """Create Azure connector"""
        name = config.get("name")
        identifier = config.get("identifier")
        credential_type = config.get('credential_type', 'InheritFromDelegate')
        delegate_selectors = config.get('delegate_selectors', [])
        
        logger.info(f"Creating Azure connector: {name}")
        
        connector_yaml = f"""connector:
  name: {name}
  identifier: {identifier}
  description: {config.get('description', '')}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  type: Azure
  tags: {{}}
  spec:
    credential:
      type: {credential_type}
"""
        
        # Add credential spec based on type
        if credential_type == 'ManualConfig':
            client_id = config.get('client_id', '<+input>')
            tenant_id = config.get('tenant_id', '<+input>')
            secret_ref = config.get('secret_ref', '<+input>')
            connector_yaml += f"""      spec:
        applicationId: {client_id}
        tenantId: {tenant_id}
        auth:
          type: Secret
          spec:
            secretRef: {secret_ref}
"""
        
        # Add delegate selectors as proper YAML list
        if delegate_selectors:
            connector_yaml += "    delegateSelectors:\n"
            for selector in delegate_selectors:
                connector_yaml += f"      - {selector}\n"
        
        connector_yaml += "    executeOnDelegate: true\n"
        
        return self._create_connector(connector_yaml, name, identifier)
    
    def create_docker_connector(self, config: Dict) -> ResourceResult:
        """Create Docker Registry connector"""
        name = config.get("name")
        identifier = config.get("identifier")
        registry_url = config.get('registry_url', 'https://index.docker.io/v2/')
        auth_type = config.get('auth_type', 'UsernamePassword')
        
        logger.info(f"Creating Docker Registry connector: {name}")
        
        delegate_selectors = config.get('delegate_selectors', [])
        
        connector_yaml = f"""connector:
  name: {name}
  identifier: {identifier}
  description: {config.get('description', '')}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  type: DockerRegistry
  tags: {{}}
  spec:
    dockerRegistryUrl: {registry_url}
    providerType: DockerHub
    auth:
      type: {auth_type}
"""
        
        if auth_type == 'UsernamePassword':
            username = config.get('username', '<+input>')
            password_ref = config.get('password_ref', '<+input>')
            connector_yaml += f"""      spec:
        username: {username}
        passwordRef: {password_ref}
"""
        elif auth_type == 'Anonymous':
            connector_yaml += "      spec: {}\n"
        
        # Add delegate selectors as proper YAML list
        if delegate_selectors:
            connector_yaml += "    delegateSelectors:\n"
            for selector in delegate_selectors:
                connector_yaml += f"      - {selector}\n"
        
        connector_yaml += "    executeOnDelegate: false\n"
        
        return self._create_connector(connector_yaml, name, identifier)
    
    def create_bitbucket_connector(self, config: Dict) -> ResourceResult:
        """Create Bitbucket connector"""
        name = config.get("name")
        identifier = config.get("identifier")
        auth = config.get('authentication', {})
        api_access = config.get('api_access', {})
        
        logger.info(f"Creating Bitbucket connector: {name}")
        
        delegate_selectors = config.get('delegate_selectors', [])
        
        connector_yaml = f"""connector:
  name: {name}
  identifier: {identifier}
  description: {config.get('description', '')}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  type: Bitbucket
  tags: {{}}
  spec:
    url: {config.get('url')}
    validationRepo: {config.get('validation_repo', '')}
    authentication:
      type: {auth.get('type', 'Http')}
      spec:
        type: {auth.get('spec_type', 'UsernameToken')}
        spec:
          username: {auth.get('username', '')}
          tokenRef: {auth.get('token_ref', '<+input>')}
    apiAccess:
      type: {api_access.get('type', 'Token')}
      spec:
        tokenRef: {api_access.get('token_ref', '<+input>')}
"""
        
        # Add delegate selectors as proper YAML list
        if delegate_selectors:
            connector_yaml += "    delegateSelectors:\n"
            for selector in delegate_selectors:
                connector_yaml += f"      - {selector}\n"
        
        connector_yaml += "    executeOnDelegate: false\n"
        
        return self._create_connector(connector_yaml, name, identifier)
    
    def create_connectors_from_config(self, connectors_config: Dict) -> List[ResourceResult]:
        """
        Create all connectors from configuration
        
        Args:
            connectors_config: Dictionary mapping connector types to list of configs
            
        Returns:
            List of ResourceResult objects
        """
        results = []
        
        # Mapping of config keys to creation methods
        creator_map = {
            'kubernetes': self.create_kubernetes_connector,
            'github': self.create_github_connector,
            'gitlab': self.create_gitlab_connector,
            'bitbucket': self.create_bitbucket_connector,
            'docker': self.create_docker_connector,
            'docker_registry': self.create_docker_connector,  # Alias
            'aws': self.create_aws_connector,
            'gcp': self.create_gcp_connector,
            'azure': self.create_azure_connector,
        }
        
        for conn_type, connectors in connectors_config.items():
            if conn_type not in creator_map:
                logger.warning(f"Unsupported connector type: {conn_type}")
                continue
            
            creator_func = creator_map[conn_type]
            
            # Handle list of connectors
            if isinstance(connectors, list):
                for conn_config in connectors:
                    result = creator_func(conn_config)
                    results.append(result)
            # Handle single connector
            else:
                result = creator_func(connectors)
                results.append(result)
        
        return results
