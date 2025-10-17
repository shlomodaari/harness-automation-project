#!/usr/bin/env python3
"""
Harness Automation with Template Entities
Creates org-level pipeline templates, then projects/pipelines that use them
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


class HarnessTemplateAutomation:
    def __init__(self, account_id: str, api_key: str, org_id: str):
        self.account_id = account_id
        self.api_key = api_key
        self.org_id = org_id
        self.base_url = "https://app.harness.io"
    
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
    
    def create_org_level_pipeline_template(self, template_name: str, template_identifier: str,
                                          template_yaml_path: str, replacements: Dict[str, str],
                                          version_label: str = "v1") -> Dict:
        """Create a pipeline template at org level"""
        logger.info(f"Creating org-level template: {template_name}")
        
        # Read and process template
        with open(template_yaml_path, 'r') as f:
            content = f.read()
        
        # Replace placeholders - do compound replacements first!
        # Sort by length descending to replace longer strings first
        sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)
        for key, value in sorted_replacements:
            content = content.replace(key, str(value))
        
        pipeline_yaml = yaml.safe_load(content)
        pipeline_spec = pipeline_yaml['pipeline']
        
        # Remove project-specific fields (templates should be reusable)
        fields_to_remove = ['name', 'identifier', 'projectIdentifier', 'orgIdentifier']
        for field in fields_to_remove:
            if field in pipeline_spec:
                del pipeline_spec[field]
        
        # Create template YAML structure
        template_yaml = {
            'template': {
                'name': template_name,
                'identifier': template_identifier,
                'versionLabel': version_label,
                'type': 'Pipeline',
                'orgIdentifier': self.org_id,
                'tags': {'automation': 'true'},
                'spec': pipeline_spec
            }
        }
        
        template_yaml_str = yaml.dump(template_yaml, default_flow_style=False, sort_keys=False)
        
        endpoint = (f"/template/api/templates?"
                   f"accountIdentifier={self.account_id}&"
                   f"orgIdentifier={self.org_id}")
        
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Content-Type": "application/yaml",
                "x-api-key": self.api_key
            }
            
            # Try to create
            response = requests.post(url, headers=headers, data=template_yaml_str)
            response.raise_for_status()
            
            logger.info(f"✓ Org-level template created: {template_name} (version {version_label})")
            return response.json()
        except requests.exceptions.HTTPError as e:
            # If template already exists, try to update it
            if e.response.status_code == 400 and 'already exists' in e.response.text:
                logger.info(f"⚠ Template already exists, updating: {template_name}")
                try:
                    # Use PUT to update
                    update_endpoint = (f"/template/api/templates/{template_identifier}?"
                                     f"accountIdentifier={self.account_id}&"
                                     f"orgIdentifier={self.org_id}")
                    update_url = f"{self.base_url}{update_endpoint}"
                    response = requests.put(update_url, headers=headers, data=template_yaml_str)
                    response.raise_for_status()
                    logger.info(f"✓ Template updated: {template_name} (version {version_label})")
                    return response.json()
                except Exception as update_error:
                    logger.error(f"✗ Failed to update template: {update_error}")
                    if hasattr(update_error, 'response') and hasattr(update_error.response, 'text'):
                        logger.error(f"Response: {update_error.response.text}")
                    raise
            else:
                logger.error(f"✗ Failed to create template: {e}")
                if hasattr(e, 'response') and hasattr(e.response, 'text'):
                    logger.error(f"Response: {e.response.text}")
                raise
        except Exception as e:
            logger.error(f"✗ Failed to create template: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise
    
    def create_pipeline_from_template(self, project_id: str, pipeline_name: str,
                                     pipeline_identifier: str, template_ref: str,
                                     template_version: str = "v1") -> Dict:
        """Create a pipeline that references an org-level template"""
        logger.info(f"Creating pipeline from template: {pipeline_name}")
        
        # Pipeline YAML that references the template
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


def load_config_from_file(config_path: str) -> Dict:
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description='Harness Automation with Templates')
    parser.add_argument('--config-file', required=True, help='Path to config YAML file')
    parser.add_argument('--create-templates', action='store_true', 
                       help='Create org-level templates (do this once)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config_from_file(args.config_file)
    
    account_id = config['harness']['account_id']
    api_key = config['harness']['api_key']
    org_id = config['harness']['org_id']
    project_name = config['project']['repo_name']
    project_id = project_name.lower().replace('-', '_')
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No actual API calls will be made")
        logger.info(f"Would create templates at org level: {org_id}")
        logger.info(f"Would create project: {project_name}")
        logger.info(f"Would create pipelines referencing templates")
        return
    
    automation = HarnessTemplateAutomation(
        account_id=account_id,
        api_key=api_key,
        org_id=org_id
    )
    
    try:
        results = {}
        template_version = "v1"  # Default version
        
        # Step 1: Create org-level templates (only if --create-templates flag)
        if args.create_templates:
            logger.info("\n" + "=" * 80)
            logger.info("STEP 1: Creating Org-Level Pipeline Templates")
            logger.info("=" * 80)
            
            # Generic replacements for template (no project-specific values)
            # Use <+input> for anything that varies by project
            template_replacements = {
                'PROJECT_NAME': '<+input>',
                'PROJECT_IDENTIFIER': '<+input>',
                'ORG_IDENTIFIER': org_id,
                'CLUSTER_CONNECTOR_REF': '<+input>',
                'DOCKER_CONNECTOR_REF': '<+input>',
                'DOCKER_REGISTRY_CONNECTOR_REF': '<+input>',
                'DOCKER_REGISTRY': 'docker.io',
                'GIT_CONNECTOR_REF': '<+input>',
                'REPO_NAME': '<+input>',
                'SLACK_WEBHOOK_URL': '<+input>',
                'PROJECT_IDENTIFIER_prod_approvers': '<+input>',
                'PROJECT_IDENTIFIER_developers': '<+input>',
                'PROJECT_IDENTIFIER_operators': '<+input>',
                'PROJECT_NAME_service': '<+input>'
            }
            
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(os.path.dirname(script_dir), 'templates')
            
            import time
            template_version = f"v{int(time.time())}"  # Use timestamp for unique version
            logger.info(f"Using version label: {template_version}")
            
            nonprod_template = automation.create_org_level_pipeline_template(
                template_name="NonProd Deployment Pipeline",
                template_identifier="nonprod_deployment_pipeline",
                template_yaml_path=os.path.join(templates_dir, 'pipeline-template-nonprod.yaml'),
                replacements=template_replacements,
                version_label=template_version
            )
            
            prod_template = automation.create_org_level_pipeline_template(
                template_name="Production Deployment Pipeline",
                template_identifier="prod_deployment_pipeline",
                template_yaml_path=os.path.join(templates_dir, 'pipeline-template-prod.yaml'),
                replacements=template_replacements,
                version_label=template_version
            )
            
            results['templates'] = {
                'nonprod': nonprod_template,
                'prod': prod_template
            }
            
            logger.info("\n✓ Org-level templates created successfully!")
            logger.info(f"  - Template: nonprod_deployment_pipeline (org.{org_id})")
            logger.info(f"  - Template: prod_deployment_pipeline (org.{org_id})")
        
        # Step 2: Create project
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: Creating Project")
        logger.info("=" * 80)
        
        project = automation.create_project(
            project_name=project_name,
            project_id=project_id,
            description=config['project'].get('description', '')
        )
        results['project'] = project
        
        # Step 3: Create pipelines from templates
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3: Creating Pipelines from Templates")
        logger.info("=" * 80)
        
        logger.info(f"Using template version for pipelines: {template_version}")
        
        nonprod_pipeline = automation.create_pipeline_from_template(
            project_id=project_id,
            pipeline_name=f"{project_name} NonProd Pipeline",
            pipeline_identifier=f"{project_id}_nonprod_pipeline",
            template_ref="nonprod_deployment_pipeline",
            template_version=template_version
        )
        
        prod_pipeline = automation.create_pipeline_from_template(
            project_id=project_id,
            pipeline_name=f"{project_name} Prod Pipeline",
            pipeline_identifier=f"{project_id}_prod_pipeline",
            template_ref="prod_deployment_pipeline",
            template_version=template_version
        )
        
        results['pipelines'] = {
            'nonprod': nonprod_pipeline,
            'prod': prod_pipeline
        }
        
        # Success summary
        logger.info("\n" + "=" * 80)
        logger.info("✅ SUCCESS - Template-Based Setup Complete!")
        logger.info("=" * 80)
        logger.info(f"\nProject: {project_name}")
        logger.info(f"  ✓ Pipelines created from org-level templates")
        logger.info(f"  ✓ NonProd Pipeline: {project_id}_nonprod_pipeline")
        logger.info(f"  ✓ Prod Pipeline: {project_id}_prod_pipeline")
        logger.info(f"\n📝 Both pipelines reference org-level templates")
        logger.info(f"   - Update the template → all pipelines update!")
        logger.info("=" * 80)
        
        # Save results
        output_file = f"template_setup_results_{project_id}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✓ Results saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"\n✗ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
