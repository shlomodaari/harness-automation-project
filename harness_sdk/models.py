"""
Data models for Harness SDK
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ResourceType(Enum):
    """Harness resource types"""
    PROJECT = "project"
    CONNECTOR = "connector"
    SERVICE = "service"
    ENVIRONMENT = "environment"
    INFRASTRUCTURE = "infrastructure"
    PIPELINE = "pipeline"
    USER_GROUP = "user_group"
    SERVICE_ACCOUNT = "service_account"
    RESOURCE_GROUP = "resource_group"
    ROLE = "role"
    SECRET = "secret"


class ConnectorType(Enum):
    """Connector types based on Harness API"""
    K8S_CLUSTER = "K8sCluster"
    GIT = "Git"
    GITHUB = "Github"
    GITLAB = "Gitlab"
    BITBUCKET = "Bitbucket"
    DOCKER_REGISTRY = "DockerRegistry"
    AWS = "Aws"
    GCP = "Gcp"
    AZURE = "Azure"
    ARTIFACTORY = "Artifactory"
    NEXUS = "Nexus"
    JENKINS = "Jenkins"
    PROMETHEUS = "Prometheus"
    DATADOG = "Datadog"
    NEW_RELIC = "NewRelic"
    SPLUNK = "Splunk"
    PAGERDUTY = "PagerDuty"


@dataclass
class HarnessConfig:
    """Harness account configuration"""
    account_id: str
    api_key: str
    org_id: str = "default"
    base_url: str = "https://app.harness.io"
    
    def __post_init__(self):
        if not self.account_id:
            raise ValueError("account_id is required")
        if not self.api_key:
            raise ValueError("api_key is required")


@dataclass
class ResourceResult:
    """Result of resource creation/operation"""
    resource_type: str
    identifier: str
    name: str
    success: bool
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    warnings: List[str] = field(default_factory=list)
    
    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.resource_type}: {self.name} ({self.identifier})"


@dataclass
class ProjectConfig:
    """Project configuration"""
    repo_name: str
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    color: str = "#0063F7"
    modules: List[str] = field(default_factory=lambda: ["CD", "CI"])
    
    @property
    def identifier(self) -> str:
        """Generate identifier from repo_name"""
        return self.repo_name.lower().replace('-', '_').replace(' ', '_')


@dataclass
class ConnectorConfig:
    """Base connector configuration"""
    name: str
    identifier: str
    type: str
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    delegate_selectors: List[str] = field(default_factory=list)
    spec: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnvironmentConfig:
    """Environment configuration"""
    name: str
    identifier: str
    type: str  # Production, PreProduction
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    variables: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class InfrastructureConfig:
    """Infrastructure configuration"""
    name: str
    identifier: str
    environment_ref: str
    type: str = "KubernetesDirect"
    deployment_type: str = "Kubernetes"
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceConfig:
    """Service configuration"""
    name: str
    identifier: str
    type: str = "Kubernetes"
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserGroupConfig:
    """User group configuration"""
    name: str
    identifier: str
    description: str = ""
    users: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    permissions: Dict[str, Any] = field(default_factory=dict)
    roles: List[str] = field(default_factory=list)
    resource_groups: List[str] = field(default_factory=list)


@dataclass
class ServiceAccountConfig:
    """Service account configuration"""
    name: str
    identifier: str
    description: str = ""
    email: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    permissions: Dict[str, Any] = field(default_factory=dict)
    roles: List[str] = field(default_factory=list)
    create_token: bool = False


@dataclass
class ResourceGroupConfig:
    """Resource group configuration"""
    name: str
    identifier: str
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    included_scopes: List[Dict[str, Any]] = field(default_factory=list)
    include_all_resources: bool = False


@dataclass
class RoleConfig:
    """Custom role configuration"""
    name: str
    identifier: str
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    permissions: List[Dict[str, Any]] = field(default_factory=list)
    allowed_scope_levels: List[str] = field(default_factory=lambda: ["project"])


@dataclass
class PipelineConfig:
    """Pipeline configuration"""
    name: str
    identifier: str
    description: str = ""
    template_ref: Optional[str] = None
    version: str = "v1"
    tags: Dict[str, str] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
