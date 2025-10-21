"""
Configuration validators for Harness resources
Validates configurations before API calls
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Validation error exception"""
    pass


class ConfigValidator:
    """Validates Harness resource configurations"""
    
    # Harness identifier rules
    IDENTIFIER_PATTERN = r'^[a-zA-Z0-9_][a-zA-Z0-9_-]{0,127}$'
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    @staticmethod
    def validate_identifier(identifier: str, resource_type: str = "resource") -> bool:
        """
        Validate Harness identifier format
        Rules: Start with alphanumeric or underscore, max 128 chars, alphanumeric/underscore/hyphen
        """
        if not identifier:
            raise ValidationError(f"{resource_type} identifier cannot be empty")
        
        if not re.match(ConfigValidator.IDENTIFIER_PATTERN, identifier):
            raise ValidationError(
                f"Invalid {resource_type} identifier '{identifier}'. "
                f"Must start with alphanumeric/underscore, max 128 chars, "
                f"only alphanumeric, underscore, and hyphen allowed"
            )
        
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not re.match(ConfigValidator.EMAIL_PATTERN, email):
            raise ValidationError(f"Invalid email format: {email}")
        return True
    
    @staticmethod
    def validate_required_fields(config: Dict, required_fields: List[str], resource_type: str) -> bool:
        """Validate that required fields are present"""
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ValidationError(
                f"{resource_type} missing required fields: {', '.join(missing_fields)}"
            )
        
        return True
    
    @classmethod
    def validate_project_config(cls, config: Dict) -> List[str]:
        """Validate project configuration"""
        errors = []
        
        try:
            cls.validate_required_fields(config, ["repo_name"], "Project")
            
            # Validate identifier
            identifier = config["repo_name"].lower().replace('-', '_').replace(' ', '_')
            cls.validate_identifier(identifier, "Project")
            
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @classmethod
    def validate_connector_config(cls, config: Dict) -> List[str]:
        """Validate connector configuration"""
        errors = []
        
        try:
            cls.validate_required_fields(config, ["name", "identifier"], "Connector")
            cls.validate_identifier(config["identifier"], "Connector")
            
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @classmethod
    def validate_environment_config(cls, config: Dict) -> List[str]:
        """Validate environment configuration"""
        errors = []
        
        try:
            cls.validate_required_fields(config, ["name", "identifier"], "Environment")
            cls.validate_identifier(config["identifier"], "Environment")
            
            # Validate environment type
            if "type" in config and config["type"] not in ["Production", "PreProduction"]:
                errors.append(f"Invalid environment type: {config['type']}. Must be 'Production' or 'PreProduction'")
            
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @classmethod
    def validate_infrastructure_config(cls, config: Dict) -> List[str]:
        """Validate infrastructure configuration"""
        errors = []
        
        try:
            cls.validate_required_fields(
                config, 
                ["name", "identifier", "environment_ref"],
                "Infrastructure"
            )
            cls.validate_identifier(config["identifier"], "Infrastructure")
            cls.validate_identifier(config["environment_ref"], "Environment reference")
            
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @classmethod
    def validate_service_config(cls, config: Dict) -> List[str]:
        """Validate service configuration"""
        errors = []
        
        try:
            cls.validate_required_fields(config, ["name", "identifier"], "Service")
            cls.validate_identifier(config["identifier"], "Service")
            
            # Validate service type
            valid_types = ["Kubernetes", "NativeHelm", "ServerlessAwsLambda", "AzureWebApp", "Ssh", "WinRm"]
            if "type" in config and config["type"] not in valid_types:
                errors.append(f"Invalid service type: {config['type']}. Must be one of {valid_types}")
            
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @classmethod
    def validate_user_group_config(cls, config: Dict) -> List[str]:
        """Validate user group configuration"""
        errors = []
        
        try:
            cls.validate_required_fields(config, ["name", "identifier"], "User Group")
            cls.validate_identifier(config["identifier"], "User Group")
            
            # Validate user emails
            if "users" in config:
                for email in config["users"]:
                    try:
                        cls.validate_email(email)
                    except ValidationError as e:
                        errors.append(str(e))
            
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @classmethod
    def validate_service_account_config(cls, config: Dict) -> List[str]:
        """Validate service account configuration"""
        errors = []
        
        try:
            cls.validate_required_fields(config, ["name", "identifier"], "Service Account")
            cls.validate_identifier(config["identifier"], "Service Account")
            
            # Validate email if provided
            if "email" in config and config["email"]:
                try:
                    cls.validate_email(config["email"])
                except ValidationError as e:
                    errors.append(str(e))
            
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @classmethod
    def validate_resource_group_config(cls, config: Dict) -> List[str]:
        """Validate resource group configuration"""
        errors = []
        
        try:
            cls.validate_required_fields(config, ["name", "identifier"], "Resource Group")
            cls.validate_identifier(config["identifier"], "Resource Group")
            
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @classmethod
    def validate_role_config(cls, config: Dict) -> List[str]:
        """Validate role configuration"""
        errors = []
        
        try:
            cls.validate_required_fields(config, ["name", "identifier"], "Role")
            cls.validate_identifier(config["identifier"], "Role")
            
            # Validate permissions structure
            if "permissions" in config:
                if not isinstance(config["permissions"], list):
                    errors.append("Role permissions must be a list")
                else:
                    for perm in config["permissions"]:
                        if "resource_type" not in perm:
                            errors.append("Each permission must have a resource_type")
                        if "actions" not in perm:
                            errors.append("Each permission must have actions")
            
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @classmethod
    def validate_pipeline_config(cls, config: Dict) -> List[str]:
        """Validate pipeline configuration"""
        errors = []
        
        try:
            cls.validate_required_fields(config, ["name", "identifier"], "Pipeline")
            cls.validate_identifier(config["identifier"], "Pipeline")
            
            # If using template, validate template_ref
            if "template_ref" in config and not config["template_ref"]:
                errors.append("template_ref cannot be empty when specified")
            
        except ValidationError as e:
            errors.append(str(e))
        
        return errors
    
    @classmethod
    def validate_full_config(cls, config: Dict) -> Dict[str, List[str]]:
        """
        Validate complete configuration file
        Returns dictionary of resource_type: [errors]
        """
        all_errors = {}
        
        # Validate harness section
        if "harness" not in config:
            all_errors["harness"] = ["Missing 'harness' section"]
        else:
            harness_errors = []
            required = ["account_id", "api_key", "org_id"]
            for field in required:
                if field not in config["harness"]:
                    harness_errors.append(f"Missing required field: {field}")
            if harness_errors:
                all_errors["harness"] = harness_errors
        
        # Validate project section
        if "project" not in config:
            all_errors["project"] = ["Missing 'project' section"]
        else:
            project_errors = cls.validate_project_config(config["project"])
            if project_errors:
                all_errors["project"] = project_errors
        
        # Validate connectors
        if "connectors" in config:
            for conn_type, connectors in config["connectors"].items():
                if isinstance(connectors, list):
                    for i, conn in enumerate(connectors):
                        conn_errors = cls.validate_connector_config(conn)
                        if conn_errors:
                            all_errors[f"connectors.{conn_type}[{i}]"] = conn_errors
        
        # Validate environments
        if "environments" in config:
            for i, env in enumerate(config["environments"]):
                env_errors = cls.validate_environment_config(env)
                if env_errors:
                    all_errors[f"environments[{i}]"] = env_errors
        
        # Validate access_control
        if "access_control" in config:
            ac = config["access_control"]
            
            if "user_groups" in ac:
                for i, ug in enumerate(ac["user_groups"]):
                    ug_errors = cls.validate_user_group_config(ug)
                    if ug_errors:
                        all_errors[f"access_control.user_groups[{i}]"] = ug_errors
            
            if "service_accounts" in ac:
                for i, sa in enumerate(ac["service_accounts"]):
                    sa_errors = cls.validate_service_account_config(sa)
                    if sa_errors:
                        all_errors[f"access_control.service_accounts[{i}]"] = sa_errors
        
        return all_errors
