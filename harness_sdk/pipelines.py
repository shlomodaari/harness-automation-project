"""
Pipeline Manager - Manages Harness Pipelines
Based on official Harness API documentation
"""

import yaml
import logging
from typing import Dict, List
from .client import HarnessClient
from .models import ResourceResult

logger = logging.getLogger(__name__)


class PipelineManager:
    """
    Manages Harness pipelines
    Reference: https://apidocs.harness.io/tag/Pipelines
    """
    
    def __init__(self, client: HarnessClient, project_id: str):
        self.client = client
        self.project_id = project_id
    
    def create_pipeline_from_template(self, config: Dict) -> ResourceResult:
        """
        Create pipeline from org-level template
        
        Args:
            config: Pipeline configuration containing:
                - name: Pipeline name
                - identifier: Unique identifier
                - description: Optional description
                - template_ref: Template identifier
                - version: Template version
                - variables: Optional template variables
                
        Returns:
            ResourceResult object
        """
        name = config.get("name")
        identifier = config.get("identifier")
        description = config.get("description", "")
        template_ref = config.get("template_ref")
        version = config.get("version", "v1")
        
        if not template_ref:
            logger.error(f"Pipeline {name} missing template_ref")
            return ResourceResult(
                resource_type="pipeline",
                identifier=identifier,
                name=name,
                success=False,
                error="template_ref is required"
            )
        
        logger.info(f"Creating pipeline from template: {name}")
        logger.info(f"  Template: {template_ref} (version {version})")
        
        # Build pipeline YAML with template reference
        pipeline_dict = {
            'pipeline': {
                'name': name,
                'identifier': identifier,
                'projectIdentifier': self.project_id,
                'orgIdentifier': self.client.config.org_id,
                'description': description,
                'tags': config.get('tags', {'created_from': 'template'}),
                'template': {
                    'templateRef': f'org.{template_ref}',
                    'versionLabel': version
                }
            }
        }
        
        # Add template variables if provided
        if 'variables' in config and config['variables']:
            pipeline_dict['pipeline']['variables'] = []
            for var_name, var_value in config['variables'].items():
                pipeline_dict['pipeline']['variables'].append({
                    'name': var_name,
                    'type': 'String',
                    'value': str(var_value)
                })
        
        pipeline_yaml = yaml.dump(pipeline_dict, default_flow_style=False, sort_keys=False)
        
        endpoint = self.client.build_endpoint(
            "/pipeline/api/pipelines/v2",
            project_id=self.project_id
        )
        
        try:
            result = self.client.post(endpoint, pipeline_yaml, content_type="application/yaml")
            
            if result.get("status") == "already_exists":
                logger.info(f"✓ Pipeline already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="pipeline",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={
                        "template_ref": template_ref,
                        "version": version,
                        "status": "existing"
                    }
                )
            
            logger.info(f"✓ Pipeline created: {name}")
            
            return ResourceResult(
                resource_type="pipeline",
                identifier=identifier,
                name=name,
                success=True,
                data={
                    "template_ref": template_ref,
                    "version": version,
                    "status": "created"
                }
            )
            
        except Exception as e:
            if "409" in str(e) or "already exists" in str(e).lower():
                logger.info(f"✓ Pipeline already exists: {name} (using existing)")
                return ResourceResult(
                    resource_type="pipeline",
                    identifier=identifier,
                    name=name,
                    success=True,
                    data={
                        "template_ref": template_ref,
                        "version": version,
                        "status": "existing"
                    }
                )
            
            logger.error(f"✗ Failed to create pipeline {name}: {e}")
            return ResourceResult(
                resource_type="pipeline",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
    
    def create_pipeline_inline(self, config: Dict) -> ResourceResult:
        """
        Create pipeline with inline definition (not from template)
        
        Args:
            config: Pipeline configuration with inline YAML
            
        Returns:
            ResourceResult object
        """
        name = config.get("name")
        identifier = config.get("identifier")
        pipeline_yaml = config.get("yaml")
        
        if not pipeline_yaml:
            logger.error(f"Pipeline {name} missing yaml definition")
            return ResourceResult(
                resource_type="pipeline",
                identifier=identifier,
                name=name,
                success=False,
                error="yaml definition is required for inline pipelines"
            )
        
        logger.info(f"Creating inline pipeline: {name}")
        
        endpoint = self.client.build_endpoint(
            "/pipeline/api/pipelines/v2",
            project_id=self.project_id
        )
        
        try:
            self.client.post(endpoint, pipeline_yaml, content_type="application/yaml")
            logger.info(f"✓ Pipeline created: {name}")
            
            return ResourceResult(
                resource_type="pipeline",
                identifier=identifier,
                name=name,
                success=True
            )
            
        except Exception as e:
            logger.error(f"✗ Failed to create pipeline {name}: {e}")
            return ResourceResult(
                resource_type="pipeline",
                identifier=identifier,
                name=name,
                success=False,
                error=str(e)
            )
    
    def create_pipelines_from_config(self, pipelines_config: Dict) -> List[ResourceResult]:
        """
        Create all pipelines from configuration
        
        Args:
            pipelines_config: Dictionary of pipeline configurations
            
        Returns:
            List of ResourceResult objects
        """
        results = []
        
        logger.info(f"\n{'=' * 80}\nCreating Pipelines\n{'=' * 80}")
        logger.info(f"Found {len(pipelines_config)} pipeline(s) to create")
        
        for pipeline_key, pipeline_config in pipelines_config.items():
            # Determine if it's a template-based or inline pipeline
            if 'template_ref' in pipeline_config:
                result = self.create_pipeline_from_template(pipeline_config)
            elif 'yaml' in pipeline_config:
                result = self.create_pipeline_inline(pipeline_config)
            else:
                logger.error(f"Pipeline {pipeline_key} must have either template_ref or yaml")
                result = ResourceResult(
                    resource_type="pipeline",
                    identifier=pipeline_config.get("identifier", pipeline_key),
                    name=pipeline_config.get("name", pipeline_key),
                    success=False,
                    error="Must specify either template_ref or yaml"
                )
            
            results.append(result)
        
        # Summary
        success_count = sum(1 for r in results if r.success)
        logger.info(f"\n✓ Created {success_count}/{len(results)} pipeline(s) successfully")
        
        return results
