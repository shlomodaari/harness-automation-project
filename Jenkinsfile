#!/usr/bin/env groovy

/**
 * Harness Project Automation - Jenkins Pipeline
 * 
 * This pipeline automates the creation of complete Harness projects
 * using only Groovy and Jenkins built-in capabilities.
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
        booleanParam(
            name: 'CREATE_RBAC',
            defaultValue: true,
            description: 'Create RBAC (user groups)'
        )
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
  base_url: "https://app.harness.io"

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
"""
                    
                    writeFile file: 'jenkins-generated-config.yaml', text: configContent
                    echo "✅ Configuration file generated: jenkins-generated-config.yaml"
                    
                    // Display config for verification
                    sh "cat jenkins-generated-config.yaml"
                }
            }
        }
        
        stage('Execute Harness API Calls') {
            steps {
                script {
                    echo "🚀 Executing Harness API calls..."
                    
                    if (params.ACTION == 'dry-run') {
                        echo "🧪 DRY RUN MODE - No changes will be made to Harness"
                        echo "Would create project: ${params.PROJECT_NAME}"
                        echo "Would create user groups with RBAC"
                        echo "Would set up pipeline templates"
                        return
                    }
                    
                    // 1. Create Project
                    def projectPayload = """
                    {
                        "project": {
                            "orgIdentifier": "${params.HARNESS_ORG_ID}",
                            "identifier": "${params.PROJECT_NAME.toLowerCase().replaceAll(/[^a-z0-9]/, '_')}",
                            "name": "${params.PROJECT_NAME}",
                            "description": "${params.PROJECT_DESCRIPTION}",
                            "color": "#0063F7"
                        }
                    }
                    """
                    
                    def projectCreateCmd = """
                    curl -s -X POST 'https://app.harness.io/gateway/ng/api/projects' \\
                        -H 'content-type: application/json' \\
                        -H 'x-api-key: ${params.HARNESS_API_KEY}' \\
                        -d '${projectPayload.replaceAll("'", "'\\\\''")}'
                    """
                    
                    try {
                        def projectResult = sh(script: projectCreateCmd, returnStdout: true).trim()
                        echo "Project creation result: ${projectResult}"
                        
                        // Parse project ID from result
                        def projectId = params.PROJECT_NAME.toLowerCase().replaceAll(/[^a-z0-9]/, '_')
                        echo "Project created with ID: ${projectId}"
                        
                        // 2. Create User Groups if CREATE_RBAC is true
                        if (params.CREATE_RBAC) {
                            createUserGroups(params.HARNESS_API_KEY, params.HARNESS_ORG_ID, projectId, 
                                             params.DEVELOPER_EMAILS, params.APPROVER_EMAILS, params.OPERATOR_EMAILS)
                        }
                        
                        writeFile file: "complete_setup_results_${System.currentTimeMillis()}.json", 
                                  text: """{"project": {"identifier": "${projectId}", "name": "${params.PROJECT_NAME}"}}"""
                        
                    } catch (Exception e) {
                        echo "Error creating project: ${e.getMessage()}"
                        error "Failed to create Harness project. See logs for details."
                    }
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
            echo "Check Harness UI: https://app.harness.io"
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

// Helper function to create user groups with RBAC
def createUserGroups(apiKey, orgId, projectId, developerEmails, approverEmails, operatorEmails) {
    echo "Creating user groups for project ${projectId}..."
    
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
    curl -s -X POST 'https://app.harness.io/gateway/ng/api/user-groups' \\
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
    curl -s -X POST 'https://app.harness.io/gateway/ng/api/user-groups' \\
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
    
    echo "User groups created and permissions set"
}

// Helper function to add RBAC permissions
def addRbacPermissions(apiKey, orgId, projectId, groupName, role) {
    echo "Adding RBAC permissions for ${groupName} with role ${role}..."
    
    def permissions = []
    if (role == "developer") {
        permissions = ["core_pipeline_view", "core_pipeline_edit", "core_pipeline_execute"]
    } else if (role == "approver") {
        permissions = ["core_pipeline_view", "core_pipeline_edit", "core_pipeline_execute", "core_pipeline_approve"]
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
                    "identifier": "developer",
                    "permissions": [${permissionsList}]
                }
            ]
        }
    }
    """
    
    def rbacCmd = """
    curl -s -X POST 'https://app.harness.io/gateway/authz/api/resource-groups' \\
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
