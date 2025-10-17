#!/usr/bin/env python3
"""
Harness Automation Script
Automates the creation of applications, pipelines, and RBAC setup in Harness
"""

import os
import sys
import json
import yaml
import argparse
import requests
from typing import Dict, List, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HarnessAutomation:
    """Main class for Harness automation operations"""
    
    def __init__(self, account_id: str, api_key: str, org_id: str, base_url: str = "https://app.harness.io"):
        self.account_id = account_id
        self.api_key = api_key
        self.org_id = org_id
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Harness API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise
    
    def create_project(self, project_name: str, project_identifier: str, description: str = "") -> Dict:
        """Create a new Harness project"""
        logger.info(f"Creating project: {project_name}")
        
        endpoint = f"/ng/api/projects?accountIdentifier={self.account_id}&orgIdentifier={self.org_id}"
        
        payload = {
            "project": {
                "orgIdentifier": self.org_id,
                "identifier": project_identifier,
                "name": project_name,
                "color": "#0063F7",
                "description": description,
                "tags": {
                    "automation": "true",
                    "created_date": datetime.now().isoformat()
                }
            }
        }
        
        try:
            result = self._make_request("POST", endpoint, payload)
            logger.info(f"✓ Project created successfully: {project_name}")
            return result
        except Exception as e:
            logger.error(f"✗ Failed to create project: {e}")
            raise
    
    def create_service(self, project_id: str, service_name: str, service_type: str = "Kubernetes") -> Dict:
        """Create a Harness service"""
        logger.info(f"Creating service: {service_name}")
        
        endpoint = (f"/ng/api/servicesV2?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}&"
                   f"projectIdentifier={project_id}")
        
        service_identifier = service_name.lower().replace("-", "_").replace(" ", "_")
        
        payload = {
            "identifier": service_identifier,
            "orgIdentifier": self.org_id,
            "projectIdentifier": project_id,
            "name": service_name,
            "description": f"Service for {service_name}",
            "tags": {
                "automation": "true"
            },
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
            logger.info(f"✓ Service created successfully: {service_name}")
            return result
        except Exception as e:
            logger.error(f"✗ Failed to create service: {e}")
            raise
    
    def create_environment(self, project_id: str, env_name: str, env_type: str = "PreProduction") -> Dict:
        """Create a Harness environment"""
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
            "tags": {
                "automation": "true",
                "environment": env_name.lower()
            },
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
            logger.info(f"✓ Environment created successfully: {env_name}")
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
            "tags": {
                "automation": "true"
            },
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
            logger.info(f"✓ Infrastructure created successfully: {infra_name}")
            return result
        except Exception as e:
            logger.error(f"✗ Failed to create infrastructure: {e}")
            raise
    
    def create_pipeline_from_template(self, project_id: str, template_path: str, 
                                     replacements: Dict[str, str]) -> Dict:
        """Create pipeline from template file"""
        logger.info(f"Creating pipeline from template: {template_path}")
        
        # Read template
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Replace placeholders (without angle brackets)
        for key, value in replacements.items():
            template_content = template_content.replace(key, str(value))
        
        # Parse YAML
        pipeline_yaml = yaml.safe_load(template_content)
        
        # Validate pipeline structure
        if 'pipeline' not in pipeline_yaml:
            raise ValueError("Invalid pipeline template: missing 'pipeline' key")
        
        # Use correct pipeline API endpoint (not /ng/api)
        endpoint = (f"/pipeline/api/pipelines/v2?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}&"
                   f"projectIdentifier={project_id}")
        
        # Convert YAML to string for API (Harness expects direct YAML)
        pipeline_yaml_str = yaml.dump(pipeline_yaml, default_flow_style=False, sort_keys=False)
        
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Content-Type": "application/yaml",
                "x-api-key": self.api_key
            }
            
            # Send YAML directly in body
            response = requests.post(url, headers=headers, data=pipeline_yaml_str)
            response.raise_for_status()
            
            logger.info(f"✓ Pipeline created successfully: {pipeline_yaml['pipeline']['name']}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to create pipeline: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise
    
    def create_user_group(self, project_id: str, group_name: str, group_id: str, 
                         description: str, users: List[str] = None) -> Dict:
        """Create a user group"""
        logger.info(f"Creating user group: {group_name}")
        
        endpoint = (f"/ng/api/user-groups?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}&"
                   f"projectIdentifier={project_id}")
        
        payload = {
            "identifier": group_id,
            "name": group_name,
            "description": description,
            "tags": {
                "automation": "true"
            },
            "users": users or [],
            "notificationConfigs": []
        }
        
        try:
            result = self._make_request("POST", endpoint, payload)
            logger.info(f"✓ User group created successfully: {group_name}")
            return result
        except Exception as e:
            logger.error(f"✗ Failed to create user group: {e}")
            raise
    
    def create_resource_group(self, project_id: str, rg_name: str, rg_id: str,
                             resources: List[Dict]) -> Dict:
        """Create a resource group"""
        logger.info(f"Creating resource group: {rg_name}")
        
        endpoint = (f"/ng/api/resourcegroup?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}&"
                   f"projectIdentifier={project_id}")
        
        payload = {
            "resourceGroup": {
                "identifier": rg_id,
                "name": rg_name,
                "description": f"Resource group for {rg_name}",
                "tags": {
                    "automation": "true"
                },
                "allowedScopeLevels": ["project"],
                "includedScopes": [
                    {
                        "filter": "INCLUDING_CHILD_SCOPES",
                        "accountIdentifier": self.account_id,
                        "orgIdentifier": self.org_id,
                        "projectIdentifier": project_id
                    }
                ],
                "resourceFilter": {
                    "includeAllResources": False,
                    "resources": resources
                }
            }
        }
        
        try:
            result = self._make_request("POST", endpoint, payload)
            logger.info(f"✓ Resource group created successfully: {rg_name}")
            return result
        except Exception as e:
            logger.error(f"✗ Failed to create resource group: {e}")
            raise
    
    def create_role(self, project_id: str, role_name: str, role_id: str,
                   permissions: List[str]) -> Dict:
        """Create a custom role"""
        logger.info(f"Creating role: {role_name}")
        
        endpoint = (f"/ng/api/roles?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}&"
                   f"projectIdentifier={project_id}")
        
        payload = {
            "role": {
                "identifier": role_id,
                "name": role_name,
                "description": f"Custom role for {role_name}",
                "tags": {
                    "automation": "true"
                },
                "permissions": permissions,
                "allowedScopeLevels": ["project"]
            }
        }
        
        try:
            result = self._make_request("POST", endpoint, payload)
            logger.info(f"✓ Role created successfully: {role_name}")
            return result
        except Exception as e:
            logger.error(f"✗ Failed to create role: {e}")
            raise
    
    def create_role_assignment(self, project_id: str, resource_group_id: str,
                              role_id: str, user_group_ids: List[str]) -> Dict:
        """Create role assignment (bind role to user groups for resource group)"""
        logger.info(f"Creating role assignment for resource group: {resource_group_id}")
        
        endpoint = (f"/ng/api/roleassignments?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}&"
                   f"projectIdentifier={project_id}")
        
        for user_group_id in user_group_ids:
            payload = {
                "roleAssignment": {
                    "resourceGroupIdentifier": resource_group_id,
                    "roleIdentifier": role_id,
                    "principal": {
                        "type": "USER_GROUP",
                        "identifier": user_group_id,
                        "scopeLevel": "project"
                    },
                    "disabled": False,
                    "managed": False
                }
            }
            
            try:
                result = self._make_request("POST", endpoint, payload)
                logger.info(f"✓ Role assignment created for user group: {user_group_id}")
            except Exception as e:
                logger.error(f"✗ Failed to create role assignment: {e}")
                raise
        
        return {"status": "success"}
    
    def setup_full_project(self, config: Dict) -> Dict:
        """Complete project setup with all resources"""
        logger.info("=" * 80)
        logger.info("Starting Full Project Setup")
        logger.info("=" * 80)
        
        results = {}
        
        try:
            # 1. Create Project
            logger.info("\n1. Creating Project...")
            project_result = self.create_project(
                project_name=config['project_name'],
                project_identifier=config['project_identifier'],
                description=config.get('description', '')
            )
            results['project'] = project_result
            
            # 2. Create Service
            logger.info("\n2. Creating Service...")
            service_result = self.create_service(
                project_id=config['project_identifier'],
                service_name=f"{config['project_name']} Service"
            )
            results['service'] = service_result
            
            # 3. Create Environments
            logger.info("\n3. Creating Environments...")
            staging_env = self.create_environment(
                project_id=config['project_identifier'],
                env_name="staging",
                env_type="PreProduction"
            )
            prod_env = self.create_environment(
                project_id=config['project_identifier'],
                env_name="production",
                env_type="Production"
            )
            results['environments'] = {'staging': staging_env, 'production': prod_env}
            
            # 4. Create Infrastructures
            logger.info("\n4. Creating Infrastructures...")
            staging_infra = self.create_infrastructure(
                project_id=config['project_identifier'],
                env_id="staging",
                infra_name="staging_infra",
                connector_ref=config.get('cluster_connector', '<+input>'),
                namespace=f"{config['project_name']}-staging"
            )
            prod_infra = self.create_infrastructure(
                project_id=config['project_identifier'],
                env_id="production",
                infra_name="prod_infra_primary",
                connector_ref=config.get('cluster_connector', '<+input>'),
                namespace=f"{config['project_name']}-prod"
            )
            results['infrastructures'] = {'staging': staging_infra, 'production': prod_infra}
            
            # 5. Create Pipelines
            logger.info("\n5. Creating Pipelines...")
            replacements = {
                'PROJECT_NAME': config['project_name'],
                'PROJECT_IDENTIFIER': config['project_identifier'],
                'ORG_IDENTIFIER': self.org_id,
                'CLUSTER_CONNECTOR_REF': config.get('cluster_connector', '<+input>'),
                'DOCKER_CONNECTOR_REF': config.get('docker_connector', '<+input>'),
                'DOCKER_REGISTRY_CONNECTOR_REF': config.get('docker_registry_connector', '<+input>'),
                'DOCKER_REGISTRY': config.get('docker_registry', 'docker.io'),
                'GIT_CONNECTOR_REF': config.get('git_connector', '<+input>'),
                'REPO_NAME': config.get('repo_name', config['project_name']),
                'SLACK_WEBHOOK_URL': config.get('slack_webhook', '<+input>')
            }
            
            nonprod_pipeline = self.create_pipeline_from_template(
                project_id=config['project_identifier'],
                template_path=config['nonprod_template_path'],
                replacements=replacements
            )
            prod_pipeline = self.create_pipeline_from_template(
                project_id=config['project_identifier'],
                template_path=config['prod_template_path'],
                replacements=replacements
            )
            results['pipelines'] = {'nonprod': nonprod_pipeline, 'prod': prod_pipeline}
            
            # 6. Setup RBAC
            logger.info("\n6. Setting up RBAC...")
            rbac_results = self.setup_rbac(config)
            results['rbac'] = rbac_results
            
            logger.info("\n" + "=" * 80)
            logger.info("✓ Full Project Setup Completed Successfully!")
            logger.info("=" * 80)
            
            return results
            
        except Exception as e:
            logger.error(f"\n✗ Project setup failed: {e}")
            raise
    
    def setup_rbac(self, config: Dict) -> Dict:
        """Setup RBAC (user groups, roles, resource groups, role assignments)"""
        project_id = config['project_identifier']
        project_name = config['project_name']
        
        rbac_results = {}
        
        try:
            # Create User Groups
            logger.info("Creating user groups...")
            developers_group = self.create_user_group(
                project_id=project_id,
                group_name=f"{project_name} Developers",
                group_id=f"{project_id}_developers",
                description="Development team members with staging access",
                users=config.get('developer_users', [])
            )
            
            approvers_group = self.create_user_group(
                project_id=project_id,
                group_name=f"{project_name} Production Approvers",
                group_id=f"{project_id}_prod_approvers",
                description="Team members who can approve production deployments",
                users=config.get('approver_users', [])
            )
            
            operators_group = self.create_user_group(
                project_id=project_id,
                group_name=f"{project_name} Operators",
                group_id=f"{project_id}_operators",
                description="Operations team with full production access",
                users=config.get('operator_users', [])
            )
            
            rbac_results['user_groups'] = {
                'developers': developers_group,
                'approvers': approvers_group,
                'operators': operators_group
            }
            
            # Create Resource Groups
            logger.info("Creating resource groups...")
            staging_resources = [
                {"resourceType": "ENVIRONMENT", "identifiers": ["staging"]},
                {"resourceType": "PIPELINE", "identifiers": [f"{project_id}_nonprod_pipeline"]}
            ]
            
            prod_resources = [
                {"resourceType": "ENVIRONMENT", "identifiers": ["production"]},
                {"resourceType": "PIPELINE", "identifiers": [f"{project_id}_prod_pipeline"]}
            ]
            
            staging_rg = self.create_resource_group(
                project_id=project_id,
                rg_name=f"{project_name} Staging Resources",
                rg_id=f"{project_id}_staging_resources",
                resources=staging_resources
            )
            
            prod_rg = self.create_resource_group(
                project_id=project_id,
                rg_name=f"{project_name} Production Resources",
                rg_id=f"{project_id}_prod_resources",
                resources=prod_resources
            )
            
            rbac_results['resource_groups'] = {
                'staging': staging_rg,
                'production': prod_rg
            }
            
            logger.info("✓ RBAC setup completed successfully")
            
            return rbac_results
            
        except Exception as e:
            logger.error(f"✗ RBAC setup failed: {e}")
            raise


def parse_repository_name(repo_name: str) -> Dict[str, str]:
    """
    Parse repository name to extract project information
    Expected format: <org>-<project>-<service>
    Example: sfdc-customer-portal-backend
    """
    parts = repo_name.split('-')
    
    if len(parts) < 2:
        raise ValueError(f"Invalid repository name format: {repo_name}")
    
    # Create project identifier (lowercase, underscores)
    project_identifier = repo_name.lower().replace('-', '_')
    
    return {
        'project_name': repo_name,
        'project_identifier': project_identifier,
        'repository': repo_name
    }


def load_config_from_file(config_path: str) -> Dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration file: {e}")
        raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Harness Automation Setup')
    parser.add_argument('--config-file', help='Path to YAML configuration file')
    parser.add_argument('--account-id', help='Harness Account ID')
    parser.add_argument('--api-key', help='Harness API Key')
    parser.add_argument('--org-id', help='Harness Organization ID')
    parser.add_argument('--repo-name', help='Repository name (for project creation)')
    parser.add_argument('--nonprod-template', help='Path to non-prod pipeline template')
    parser.add_argument('--prod-template', help='Path to prod pipeline template')
    parser.add_argument('--description', default='', help='Project description')
    parser.add_argument('--cluster-connector', default='<+input>', help='Kubernetes cluster connector ref')
    parser.add_argument('--docker-connector', default='<+input>', help='Docker connector ref')
    parser.add_argument('--docker-registry-connector', default='<+input>', help='Docker registry connector ref')
    parser.add_argument('--docker-registry', default='docker.io', help='Docker registry URL')
    parser.add_argument('--git-connector', default='<+input>', help='Git connector ref')
    parser.add_argument('--developer-users', nargs='*', default=[], help='Developer user emails')
    parser.add_argument('--approver-users', nargs='*', default=[], help='Approver user emails')
    parser.add_argument('--operator-users', nargs='*', default=[], help='Operator user emails')
    parser.add_argument('--slack-webhook', default='<+input>', help='Slack webhook URL')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no actual API calls)')
    
    args = parser.parse_args()
    
    # Load from config file if provided
    if args.config_file:
        file_config = load_config_from_file(args.config_file)
        
        # Use command-line args to override file config
        args.account_id = args.account_id or file_config['harness']['account_id']
        args.api_key = args.api_key or file_config['harness']['api_key']
        args.org_id = args.org_id or file_config['harness']['org_id']
        args.repo_name = args.repo_name or file_config['project']['repo_name']
        args.description = args.description or file_config['project'].get('description', '')
        
        # Connectors from file
        connectors = file_config.get('connectors', {})
        args.cluster_connector = args.cluster_connector or connectors.get('cluster_connector', '<+input>')
        args.docker_connector = args.docker_connector or connectors.get('docker_connector', '<+input>')
        args.docker_registry_connector = args.docker_registry_connector or connectors.get('docker_registry_connector', '<+input>')
        args.docker_registry = args.docker_registry or connectors.get('docker_registry', 'docker.io')
        args.git_connector = args.git_connector or connectors.get('git_connector', '<+input>')
        
        # Users from file
        users = file_config.get('users', {})
        if not args.developer_users:
            args.developer_users = users.get('developers', [])
        if not args.approver_users:
            args.approver_users = users.get('approvers', [])
        if not args.operator_users:
            args.operator_users = users.get('operators', [])
        
        # Notifications from file
        notifications = file_config.get('notifications', {})
        args.slack_webhook = args.slack_webhook or notifications.get('slack_webhook', '<+input>')
        
        # Set template paths if not provided
        if not args.nonprod_template:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            args.nonprod_template = os.path.join(os.path.dirname(script_dir), 'templates', 'pipeline-template-nonprod.yaml')
        if not args.prod_template:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            args.prod_template = os.path.join(os.path.dirname(script_dir), 'templates', 'pipeline-template-prod.yaml')
    
    # Validate required arguments
    required = ['account_id', 'api_key', 'org_id', 'repo_name']
    missing = [arg for arg in required if not getattr(args, arg, None)]
    if missing:
        logger.error(f"Missing required arguments: {', '.join(missing)}")
        parser.print_help()
        sys.exit(1)
    
    try:
        # Parse repository name
        project_info = parse_repository_name(args.repo_name)
        
        logger.info(f"Project Name: {project_info['project_name']}")
        logger.info(f"Project Identifier: {project_info['project_identifier']}")
        
        if args.dry_run:
            logger.info("DRY RUN MODE - No actual API calls will be made")
            return
        
        # Initialize automation
        automation = HarnessAutomation(
            account_id=args.account_id,
            api_key=args.api_key,
            org_id=args.org_id
        )
        
        # Prepare configuration
        config = {
            'project_name': project_info['project_name'],
            'project_identifier': project_info['project_identifier'],
            'description': args.description,
            'nonprod_template_path': args.nonprod_template,
            'prod_template_path': args.prod_template,
            'cluster_connector': args.cluster_connector,
            'docker_connector': args.docker_connector,
            'docker_registry_connector': args.docker_registry_connector,
            'docker_registry': args.docker_registry,
            'git_connector': args.git_connector,
            'repo_name': project_info['repository'],
            'developer_users': args.developer_users,
            'approver_users': args.approver_users,
            'operator_users': args.operator_users,
            'slack_webhook': args.slack_webhook
        }
        
        # Run full project setup
        results = automation.setup_full_project(config)
        
        # Save results to file
        output_file = f"harness_setup_results_{project_info['project_identifier']}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✓ Setup results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"\n✗ Automation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
