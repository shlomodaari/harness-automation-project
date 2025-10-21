"""
Resource Manager - Manages Harness project resources
Based on official Harness API documentation
"""

import json
import logging
from typing import Dict, List
from .client import HarnessClient
from .models import ResourceResult

logger = logging.getLogger(__name__)


def normalize_identifier(name: str) -> str:
    """Convert name to valid Harness identifier"""
    return name.lower().replace("-", "_").replace(" ", "_")


class ResourceManager:
    """
    Manages Harness resources: Environments, Infrastructures, Services
    Reference: https://apidocs.harness.io/tag/Environments
               https://apidocs.harness.io/tag/Infrastructures
               https://apidocs.harness.io/tag/Services
    """
    
    def __init__(self, client: HarnessClient, project_id: str):
        self.client = client
        self.project_id = project_id
    
    def create_project(self, project_config: Dict) -> ResourceResult:
        """
        Create or retrieve Harness project (idempotent)
        
        Args:
            project_config: Project configuration
            
        Returns:
            ResourceResult object
        """
        project_name = project_config.get("repo_name")
        project_id = normalize_identifier(project_name)
        description = project_config.get("description", "")
        tags = project_config.get("tags", {})
        
        # Check if project exists first (GET request)
        logger.info(f"Checking if project exists: {project_name}")
        try:
            get_endpoint = f"/ng/api/projects/{project_id}?accountIdentifier={self.client.config.account_id}&orgIdentifier={self.client.config.org_id}"
            existing = self.client.get(get_endpoint)
            if existing and existing.get("data"):
                logger.info(f"✓ Project already exists: {project_name} (using existing)")
                return ResourceResult(
                    resource_type="project",
                    identifier=project_id,
                    name=project_name,
                    success=True,
                    data={"status": "existing"}
                )
        except:
            # Project doesn't exist, continue to create
            pass
        
        logger.info(f"Creating project: {project_name}")
        
        endpoint = self.client.build_query_params(accountIdentifier=self.client.config.account_id, orgIdentifier=self.client.config.org_id)
        
        payload = {
            "project": {
                "orgIdentifier": self.client.config.org_id,
                "identifier": project_id,
                "name": project_name,
                "color": "#0063F7",
                "modules": ["CD"],
                "description": description,
                "tags": tags
            }
        }
        
        try:
            result = self.client.post(f"/ng/api/projects?{endpoint}", payload)
            logger.info(f"✓ Project created: {project_name}")
            
            return ResourceResult(
                resource_type="project",
                identifier=project_id,
                name=project_name,
                success=True,
                data={"status": "created"}
            )
        except Exception as e:
            # Check if it's a 409 conflict (already exists)
            if "409" in str(e) or "already exists" in str(e).lower():
                logger.info(f"✓ Project already exists: {project_name} (using existing)")
                return ResourceResult(
                    resource_type="project",
                    identifier=project_id,
                    name=project_name,
                    success=True,
                    data={"status": "existing"}
                )
            
            logger.error(f"✗ Failed to create project: {e}")
            return ResourceResult(
                resource_type="project",
                identifier=project_id,
                name=project_name,
                success=False,
                error=str(e)
            )
    
    def create_environment(self, config: Dict) -> ResourceResult:
        """
        Create environment
        
        Args:
            config: Environment configuration
            
        Returns:
            ResourceResult object
        """
        name = config.get("name")
        identifier = config.get("identifier")
        description = config.get("description", "")
        env_type = config.get("type", "PreProduction")
        
        logger.info(f"Creating environment: {name}")
        
        # Build environment YAML with proper escaping
        env_yaml = f"""environment:
  name: {name}
  identifier: {identifier}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  description: {description if description else '""'}
  type: {env_type}
  tags: {json.dumps(config.get("tags", {}))}
"""
        
        # Add variables if present
        if "variables" in config and config["variables"]:
            env_yaml += "  variables:\n"
            for var in config["variables"]:
                env_yaml += f"    - name: {var['name']}\n"
                env_yaml += f"      value: \"{var['value']}\"\n"
                env_yaml += f"      type: {var.get('type', 'String')}\n"
        
        endpoint = self.client.build_endpoint(
            "/ng/api/environmentsV2",
            project_id=self.project_id
        )
        
        # Wrap YAML in JSON payload
        payload = {
            "identifier": identifier,
            "orgIdentifier": self.client.config.org_id,
            "projectIdentifier": self.project_id,
            "name": name,
            "description": description,
            "type": env_type,
            "tags": config.get("tags", {}),
            "yaml": env_yaml
        }
        
        logger.debug(f"Environment YAML:\n{env_yaml}")
        
        try:
            result = self.client.post(endpoint, payload)
            
            if result.get("status") == "already_exists":
                logger.info(f"✓ Environment already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="environment",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing"}
                )
            
            logger.info(f"✓ Environment created: {name}")
            
            return ResourceResult(
                resource_type="environment",
                identifier=identifier,
                name=name,
                success=True,
                data={"status": "created"}
            )
        except Exception as e:
            if "409" in str(e) or "already exists" in str(e).lower():
                logger.info(f"✓ Environment already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="environment",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing"}
                )
            
            logger.error(f"✗ Failed to create environment {name}: {e}")
            return ResourceResult(
                resource_type="environment",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
    
    def create_infrastructure(self, config: Dict) -> ResourceResult:
        """
        Create infrastructure definition
        
        Args:
            config: Infrastructure configuration
            
        Returns:
            ResourceResult object
        """
        name = config.get("name")
        identifier = config.get("identifier")
        description = config.get("description", "")
        env_ref = config.get("environment_ref")
        infra_type = config.get("type", "KubernetesDirect")
        deployment_type = config.get("deployment_type", "Kubernetes")
        
        logger.info(f"Creating infrastructure: {name}")
        
        # Get infrastructure configuration
        infra_config = config.get("config", {})
        connector_ref = infra_config.get("connector_ref", "<+input>")
        namespace = infra_config.get("namespace", f"{self.project_id}-{env_ref}")
        release_name = infra_config.get("release_name", "release-<+INFRA_KEY>")
        allow_simultaneous = infra_config.get("allow_simultaneous", False)
        
        # Build infrastructure YAML
        infra_yaml = f"""infrastructureDefinition:
  name: {name}
  identifier: {identifier}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  environmentRef: {env_ref}
  deploymentType: {deployment_type}
  type: {infra_type}
  spec:
    connectorRef: {connector_ref}
    namespace: {namespace}
    releaseName: {release_name}
  allowSimultaneousDeployments: {str(allow_simultaneous).lower()}
"""
        
        endpoint = self.client.build_endpoint(
            "/ng/api/infrastructures",
            project_id=self.project_id,
            environmentIdentifier=env_ref
        )
        
        # Wrap YAML in JSON payload
        payload = {
            "identifier": identifier,
            "orgIdentifier": self.client.config.org_id,
            "projectIdentifier": self.project_id,
            "environmentRef": env_ref,
            "name": name,
            "description": description,
            "tags": config.get("tags", {}),
            "type": infra_type,
            "yaml": infra_yaml
        }
        
        try:
            result = self.client.post(endpoint, payload)
            
            if result.get("status") == "already_exists":
                logger.info(f"✓ Infrastructure already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="infrastructure",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing"}
                )
            
            logger.info(f"✓ Infrastructure created: {name}")
            
            return ResourceResult(
                resource_type="infrastructure",
                identifier=identifier,
                name=name,
                success=True,
                data={"status": "created"}
            )
        except Exception as e:
            if "409" in str(e) or "already exists" in str(e).lower():
                logger.info(f"✓ Infrastructure already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="infrastructure",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing"}
                )
            
            logger.error(f"✗ Failed to create infrastructure {name}: {e}")
            return ResourceResult(
                resource_type="infrastructure",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
    
    def create_service(self, config: Dict) -> ResourceResult:
        """
        Create service
        
        Args:
            config: Service configuration
            
        Returns:
            ResourceResult object
        """
        name = config.get("name")
        identifier = config.get("identifier")
        description = config.get("description", "")
        service_type = config.get("type", "Kubernetes")
        
        logger.info(f"Creating service: {name}")
        
        # Build service YAML
        service_yaml = f"""service:
  name: {name}
  identifier: {identifier}
  orgIdentifier: {self.client.config.org_id}
  projectIdentifier: {self.project_id}
  description: {description}
  tags: {json.dumps(config.get('tags', {}))}
  serviceDefinition:
    type: {service_type}
    spec:
"""
        
        # Add manifests section
        service_config = config.get("config", {})
        if "manifests" in service_config:
            service_yaml += "      manifests:\n"
            for manifest in service_config["manifests"]:
                service_yaml += f"        - manifest:\n"
                service_yaml += f"            identifier: {manifest.get('identifier', 'k8s_manifests')}\n"
                service_yaml += f"            type: {manifest.get('type', 'K8sManifest')}\n"
                service_yaml += f"            spec:\n"
                service_yaml += f"              store:\n"
                service_yaml += f"                type: Github\n"
                service_yaml += f"                spec:\n"
                service_yaml += f"                  connectorRef: {manifest.get('connector_ref', '<+input>')}\n"
                service_yaml += f"                  gitFetchType: Branch\n"
                
                if "git_details" in manifest:
                    git_details = manifest["git_details"]
                    service_yaml += f"                  branch: {git_details.get('branch', 'main')}\n"
                    service_yaml += f"                  paths:\n"
                    for path in git_details.get("paths", ["k8s/"]):
                        service_yaml += f"                    - {path}\n"
                
                service_yaml += f"              skipResourceVersioning: false\n"
        
        # Add artifacts section
        if "artifacts" in service_config:
            service_yaml += "      artifacts:\n"
            service_yaml += "        primary:\n"
            service_yaml += "          primaryArtifactRef: <+input>\n"
            service_yaml += "          sources:\n"
            
            for artifact in service_config["artifacts"]:
                service_yaml += f"            - identifier: {artifact.get('identifier', 'docker_image')}\n"
                service_yaml += f"              type: {artifact.get('type', 'DockerRegistry')}\n"
                service_yaml += f"              spec:\n"
                service_yaml += f"                connectorRef: {artifact.get('connector_ref', '<+input>')}\n"
                service_yaml += f"                imagePath: {artifact.get('image_path', '<+input>')}\n"
                service_yaml += f"                tag: <+input>\n"
        
        endpoint = self.client.build_endpoint("/ng/api/servicesV2")
        
        # Wrap YAML in JSON payload  
        payload = {
            "identifier": identifier,
            "orgIdentifier": self.client.config.org_id,
            "projectIdentifier": self.project_id,
            "name": name,
            "description": description,
            "tags": config.get("tags", {}),
            "yaml": service_yaml
        }
        
        try:
            result = self.client.post(endpoint, payload)
            
            if result.get("status") == "already_exists":
                logger.info(f"✓ Service already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="service",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing"}
                )
            
            logger.info(f"✓ Service created: {name}")
            
            return ResourceResult(
                resource_type="service",
                identifier=identifier,
                name=name,
                success=True,
                data={"status": "created"}
            )
        except Exception as e:
            if "409" in str(e) or "already exists" in str(e).lower():
                logger.info(f"✓ Service already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="service",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={"status": "existing"}
                )
            
            logger.error(f"✗ Failed to create service {name}: {e}")
            return ResourceResult(
                resource_type="service",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
    
    def create_resources_from_config(self, config: Dict) -> Dict[str, List[ResourceResult]]:
        """
        Create all resources from configuration
        
        Args:
            config: Full configuration with environments, infrastructures, services
            
        Returns:
            Dictionary mapping resource types to lists of results
        """
        results = {
            "environments": [],
            "infrastructures": [],
            "services": []
        }
        
        # Create environments
        if "environments" in config:
            logger.info(f"\n{'=' * 80}\nCreating Environments\n{'=' * 80}")
            for env_config in config["environments"]:
                result = self.create_environment(env_config)
                results["environments"].append(result)
        
        # Create infrastructures
        if "infrastructures" in config:
            logger.info(f"\n{'=' * 80}\nCreating Infrastructures\n{'=' * 80}")
            for infra_config in config["infrastructures"]:
                result = self.create_infrastructure(infra_config)
                results["infrastructures"].append(result)
        
        # Create services
        if "services" in config:
            logger.info(f"\n{'=' * 80}\nCreating Services\n{'=' * 80}")
            for service_config in config["services"]:
                result = self.create_service(service_config)
                results["services"].append(result)
        
        return results
