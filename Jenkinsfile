#!/usr/bin/env groovy

pipeline {
    agent any
    
    parameters {
        // Action Selection
        choice(
            name: 'ACTION',
            choices: ['create-project', 'create-templates', 'dry-run'],
            description: 'What action to perform'
        )
        
        // Project Information
        string(
            name: 'PROJECT_NAME',
            defaultValue: 'jenkins-project-1',
            description: 'Project name (used for repo_name in config)'
        )
        string(
            name: 'PROJECT_DESCRIPTION',
            defaultValue: 'Project created via Jenkins',
            description: 'Project description'
        )
        
        // Harness Configuration
        string(
            name: 'HARNESS_ORG_ID',
            defaultValue: 'default',
            description: 'Harness Organization ID'
        )
        string(
            name: 'HARNESS_BASE_URL',
            defaultValue: 'https://app.harness.io',
            description: 'Harness base URL'
        )
        
        // Connector Information
        string(
            name: 'CLUSTER_CONNECTOR',
            defaultValue: '<+input>',
            description: 'Kubernetes cluster connector (leave as <+input> to configure later)'
        )
        string(
            name: 'DOCKER_CONNECTOR',
            defaultValue: '<+input>',
            description: 'Docker connector (leave as <+input> to configure later)'
        )
        string(
            name: 'DOCKER_REGISTRY_CONNECTOR',
            defaultValue: '<+input>',
            description: 'Docker registry connector (leave as <+input> to configure later)'
        )
        string(
            name: 'DOCKER_REGISTRY',
            defaultValue: 'docker.io',
            description: 'Docker registry URL'
        )
        string(
            name: 'GIT_CONNECTOR',
            defaultValue: '<+input>',
            description: 'Git connector (leave as <+input> to configure later)'
        )
        
        // User Lists
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
        
        // Notification Settings
        string(
            name: 'SLACK_WEBHOOK',
            defaultValue: '<+input>',
            description: 'Slack webhook URL (leave as <+input> to configure later)'
        )
        string(
            name: 'EMAIL_DOMAIN',
            defaultValue: 'example.com',
            description: 'Email domain for notifications'
        )
        
        // Feature Flags
        booleanParam(
            name: 'GIT_EXPERIENCE',
            defaultValue: false,
            description: 'Enable Git experience'
        )
        booleanParam(
            name: 'CREATE_RBAC',
            defaultValue: true,
            description: 'Create RBAC (user groups)'
        )
        booleanParam(
            name: 'CREATE_PIPELINES',
            defaultValue: true,
            description: 'Create pipelines'
        )
        
        // NonProd Pipeline Configuration
        string(
            name: 'NONPROD_PIPELINE_NAME',
            defaultValue: 'NonProd Deployment Pipeline',
            description: 'Name of the non-production pipeline'
        )
        string(
            name: 'NONPROD_PIPELINE_IDENTIFIER',
            defaultValue: 'nonprod_pipeline',
            description: 'Identifier for the non-production pipeline'
        )
        string(
            name: 'NONPROD_TEMPLATE_ID',
            defaultValue: 'nonprod_deployment_pipeline',
            description: 'Template ID for non-production pipeline'
        )
        string(
            name: 'NONPROD_TEMPLATE_VERSION',
            defaultValue: 'v1760729233',  // FIXED: Using actual version from screenshot
            description: 'Template version for non-production pipeline'
        )
        
        // Production Pipeline Configuration
        string(
            name: 'PROD_PIPELINE_NAME',
            defaultValue: 'Production Deployment Pipeline',
            description: 'Name of the production pipeline'
        )
        string(
            name: 'PROD_PIPELINE_IDENTIFIER',
            defaultValue: 'prod_pipeline',
            description: 'Identifier for the production pipeline'
        )
        string(
            name: 'PROD_TEMPLATE_ID',
            defaultValue: 'prod_deployment_pipeline',
            description: 'Template ID for production pipeline'
        )
        string(
            name: 'PROD_TEMPLATE_VERSION',
            defaultValue: 'v1760729233',  // FIXED: Using actual version from screenshot
            description: 'Template version for production pipeline'
        )
    }
    
    stages {
        stage('Run Automation') {
            steps {
                script {
                    // Checkout the code
                    checkout scm
                    
                    echo "Using credentials: harness-account-id and harness-api-credentials"
                    
                    // Convert comma-separated emails to YAML lists
                    def devEmails = params.DEVELOPER_EMAILS.split(',')
                        .collect { email -> "    - ${email.trim()}" }
                        .join('\n')
                    
                    def approverEmails = params.APPROVER_EMAILS.split(',')
                        .collect { email -> "    - ${email.trim()}" }
                        .join('\n')
                    
                    def operatorEmails = params.OPERATOR_EMAILS.split(',')
                        .collect { email -> "    - ${email.trim()}" }
                        .join('\n')
                    
                    // Use the credentials
                    withCredentials([
                        string(credentialsId: 'harness-account-id', variable: 'ACCOUNT_ID'),
                        string(credentialsId: 'harness-api-credentials', variable: 'API_KEY')
                    ]) {
                        // Generate a new config file
                        writeFile file: 'jenkins-config.yaml', text: """harness:
  account_id: "${ACCOUNT_ID}"
  api_key: "${API_KEY}"
  org_id: "${params.HARNESS_ORG_ID}"
  base_url: "${params.HARNESS_BASE_URL}"

project:
  repo_name: "${params.PROJECT_NAME}"
  description: "${params.PROJECT_DESCRIPTION}"

connectors:
  cluster_connector: "${params.CLUSTER_CONNECTOR}"
  docker_connector: "${params.DOCKER_CONNECTOR}"
  docker_registry_connector: "${params.DOCKER_REGISTRY_CONNECTOR}"
  docker_registry: "${params.DOCKER_REGISTRY}"
  git_connector: "${params.GIT_CONNECTOR}"

users:
  developers:
${devEmails}
  approvers:
${approverEmails}
  operators:
${operatorEmails}

notifications:
  slack_webhook: "${params.SLACK_WEBHOOK}"
  email_domain: "${params.EMAIL_DOMAIN}"

features:
  git_experience: ${params.GIT_EXPERIENCE}
  create_rbac: ${params.CREATE_RBAC}
  create_pipelines: ${params.CREATE_PIPELINES}

pipelines:
  nonprod:
    name: "${params.NONPROD_PIPELINE_NAME}"
    identifier: "${params.NONPROD_PIPELINE_IDENTIFIER}"
    template_ref: "${params.NONPROD_TEMPLATE_ID}"
    version: "${params.NONPROD_TEMPLATE_VERSION}"
  prod:
    name: "${params.PROD_PIPELINE_NAME}"
    identifier: "${params.PROD_PIPELINE_IDENTIFIER}"
    template_ref: "${params.PROD_TEMPLATE_ID}"
    version: "${params.PROD_TEMPLATE_VERSION}"
"""
                        
                        echo "Configuration generated with secure credentials"
                        
                        // Determine action flag
                        def actionFlag = ""
                        
                        if (params.ACTION == 'dry-run') {
                            actionFlag = "--dry-run"
                            echo "🧪 Running in dry-run mode"
                        } else if (params.ACTION == 'create-templates') {
                            actionFlag = "--create-templates"
                            echo "📋 Creating org-level templates"
                        } else {
                            echo "📦 Creating complete project"
                        }
                        
                        try {
                            // Run the script
                            sh "python3 scripts/create_complete_project.py --config-file jenkins-config.yaml ${actionFlag}"
                            echo "✅ SUCCESS! Project automation completed."
                        } catch (Exception e) {
                            echo "❌ ERROR: ${e.getMessage()}"
                            currentBuild.result = 'FAILURE'
                        } finally {
                            // Clean up
                            sh "rm -f jenkins-config.yaml || true"
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "✅ SUCCESS! Harness project '${params.PROJECT_NAME}' created successfully!"
            echo "✨ Check Harness UI at: ${params.HARNESS_BASE_URL}"
        }
        failure {
            echo "❌ FAILED! Project creation encountered issues."
            echo "📋 Please check the logs above for detailed error messages."
        }
    }
}
