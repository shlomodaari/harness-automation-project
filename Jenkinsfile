#!/usr/bin/env groovy

/**
 * Harness Project Automation - Jenkins Pipeline
 * 
 * Complete implementation with project, user groups, environments, services, and pipelines
 */

pipeline {
    agent any
    
    parameters {
        choice(
            name: 'ACTION',
            choices: ['create-project', 'dry-run'],
            description: 'What action to perform'
        )
        string(
            name: 'PROJECT_NAME',
            defaultValue: 'my-new-project',
            description: 'Project name (used for repo_name in config)'
        )
        string(
            name: 'PROJECT_DESCRIPTION',
            defaultValue: 'Automated project creation',
            description: 'Project description'
        )
        string(
            name: 'HARNESS_ACCOUNT_ID',
            defaultValue: '',
            description: 'Harness Account ID'
        )
        password(
            name: 'HARNESS_API_KEY',
            defaultValue: '',
            description: 'Harness API Key'
        )
        string(
            name: 'HARNESS_ORG_ID',
            defaultValue: 'default',
            description: 'Harness Organization ID'
        )
        text(
            name: 'DEVELOPER_EMAILS',
            defaultValue: 'dev@example.com',
            description: 'Developer emails (comma-separated)'
        )
        text(
            name: 'APPROVER_EMAILS',
            defaultValue: 'manager@example.com',
            description: 'Approver emails (comma-separated)'
        )
        text(
            name: 'OPERATOR_EMAILS',
            defaultValue: 'ops@example.com',
            description: 'Operator emails (comma-separated)'
        )
        string(
            name: 'NONPROD_TEMPLATE_REF',
            defaultValue: 'nonprod_deployment_pipeline',
            description: 'NonProd template identifier'
        )
        string(
            name: 'NONPROD_TEMPLATE_VERSION',
            defaultValue: 'v1760729233',
            description: 'NonProd template version'
        )
        string(
            name: 'PROD_TEMPLATE_REF',
            defaultValue: 'prod_deployment_pipeline',
            description: 'Prod template identifier'
        )
        string(
            name: 'PROD_TEMPLATE_VERSION',
            defaultValue: 'v1760729233',
            description: 'Prod template version'
        )
        booleanParam(
            name: 'CREATE_RBAC',
            defaultValue: true,
            description: 'Create RBAC (user groups)'
        )
    }
    
    environment {
        HARNESS_BASE_URL = "https://app.harness.io"
    }
    
    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "🔄 Checking out code..."
                    checkout scm
                }
            }
        }
        
        stage('Generate Configuration') {
            steps {
                script {
                    echo "📝 Generating configuration file..."
                    
                    // Convert comma-separated emails to YAML list format
                    def devEmails = params.DEVELOPER_EMAILS.split(',')
                        .collect { email -> "    - ${email.trim()}" }
                        .join('\n')
                    
                    def approverEmails = params.APPROVER_EMAILS.split(',')
                        .collect { email -> "    - ${email.trim()}" }
                        .join('\n')
                    
                    def operatorEmails = params.OPERATOR_EMAILS.split(',')
                        .collect { email -> "    - ${email.trim()}" }
                        .join('\n')
                    
                    def configContent = """harness:
  account_id: "${params.HARNESS_ACCOUNT_ID}"
  api_key: "${params.HARNESS_API_KEY}"
  org_id: "${params.HARNESS_ORG_ID}"
  base_url: "${HARNESS_BASE_URL}"

project:
  repo_name: "${params.PROJECT_NAME}"
  description: "${params.PROJECT_DESCRIPTION}"

connectors:
  cluster_connector: "<+input>"
  docker_connector: "<+input>"
  docker_registry_connector: "<+input>"
  docker_registry: "docker.io"
  git_connector: "<+input>"

users:
  developers:
${devEmails}
  approvers:
${approverEmails}
  operators:
${operatorEmails}

notifications:
  slack_webhook: "<+input>"
  email_domain: "example.com"

features:
  git_experience: false
  create_rbac: ${params.CREATE_RBAC}
  create_pipelines: true

pipelines:
  nonprod:
    name: "NonProd Deployment Pipeline"
    identifier: "nonprod_pipeline"
    template_ref: "${params.NONPROD_TEMPLATE_REF}"
    version: "${params.NONPROD_TEMPLATE_VERSION}"
  prod:
    name: "Production Deployment Pipeline"
    identifier: "prod_pipeline"
    template_ref: "${params.PROD_TEMPLATE_REF}"
    version: "${params.PROD_TEMPLATE_VERSION}"
"""
                    
                    writeFile file: 'jenkins-generated-config.yaml', text: configContent
                    echo "✅ Configuration file generated: jenkins-generated-config.yaml"
                    
                    // Display config for verification
                    sh "cat jenkins-generated-config.yaml"
                }
            }
        }
        
        stage('Execute Harness Setup') {
            steps {
                script {
                    echo "🚀 Creating Harness resources..."
                    
                    if (params.ACTION == 'dry-run') {
                        echo "🧪 DRY RUN MODE - No changes will be made to Harness"
                        echo "Would create project: ${params.PROJECT_NAME}"
                        echo "Would create user groups with RBAC"
                        echo "Would create environments: prod, nonprod"
                        echo "Would create services"
                        echo "Would set up pipeline templates"
                        return
                    }
                    
                    // Project identifier (slugified)
                    def projectId = params.PROJECT_NAME.toLowerCase().replaceAll(/[^a-z0-9]/, '_')
                    def projectResult = "Initial value"
                    
                    // Step 1: Create Project
                    try {
                        echo "📂 Creating project: ${params.PROJECT_NAME}"
                        def projectPayload = """
                        {
                            "project": {
                                "orgIdentifier": "${params.HARNESS_ORG_ID}",
                                "identifier": "${projectId}",
                                "name": "${params.PROJECT_NAME}",
                                "description": "${params.PROJECT_DESCRIPTION}",
                                "color": "#0063F7"
                            }
                        }
                        """
                        
                        def projectCreateCmd = """
                        curl -s -X POST '${HARNESS_BASE_URL}/gateway/ng/api/projects' \\
                            -H 'content-type: application/json' \\
                            -H 'x-api-key: ${params.HARNESS_API_KEY}' \\
                            -d '${projectPayload.replaceAll("'", "'\\\\''")}'
                        """
                        
                        projectResult = sh(script: projectCreateCmd, returnStdout: true).trim()
                        echo "Project creation result: ${projectResult}"
                        echo "Project created with ID: ${projectId}"
                    } catch (Exception e) {
                        echo "Warning: Error creating project, it might already exist: ${e.getMessage()}"
                    }
                    
                    // Step 2: Create Environments (Prod & NonProd)
                    try {
                        echo "🌎 Creating environments..."
                        createEnvironment(params.HARNESS_API_KEY, params.HARNESS_ORG_ID, projectId, "nonprod", "NonProd")
                        createEnvironment(params.HARNESS_API_KEY, params.HARNESS_ORG_ID, projectId, "prod", "Production")
                    } catch (Exception e) {
                        echo "Warning: Error creating environments: ${e.getMessage()}"
                    }
                    
                    // Step 3: Create Service
                    try {
                        echo "⚙️ Creating service..."
                        createService(params.HARNESS_API_KEY, params.HARNESS_ORG_ID, projectId, "main_service", "${params.PROJECT_NAME} Main Service")
                    } catch (Exception e) {
                        echo "Warning: Error creating service: ${e.getMessage()}"
                    }
                    
                    // Step 4: Create User Groups if CREATE_RBAC is true
                    if (params.CREATE_RBAC) {
                        echo "👥 Creating user groups..."
                        try {
                            createUserGroups(params.HARNESS_API_KEY, params.HARNESS_ORG_ID, projectId, 
                                             params.DEVELOPER_EMAILS, params.APPROVER_EMAILS, params.OPERATOR_EMAILS)
                        } catch (Exception e) {
                            echo "Warning: Error creating user groups: ${e.getMessage()}"
                        }
                    }
                    
                    // Step 5: Create Pipelines
                    try {
                        echo "🔄 Creating pipelines..."
                        createPipeline(params.HARNESS_API_KEY, params.HARNESS_ORG_ID, projectId, 
                                      "nonprod_pipeline", "NonProd Deployment Pipeline",
                                      params.NONPROD_TEMPLATE_REF, params.NONPROD_TEMPLATE_VERSION)
                        
                        createPipeline(params.HARNESS_API_KEY, params.HARNESS_ORG_ID, projectId,
                                      "prod_pipeline", "Production Deployment Pipeline",
                                      params.PROD_TEMPLATE_REF, params.PROD_TEMPLATE_VERSION)
                    } catch (Exception e) {
                        echo "Warning: Error creating pipelines: ${e.getMessage()}"
                    }
                    
                    // Save results
                    def results = [
                        "project": [
                            "identifier": projectId,
                            "name": params.PROJECT_NAME
                        ],
                        "environments": ["nonprod", "prod"],
                        "services": ["main_service"],
                        "pipelines": ["nonprod_pipeline", "prod_pipeline"]
                    ]
                    
                    writeFile file: "complete_setup_results_${System.currentTimeMillis()}.json", 
                              text: groovy.json.JsonOutput.toJson(results)
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                script {
                    echo "📁 Archiving results..."
                    archiveArtifacts artifacts: 'complete_setup_results_*.json', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'jenkins-generated-config.yaml', allowEmptyArchive: true
                }
            }
        }
    }
    
    post {
        success {
            echo "✅ SUCCESS! Harness project automation completed successfully!"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Project: ${params.PROJECT_NAME}"
            echo "Action: ${params.ACTION}"
            echo "Check Harness UI: ${HARNESS_BASE_URL}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        }
        failure {
            echo "❌ FAILED! Harness project automation failed!"
            echo "Check the logs above for error details."
        }
        always {
            echo "Cleaning up sensitive files..."
            script {
                try {
                    sh 'rm -f jenkins-generated-config.yaml'
                    echo "Cleanup complete"
                } catch (Exception e) {
                    echo "Note: Could not clean up files, but this is not critical."
                }
            }
        }
    }
}

// Helper function to create environments
def createEnvironment(apiKey, orgId, projectId, envId, envName) {
    def envPayload = """
    {
        "environment": {
            "orgIdentifier": "${orgId}",
            "projectIdentifier": "${projectId}",
            "identifier": "${envId}",
            "name": "${envName}",
            "description": "${envName} environment",
            "type": "PreProduction",
            "tags": {}
        }
    }
    """
    
    if (envId == "prod") {
        // Override type for prod environment
        envPayload = envPayload.replace('"type": "PreProduction"', '"type": "Production"')
    }
    
    def envCmd = """
    curl -s -X POST '${HARNESS_BASE_URL}/gateway/ng/api/environments' \\
        -H 'content-type: application/json' \\
        -H 'x-api-key: ${apiKey}' \\
        -d '${envPayload.replaceAll("'", "'\\\\''")}'
    """
    
    def envResult = sh(script: envCmd, returnStdout: true).trim()
    echo "Environment creation result for ${envId}: ${envResult}"
}

// Helper function to create service
def createService(apiKey, orgId, projectId, serviceId, serviceName) {
    def servicePayload = """
    {
        "service": {
            "name": "${serviceName}",
            "identifier": "${serviceId}",
            "orgIdentifier": "${orgId}",
            "projectIdentifier": "${projectId}",
            "serviceDefinition": {
                "type": "Kubernetes",
                "spec": {
                    "artifacts": {
                        "primary": {
                            "type": "DockerRegistry",
                            "spec": {
                                "connectorRef": "<+input>",
                                "imagePath": "<+input>",
                                "tag": "<+input>"
                            }
                        }
                    },
                    "manifests": {
                        "manifest": {
                            "type": "K8sManifest",
                            "spec": {
                                "store": {
                                    "type": "Git",
                                    "spec": {
                                        "connectorRef": "<+input>",
                                        "gitFetchType": "Branch",
                                        "branch": "main",
                                        "paths": ["<+input>"]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    
    def serviceCmd = """
    curl -s -X POST '${HARNESS_BASE_URL}/gateway/ng/api/services' \\
        -H 'content-type: application/json' \\
        -H 'x-api-key: ${apiKey}' \\
        -d '${servicePayload.replaceAll("'", "'\\\\''")}'
    """
    
    def serviceResult = sh(script: serviceCmd, returnStdout: true).trim()
    echo "Service creation result: ${serviceResult}"
}

// Helper function to create pipelines from templates
def createPipeline(apiKey, orgId, projectId, pipelineId, pipelineName, templateRef, templateVersion) {
    def pipelinePayload = """
    {
        "pipeline": {
            "name": "${pipelineName}",
            "identifier": "${pipelineId}",
            "orgIdentifier": "${orgId}",
            "projectIdentifier": "${projectId}",
            "templateRef": "${templateRef}",
            "templateVersion": "${templateVersion}",
            "tags": {},
            "properties": {}
        }
    }
    """
    
    def pipelineCmd = """
    curl -s -X POST '${HARNESS_BASE_URL}/gateway/pipeline/api/pipelines/v2' \\
        -H 'content-type: application/json' \\
        -H 'x-api-key: ${apiKey}' \\
        -d '${pipelinePayload.replaceAll("'", "'\\\\''")}'
    """
    
    def pipelineResult = sh(script: pipelineCmd, returnStdout: true).trim()
    echo "Pipeline creation result for ${pipelineId}: ${pipelineResult}"
}

// Helper function to create user groups with RBAC
def createUserGroups(apiKey, orgId, projectId, developerEmails, approverEmails, operatorEmails) {
    // Create developer group
    def devGroupPayload = """
    {
        "userGroup": {
            "name": "${projectId}_developers",
            "orgIdentifier": "${orgId}",
            "description": "Developers for ${projectId}",
            "userEmails": ${parseEmailsToJson(developerEmails)},
            "isSSOLinked": false
        }
    }
    """
    
    def devGroupCmd = """
    curl -s -X POST '${HARNESS_BASE_URL}/gateway/ng/api/user-groups' \\
        -H 'content-type: application/json' \\
        -H 'x-api-key: ${apiKey}' \\
        -d '${devGroupPayload.replaceAll("'", "'\\\\''")}'
    """
    
    try {
        def devResult = sh(script: devGroupCmd, returnStdout: true).trim()
        echo "Developer group created: ${devResult}"
        
        // Add permissions for developers
        addRbacPermissions(apiKey, orgId, projectId, "${projectId}_developers", "developer")
    } catch (Exception e) {
        echo "Warning: Failed to create developer group: ${e.getMessage()}"
    }
    
    // Create approver group
    def approverGroupPayload = """
    {
        "userGroup": {
            "name": "${projectId}_approvers",
            "orgIdentifier": "${orgId}",
            "description": "Approvers for ${projectId}",
            "userEmails": ${parseEmailsToJson(approverEmails)},
            "isSSOLinked": false
        }
    }
    """
    
    def approverGroupCmd = """
    curl -s -X POST '${HARNESS_BASE_URL}/gateway/ng/api/user-groups' \\
        -H 'content-type: application/json' \\
        -H 'x-api-key: ${apiKey}' \\
        -d '${approverGroupPayload.replaceAll("'", "'\\\\''")}'
    """
    
    try {
        def approverResult = sh(script: approverGroupCmd, returnStdout: true).trim()
        echo "Approver group created: ${approverResult}"
        
        // Add permissions for approvers
        addRbacPermissions(apiKey, orgId, projectId, "${projectId}_approvers", "approver")
    } catch (Exception e) {
        echo "Warning: Failed to create approver group: ${e.getMessage()}"
    }
    
    // Create operator group
    def operatorGroupPayload = """
    {
        "userGroup": {
            "name": "${projectId}_operators",
            "orgIdentifier": "${orgId}",
            "description": "Operators for ${projectId}",
            "userEmails": ${parseEmailsToJson(operatorEmails)},
            "isSSOLinked": false
        }
    }
    """
    
    def operatorGroupCmd = """
    curl -s -X POST '${HARNESS_BASE_URL}/gateway/ng/api/user-groups' \\
        -H 'content-type: application/json' \\
        -H 'x-api-key: ${apiKey}' \\
        -d '${operatorGroupPayload.replaceAll("'", "'\\\\''")}'
    """
    
    try {
        def operatorResult = sh(script: operatorGroupCmd, returnStdout: true).trim()
        echo "Operator group created: ${operatorResult}"
        
        // Add permissions for operators
        addRbacPermissions(apiKey, orgId, projectId, "${projectId}_operators", "operator")
    } catch (Exception e) {
        echo "Warning: Failed to create operator group: ${e.getMessage()}"
    }
    
    echo "User groups created and permissions set"
}

// Helper function to add RBAC permissions
def addRbacPermissions(apiKey, orgId, projectId, groupName, role) {
    echo "Adding RBAC permissions for ${groupName} with role ${role}..."
    
    def permissions = []
    if (role == "developer") {
        permissions = ["core_pipeline_view", "core_pipeline_edit", "core_environment_view", "core_service_view"]
    } else if (role == "approver") {
        permissions = ["core_pipeline_view", "core_pipeline_edit", "core_pipeline_execute", "core_pipeline_approve", "core_environment_view", "core_service_view"]
    } else if (role == "operator") {
        permissions = ["core_pipeline_view", "core_pipeline_execute", "core_environment_view", "core_service_view"]
    }
    
    def permissionsList = permissions.collect { "\"${it}\"" }.join(",")
    
    def rbacPayload = """
    {
        "resourceGroupRequest": {
            "identifier": "${groupName}_permissions",
            "name": "${groupName} permissions",
            "orgIdentifier": "${orgId}",
            "projectIdentifier": "${projectId}",
            "resourceSelectors": [
                {
                    "type": "ALL",
                    "filter": "*"
                }
            ],
            "roles": [
                {
                    "identifier": "custom",
                    "permissions": [${permissionsList}]
                }
            ]
        }
    }
    """
    
    def rbacCmd = """
    curl -s -X POST '${HARNESS_BASE_URL}/gateway/authz/api/resource-groups' \\
        -H 'content-type: application/json' \\
        -H 'x-api-key: ${apiKey}' \\
        -d '${rbacPayload.replaceAll("'", "'\\\\''")}'
    """
    
    try {
        def rbacResult = sh(script: rbacCmd, returnStdout: true).trim()
        echo "RBAC permissions added for ${groupName}: ${rbacResult}"
    } catch (Exception e) {
        echo "Warning: Failed to add RBAC permissions for ${groupName}: ${e.getMessage()}"
    }
}

// Helper function to parse emails to JSON array
def parseEmailsToJson(emailsText) {
    def emails = emailsText.split(',').collect { it.trim() }
    return "[" + emails.collect { "\"${it}\"" }.join(",") + "]"
}
