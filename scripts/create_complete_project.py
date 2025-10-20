#!/usr/bin/env python3
"""
Complete Harness Project Creation with Template References
Creates: Project, Service, Environments, Infrastructures, Pipelines (from templates), User Groups, RBAC
"""

import requests
import yaml
import json
import logging
import argparse
import sys
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HarnessCompleteAutomation:
    def __init__(self, account_id: str, api_key: str, org_id: str, base_url: str = "https://app.harness.io"):
        self.account_id = account_id
        self.api_key = api_key
        self.org_id = org_id
        self.base_url = base_url
    
    def _make_request(self, method: str, endpoint: str, payload: Dict = None, content_type: str = "application/json") -> Dict:
        """Make API request to Harness"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": content_type,
            "x-api-key": self.api_key
        }
        
        if content_type == "application/json":
            response = requests.request(method, url, headers=headers, json=payload)
        else:
            response = requests.request(method, url, headers=headers, data=payload)
        
        response.raise_for_status()
        return response.json()
    
    def create_project(self, project_name: str, project_id: str, description: str = "") -> Dict:
        """Create a project"""
        logger.info(f"Creating project: {project_name}")
        
        endpoint = (f"/ng/api/projects?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}")
        
        payload = {
            "project": {
                "identifier": project_id,
                "name": project_name,
                "description": description,
                "tags": {"automation": "true"},
                "color": "#0063F7",
                "modules": ["CD", "CI"]
            }
        }
        
        try:
            result = self._make_request("POST", endpoint, payload)
            logger.info(f"✓ Project created: {project_name}")
            return result
        except Exception as e:
            logger.error(f"✗ Failed to create project: {e}")
            raise
    
    def create_service(self, project_id: str, service_name: str, service_identifier: str, service_type: str = "Kubernetes") -> Dict:
        """Create service"""
        logger.info(f"Creating service: {service_name}")
        
        endpoint = (f"/ng/api/servicesV2?"
                   f"accountIdentifier={self.account_id}")
        
        payload = {
            "identifier": service_identifier,
            "orgIdentifier": self.org_id,
            "projectIdentifier": project_id,
            "name": service_name,
            "description": f"Service for {service_name}",
            "tags": {"automation": "true"},
            "yaml": f"""service:
  name: {service_name}
  identifier: {service_identifier}
  orgIdentifier: {self.org_id}
  projectIdentifier: {project_id}
  serviceDefinition:
    type: {service_type}
    spec:
      manifests:
        - manifest:
            identifier: k8s_manifests
            type: K8sManifest
            spec:
              store:
                type: Github
                spec:
                  connectorRef: <+input>
                  gitFetchType: Branch
                  branch: main
                  paths:
                    - k8s/
              skipResourceVersioning: false
      artifacts:
        primary:
          primaryArtifactRef: <+input>
          sources:
            - identifier: docker_image
              type: DockerRegistry
              spec:
                connectorRef: <+input>
                imagePath: <+input>
                tag: <+input>
"""
        }
        
        try:
            result = self._make_request("POST", endpoint, payload)
            logger.info(f"✓ Service created: {service_name}")
            return result
        except Exception as e:
            logger.error(f"✗ Failed to create service: {e}")
            raise
    
    def create_environment(self, project_id: str, env_name: str, env_type: str = "PreProduction") -> Dict:
        """Create environment"""
        logger.info(f"Creating environment: {env_name}")
        
        endpoint = (f"/ng/api/environmentsV2?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}&"
                   f"projectIdentifier={project_id}")
        
        env_identifier = env_name.lower().replace("-", "_")
        
        payload = {
            "identifier": env_identifier,
            "orgIdentifier": self.org_id,
            "projectIdentifier": project_id,
            "name": env_name,
            "description": f"{env_name} environment",
            "type": env_type,
            "tags": {"automation": "true", "environment": env_name.lower()},
            "yaml": f"""environment:
  name: {env_name}
  identifier: {env_identifier}
  orgIdentifier: {self.org_id}
  projectIdentifier: {project_id}
  type: {env_type}
  tags:
    environment: {env_name.lower()}
  variables: []
"""
        }
        
        try:
            result = self._make_request("POST", endpoint, payload)
            logger.info(f"✓ Environment created: {env_name}")
            return result
        except Exception as e:
            logger.error(f"✗ Failed to create environment: {e}")
            raise
    
    def create_infrastructure(self, project_id: str, env_id: str, infra_name: str, 
                            connector_ref: str, namespace: str) -> Dict:
        """Create infrastructure definition"""
        logger.info(f"Creating infrastructure: {infra_name}")
        
        endpoint = (f"/ng/api/infrastructures?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}&"
                   f"projectIdentifier={project_id}")
        
        infra_identifier = infra_name.lower().replace("-", "_")
        
        payload = {
            "identifier": infra_identifier,
            "orgIdentifier": self.org_id,
            "projectIdentifier": project_id,
            "environmentRef": env_id,
            "name": infra_name,
            "description": f"Infrastructure for {infra_name}",
            "tags": {"automation": "true"},
            "type": "KubernetesDirect",
            "yaml": f"""infrastructureDefinition:
  name: {infra_name}
  identifier: {infra_identifier}
  orgIdentifier: {self.org_id}
  projectIdentifier: {project_id}
  environmentRef: {env_id}
  deploymentType: Kubernetes
  type: KubernetesDirect
  spec:
    connectorRef: {connector_ref}
    namespace: {namespace}
    releaseName: release-<+INFRA_KEY>
  allowSimultaneousDeployments: false
"""
        }
        
        try:
            result = self._make_request("POST", endpoint, payload)
            logger.info(f"✓ Infrastructure created: {infra_name}")
            return result
        except Exception as e:
            logger.error(f"✗ Failed to create infrastructure: {e}")
            raise
    
    def create_pipeline_from_template(self, project_id: str, pipeline_name: str,
                                     pipeline_identifier: str, template_ref: str,
                                     template_version: str = "v1") -> Dict:
        """Create a pipeline that references an org-level template"""
        logger.info(f"Creating pipeline from template: {pipeline_name}")
        
        pipeline_yaml = {
            'pipeline': {
                'name': pipeline_name,
                'identifier': pipeline_identifier,
                'projectIdentifier': project_id,
                'orgIdentifier': self.org_id,
                'tags': {'created_from': 'template'},
                'template': {
                    'templateRef': f'org.{template_ref}',
                    'versionLabel': template_version
                }
            }
        }
        
        pipeline_yaml_str = yaml.dump(pipeline_yaml, default_flow_style=False, sort_keys=False)
        
        endpoint = (f"/pipeline/api/pipelines/v2?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}&"
                   f"projectIdentifier={project_id}")
        
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Content-Type": "application/yaml",
                "x-api-key": self.api_key
            }
            
            response = requests.post(url, headers=headers, data=pipeline_yaml_str)
            response.raise_for_status()
            
            logger.info(f"✓ Pipeline created from template: {pipeline_name}")
            return response.json()
        except Exception as e:
            logger.error(f"✗ Failed to create pipeline: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise
    
    def create_user_group(self, project_id: str, group_name: str, group_id: str,
                         description: str, users: List[str] = None) -> Dict:
        """Create user group"""
        logger.info(f"Creating user group: {group_name}")
        
        endpoint = (f"/ng/api/user-groups?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}&"
                   f"projectIdentifier={project_id}")
        
        payload = {
            "identifier": group_id,
            "name": group_name,
            "description": description,
            "tags": {"automation": "true"},
            "users": users or [],
            "notificationConfigs": []
        }
        
        try:
            result = self._make_request("POST", endpoint, payload)
            logger.info(f"✓ User group created: {group_name}")
            return result
        except Exception as e:
            logger.error(f"✗ Failed to create user group: {e}")
            raise


def load_config_from_file(config_path: str) -> Dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description='Complete Harness Project Creation')
    parser.add_argument('--config-file', required=True, help='Path to config YAML file')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--create-templates', action='store_true', help='Create org-level templates')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config_from_file(args.config_file)
    
    account_id = config['harness']['account_id']
    api_key = config['harness']['api_key']
    org_id = config['harness']['org_id']
    base_url = config['harness'].get('base_url', "https://app.harness.io")
    project_name = config['project']['repo_name']
    project_id = project_name.lower().replace('-', '_')
    
    if args.dry_run:
        logger.info("DRY RUN MODE")
        logger.info(f"Would create project: {project_name}")
        logger.info(f"Using templates:")
        
        # Check both templates and pipelines sections for compatibility
        # This makes it work with both the old script format and your Jenkins config
        if 'templates' in config:
            logger.info(f"  - NonProd: {config.get('templates', {}).get('nonprod', {}).get('template_ref', 'N/A')}")
            logger.info(f"  - Prod: {config.get('templates', {}).get('prod', {}).get('template_ref', 'N/A')}")
        elif 'pipelines' in config:
            logger.info(f"  - NonProd: {config.get('pipelines', {}).get('nonprod', {}).get('template_ref', 'N/A')}")
            logger.info(f"  - Prod: {config.get('pipelines', {}).get('prod', {}).get('template_ref', 'N/A')}")
        return
    
    automation = HarnessCompleteAutomation(
        account_id=account_id,
        api_key=api_key,
        org_id=org_id,
        base_url=base_url
    )
    
    try:
        results = {}
        
        # Step 1: Create Project
        logger.info("\n" + "=" * 80)
        logger.info("STEP 1: Creating Project")
        logger.info("=" * 80)
        
        project = automation.create_project(
            project_name=project_name,
            project_id=project_id,
            description=config['project'].get('description', '')
        )
        results['project'] = project
        
        # Step 2: Create Service
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: Creating Service")
        logger.info("=" * 80)
        
        service = automation.create_service(
            project_id=project_id,
            service_name=f"{project_name} Service",
            service_identifier=f"{project_id}_service"
        )
        results['service'] = service
        
        # Step 3: Create Environments
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3: Creating Environments")
        logger.info("=" * 80)
        
        staging_env = automation.create_environment(
            project_id=project_id,
            env_name="staging",
            env_type="PreProduction"
        )
        
        prod_env = automation.create_environment(
            project_id=project_id,
            env_name="production",
            env_type="Production"
        )
        results['environments'] = {'staging': staging_env, 'production': prod_env}
        
        # Step 4: Create Infrastructures
        logger.info("\n" + "=" * 80)
        logger.info("STEP 4: Creating Infrastructures")
        logger.info("=" * 80)
        
        staging_infra = automation.create_infrastructure(
            project_id=project_id,
            env_id="staging",
            infra_name="staging_infra",
            connector_ref=config.get('connectors', {}).get('cluster_connector', '<+input>'),
            namespace=f"{project_name}-staging"
        )
        
        prod_infra = automation.create_infrastructure(
            project_id=project_id,
            env_id="production",
            infra_name="prod_infra_primary",
            connector_ref=config.get('connectors', {}).get('cluster_connector', '<+input>'),
            namespace=f"{project_name}-prod"
        )
        results['infrastructures'] = {'staging': staging_infra, 'production': prod_infra}
        
        # Step 5: Create Pipelines from Templates
        logger.info("\n" + "=" * 80)
        logger.info("STEP 5: Creating Pipelines from Templates")
        logger.info("=" * 80)
        
        # FIXED: Check both templates and pipelines sections for backward compatibility
        # This makes it work with both the old script format and the Jenkins config
        if 'pipelines' in config:
            nonprod_template_ref = config.get('pipelines', {}).get('nonprod', {}).get('template_ref', 'nonprod_deployment_pipeline')
            nonprod_version = config.get('pipelines', {}).get('nonprod', {}).get('version', 'v1')
            
            prod_template_ref = config.get('pipelines', {}).get('prod', {}).get('template_ref', 'prod_deployment_pipeline')
            prod_version = config.get('pipelines', {}).get('prod', {}).get('version', 'v1')
        else:
            # Fallback to old format
            nonprod_template_config = config.get('templates', {}).get('nonprod', {})
            prod_template_config = config.get('templates', {}).get('prod', {})
            
            nonprod_template_ref = nonprod_template_config.get('template_ref', 'nonprod_deployment_pipeline')
            nonprod_version = nonprod_template_config.get('version', 'v1')
            
            prod_template_ref = prod_template_config.get('template_ref', 'prod_deployment_pipeline')
            prod_version = prod_template_config.get('version', 'v1')
            
        logger.info(f"Using NonProd Template: {nonprod_template_ref} (version {nonprod_version})")
        logger.info(f"Using Prod Template: {prod_template_ref} (version {prod_version})")
        
        nonprod_pipeline = automation.create_pipeline_from_template(
            project_id=project_id,
            pipeline_name=f"{project_name} NonProd Pipeline",
            pipeline_identifier=f"{project_id}_nonprod_pipeline",
            template_ref=nonprod_template_ref,
            template_version=nonprod_version
        )
        
        prod_pipeline = automation.create_pipeline_from_template(
            project_id=project_id,
            pipeline_name=f"{project_name} Prod Pipeline",
            pipeline_identifier=f"{project_id}_prod_pipeline",
            template_ref=prod_template_ref,
            template_version=prod_version
        )
        results['pipelines'] = {'nonprod': nonprod_pipeline, 'prod': prod_pipeline}
        
        # Step 6: Create User Groups
        if config.get('features', {}).get('create_rbac', True):
            logger.info("\n" + "=" * 80)
            logger.info("STEP 6: Creating User Groups")
            logger.info("=" * 80)
            
            developers_group = automation.create_user_group(
                project_id=project_id,
                group_name=f"{project_name} Developers",
                group_id=f"{project_id}_developers",
                description="Development team members",
                users=config.get('users', {}).get('developers', [])
            )
            
            approvers_group = automation.create_user_group(
                project_id=project_id,
                group_name=f"{project_name} Production Approvers",
                group_id=f"{project_id}_prod_approvers",
                description="Production approvers",
                users=config.get('users', {}).get('approvers', [])
            )
            
            operators_group = automation.create_user_group(
                project_id=project_id,
                group_name=f"{project_name} Operators",
                group_id=f"{project_id}_operators",
                description="Operations team",
                users=config.get('users', {}).get('operators', [])
            )
            
            results['user_groups'] = {
                'developers': developers_group,
                'approvers': approvers_group,
                'operators': operators_group
            }
        
        # Success summary
        logger.info("\n" + "=" * 80)
        logger.info("✅ SUCCESS - Complete Project Setup!")
        logger.info("=" * 80)
        logger.info(f"\nProject: {project_name}")
        logger.info(f"  ✓ Service: {project_id}_service")
        logger.info(f"  ✓ Environments: staging, production")
        logger.info(f"  ✓ Infrastructures: staging_infra, prod_infra_primary")
        logger.info(f"  ✓ Pipelines:")
        logger.info(f"      - NonProd (uses template: {nonprod_template_ref} v{nonprod_version})")
        logger.info(f"      - Prod (uses template: {prod_template_ref} v{prod_version})")
        logger.info(f"  ✓ User Groups: 3")
        logger.info("=" * 80)
        
        # Save results
        output_file = f"complete_setup_results_{project_id}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✓ Results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"\n✗ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
