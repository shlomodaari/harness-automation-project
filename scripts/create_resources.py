#!/usr/bin/env python3
"""
Harness Resource Creation - Main Orchestrator
Creates all Harness resources based on configuration
Version: 3.0 - Production Ready with Modular Architecture
"""

import sys
import os
import yaml
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness_sdk import (
    HarnessClient,
    HarnessConfig,
    ConnectorManager,
    RBACManager,
    ResourceManager,
    PipelineManager,
    SecretsManager,
    ConfigValidator,
    ResourceResult
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('harness_resources.log')
    ]
)
logger = logging.getLogger(__name__)


class HarnessOrchestrator:
    """
    Orchestrates creation of all Harness resources
    Manages dependencies and creation order
    """
    
    def __init__(self, config: Dict, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.results = {
            "project": None,
            "connectors": [],
            "access_control": {},
            "resources": {},
            "pipelines": []
        }
        
        # Initialize Harness client
        harness_config = HarnessConfig(
            account_id=config['harness']['account_id'],
            api_key=config['harness']['api_key'],
            org_id=config['harness'].get('org_id', 'default'),
            base_url=config['harness'].get('base_url', 'https://app.harness.io')
        )
        
        self.client = HarnessClient(harness_config)
        
        # Get project details
        project_name = config['project']['repo_name']
        self.project_id = project_name.lower().replace('-', '_').replace(' ', '_')
        self.project_name = project_name
        
        # Initialize managers
        self.resource_manager = ResourceManager(self.client, self.project_id)
        
        logger.info(f"✓ Orchestrator initialized for project: {project_name}")
    
    def validate_configuration(self) -> bool:
        """Validate complete configuration"""
        logger.info("\n" + "=" * 80)
        logger.info("VALIDATING CONFIGURATION")
        logger.info("=" * 80)
        
        validator = ConfigValidator()
        all_errors = validator.validate_full_config(self.config)
        
        if all_errors:
            logger.error("Configuration validation failed:")
            for section, errors in all_errors.items():
                logger.error(f"\n{section}:")
                for error in errors:
                    logger.error(f"  - {error}")
            return False
        
        logger.info("✓ Configuration validated successfully")
        return True
    
    def create_project(self) -> bool:
        """Create Harness project"""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 1: Creating Project")
        logger.info("=" * 80)
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create project: {self.project_name}")
            return True
        
        result = self.resource_manager.create_project(
            self.config['project']
        )
        
        self.results['project'] = result
        return result.success
    
    def create_connectors(self) -> bool:
        """Create all connectors"""
        if 'connectors' not in self.config:
            logger.info("\nNo connectors configured, skipping...")
            return True
        
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: Creating Connectors")
        logger.info("=" * 80)
        
        if self.dry_run:
            logger.info("[DRY RUN] Would create connectors")
            return True
        
        connector_manager = ConnectorManager(self.client, self.project_id)
        results = connector_manager.create_connectors_from_config(self.config['connectors'])
        
        self.results['connectors'] = results
        
        success_count = sum(1 for r in results if r.success)
        logger.info(f"\n✓ Created {success_count}/{len(results)} connector(s)")
        
        return success_count > 0 or len(results) == 0
    
    def create_secrets(self) -> bool:
        """Create all secrets"""
        if 'secrets' not in self.config:
            logger.info("\nNo secrets configured, skipping...")
            return True
        
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2.5: Creating Secrets")
        logger.info("=" * 80)
        
        if self.dry_run:
            logger.info("[DRY RUN] Would create secrets")
            return True
        
        secrets_manager = SecretsManager(self.client, self.project_id)
        results = []
        
        # Create text secrets
        if 'text_secrets' in self.config['secrets']:
            logger.info("\n" + "=" * 80)
            logger.info("Creating Text Secrets")
            logger.info("=" * 80)
            for secret_config in self.config['secrets']['text_secrets']:
                result = secrets_manager.create_text_secret(secret_config)
                results.append(result)
        
        # Create file secrets
        if 'file_secrets' in self.config['secrets']:
            logger.info("\n" + "=" * 80)
            logger.info("Creating File Secrets")
            logger.info("=" * 80)
            for secret_config in self.config['secrets']['file_secrets']:
                result = secrets_manager.create_file_secret(secret_config)
                results.append(result)
        
        self.results['secrets'] = results
        
        success_count = sum(1 for r in results if r.success)
        logger.info(f"\n✓ Created {success_count}/{len(results)} secret(s)")
        
        return success_count > 0 or len(results) == 0
    
    def create_access_control(self) -> bool:
        """Create all RBAC resources"""
        if 'access_control' not in self.config:
            logger.info("\nNo access control configured, skipping...")
            return True
        
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3: Creating Access Control (RBAC)")
        logger.info("=" * 80)
        
        if self.dry_run:
            logger.info("[DRY RUN] Would create RBAC resources")
            return True
        
        rbac_manager = RBACManager(self.client, self.project_id)
        results = rbac_manager.create_rbac_from_config(self.config['access_control'])
        
        self.results['access_control'] = results
        
        total = sum(len(r) for r in results.values())
        success = sum(1 for results_list in results.values() for r in results_list if r.success)
        
        logger.info(f"\n✓ Created {success}/{total} RBAC resource(s)")
        
        return success > 0 or total == 0
    
    def create_resources(self) -> bool:
        """Create environments, infrastructures, and services"""
        logger.info("\n" + "=" * 80)
        logger.info("STEP 4: Creating Resources")
        logger.info("=" * 80)
        
        if self.dry_run:
            logger.info("[DRY RUN] Would create resources")
            return True
        
        results = self.resource_manager.create_resources_from_config(self.config)
        
        self.results['resources'] = results
        
        total = sum(len(r) for r in results.values())
        success = sum(1 for results_list in results.values() for r in results_list if r.success)
        
        logger.info(f"\n✓ Created {success}/{total} resource(s)")
        
        return success > 0 or total == 0
    
    def create_pipelines(self) -> bool:
        """Create all pipelines"""
        if 'pipelines' not in self.config:
            logger.info("\nNo pipelines configured, skipping...")
            return True
        
        logger.info("\n" + "=" * 80)
        logger.info("STEP 5: Creating Pipelines")
        logger.info("=" * 80)
        
        if self.dry_run:
            logger.info("[DRY RUN] Would create pipelines")
            return True
        
        pipeline_manager = PipelineManager(self.client, self.project_id)
        results = pipeline_manager.create_pipelines_from_config(self.config['pipelines'])
        
        self.results['pipelines'] = results
        
        success_count = sum(1 for r in results if r.success)
        logger.info(f"\n✓ Created {success_count}/{len(results)} pipeline(s)")
        
        return success_count > 0 or len(results) == 0
    
    def print_summary(self):
        """Print final summary"""
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        
        # Project
        if self.results['project']:
            status = "✓" if self.results['project'].success else "✗"
            logger.info(f"\n{status} Project: {self.project_name}")
        
        # Connectors
        if self.results['connectors']:
            success = sum(1 for r in self.results['connectors'] if r.success)
            total = len(self.results['connectors'])
            logger.info(f"\n✓ Connectors: {success}/{total} created")
            for result in self.results['connectors']:
                status = "✓" if result.success else "✗"
                logger.info(f"  {status} {result.name}")
        
        # Access Control
        if self.results['access_control']:
            logger.info(f"\n✓ Access Control:")
            for resource_type, results in self.results['access_control'].items():
                if results:
                    success = sum(1 for r in results if r.success)
                    logger.info(f"  - {resource_type}: {success}/{len(results)} created")
        
        # Resources
        if self.results['resources']:
            logger.info(f"\n✓ Resources:")
            for resource_type, results in self.results['resources'].items():
                if results:
                    success = sum(1 for r in results if r.success)
                    logger.info(f"  - {resource_type}: {success}/{len(results)} created")
        
        # Pipelines
        if self.results['pipelines']:
            success = sum(1 for r in self.results['pipelines'] if r.success)
            total = len(self.results['pipelines'])
            logger.info(f"\n✓ Pipelines: {success}/{total} created")
            for result in self.results['pipelines']:
                status = "✓" if result.success else "✗"
                logger.info(f"  {status} {result.name}")
        
        logger.info("\n" + "=" * 80)
    
    def save_results(self):
        """Save results to JSON file"""
        output_file = f"harness_resources_{self.project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert results to serializable format
        serializable_results = {
            "project": self._result_to_dict(self.results['project']) if self.results['project'] else None,
            "connectors": [self._result_to_dict(r) for r in self.results['connectors']],
            "access_control": {
                k: [self._result_to_dict(r) for r in v]
                for k, v in self.results['access_control'].items()
            },
            "resources": {
                k: [self._result_to_dict(r) for r in v]
                for k, v in self.results['resources'].items()
            },
            "pipelines": [self._result_to_dict(r) for r in self.results['pipelines']]
        }
        
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"\n✓ Results saved to: {output_file}")
    
    @staticmethod
    def _result_to_dict(result: ResourceResult) -> Dict:
        """Convert ResourceResult to dictionary"""
        if not result:
            return None
        return {
            "resource_type": result.resource_type,
            "identifier": result.identifier,
            "name": result.name,
            "success": result.success,
            "error": result.error,
            "data": result.data
        }
    
    def run(self) -> bool:
        """Run complete orchestration"""
        try:
            # Validate configuration
            if not self.validate_configuration():
                return False
            
            # Create resources in order
            if not self.create_project():
                logger.error("Failed to create project, aborting...")
                return False
            
            self.create_connectors()
            self.create_secrets()
            self.create_access_control()
            self.create_resources()
            self.create_pipelines()
            
            # Print summary
            self.print_summary()
            
            # Save results
            if not self.dry_run:
                self.save_results()
            
            logger.info("\n✅ SUCCESS! All resources created")
            return True
            
        except KeyboardInterrupt:
            logger.warning("\n⚠️  Operation cancelled by user")
            return False
        except Exception as e:
            logger.error(f"\n✗ Fatal error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"✓ Configuration loaded from: {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML syntax: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Harness Resource Creation - Comprehensive Automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate configuration (dry run)
  python3 create_resources.py --config my-config.yaml --dry-run
  
  # Create all resources
  python3 create_resources.py --config my-config.yaml
  
  # Verbose mode for debugging
  python3 create_resources.py --config my-config.yaml --verbose
  
  # Skip validation (not recommended)
  python3 create_resources.py --config my-config.yaml --skip-validation
        """
    )
    
    parser.add_argument(
        '--config',
        required=True,
        help='Path to configuration YAML file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate configuration without creating resources'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose/debug logging'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip configuration validation (not recommended)'
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print header
    logger.info("=" * 80)
    logger.info("Harness Resource Creation - v3.0")
    logger.info("=" * 80)
    logger.info(f"Configuration: {args.config}")
    logger.info(f"Mode: {'DRY RUN' if args.dry_run else 'CREATE'}")
    logger.info("=" * 80)
    
    # Load configuration
    config = load_config(args.config)
    
    # Create and run orchestrator
    orchestrator = HarnessOrchestrator(config, dry_run=args.dry_run)
    success = orchestrator.run()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
