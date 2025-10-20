#!/usr/bin/env groovy

/**
 * Harness Project Automation - Jenkins Pipeline
 * With comprehensive parameter options and secure credential handling
 */

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
            name: 'PROJECT_IDENTIFIER',
            defaultValue: '',
            description: 'Optional: Project identifier (defaults to PROJECT_NAME with special chars replaced by underscores)'
        )
        string(
            name: 'PROJECT_DESCRIPTION',
            defaultValue: 'Project created via Jenkins',
            description: 'Project description'
        )
        
        // Harness Base URL
        string(
            name: 'HARNESS_BASE_URL',
            defaultValue: 'https://app.harness.io',
            description: 'Harness base URL'
        )
        string(
            name: 'HARNESS_ORG_ID',
            defaultValue: 'default',
            description: 'Harness Organization ID'
        )
        
        // Connector Information
        string(
            name: 'CLUSTER_CONNECTOR',
            defaultValue: '<+input>',
            description: 'Cluster connector reference'
        )
        string(
            name: 'DOCKER_CONNECTOR',
            defaultValue: '<+input>',
            description: 'Docker connector reference'
        )
        string(
            name: 'DOCKER_REGISTRY_CONNECTOR',
            defaultValue: '<+input>',
            description: 'Docker registry connector reference'
        )
        string(
            name: 'DOCKER_REGISTRY',
            defaultValue: 'docker.io',
            description: 'Docker registry URL'
        )
        string(
            name: 'GIT_CONNECTOR',
            defaultValue: '<+input>',
            description: 'Git connector reference'
        )
        
        // User Email Lists
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
            description: 'Slack webhook URL for notifications'
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
        
        // Pipeline Templates
        string(
            name: 'NONPROD_PIPELINE_NAME',
            defaultValue: 'NonProd Deployment Pipeline',
            description: 'Non-production pipeline name'
        )
        string(
            name: 'NONPROD_PIPELINE_IDENTIFIER',
            defaultValue: 'nonprod_pipeline',
            description: 'Non-production pipeline identifier'
        )
        string(
            name: 'NONPROD_TEMPLATE_REF',
            defaultValue: 'nonprod_deployment_pipeline',
            description: 'Non-production template reference'
        )
        string(
            name: 'NONPROD_TEMPLATE_VERSION',
            defaultValue: 'v1760729233',
            description: 'Non-production template version'
        )
        string(
            name: 'PROD_PIPELINE_NAME',
            defaultValue: 'Production Deployment Pipeline',
            description: 'Production pipeline name'
        )
        string(
            name: 'PROD_PIPELINE_IDENTIFIER',
            defaultValue: 'prod_pipeline',
            description: 'Production pipeline identifier'
        )
        string(
            name: 'PROD_TEMPLATE_REF',
            defaultValue: 'prod_deployment_pipeline',
            description: 'Production template reference'
        )
        string(
            name: 'PROD_TEMPLATE_VERSION',
            defaultValue: 'v1760729233',
            description: 'Production template version'
        )
        
        // Advanced Options
        booleanParam(
            name: 'VERBOSE_OUTPUT',
            defaultValue: true,
            description: 'Show verbose output'
        )
    }
    
    environment {
        // Use Jenkins credential bindings for sensitive information
        HARNESS_CREDS = credentials('harness-api-credentials')
        // HARNESS_CREDS_USR will contain the account ID
        // HARNESS_CREDS_PSW will contain the API key
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh "ls -la scripts/"
            }
        }
        
        stage('Generate Configuration') {
            steps {
                script {
                    echo "📝 Generating configuration file..."
                    
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
                    
                    // Set project identifier if provided, otherwise use sanitized PROJECT_NAME
                    def projectId = params.PROJECT_IDENTIFIER ?: 
                        params.PROJECT_NAME.toLowerCase().replaceAll(/[^a-z0-9]/, '_')
                    
                    // Generate configuration file
                    def configContent = """harness:
  account_id: "${HARNESS_CREDS_USR}"
  api_key: "${HARNESS_CREDS_PSW}"
  org_id: "${params.HARNESS_ORG_ID}"
  base_url: "${params.HARNESS_BASE_URL}"

project:
  repo_name: "${params.PROJECT_NAME}"
  identifier: "${projectId}"
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
    template_ref: "${params.NONPROD_TEMPLATE_REF}"
    version: "${params.NONPROD_TEMPLATE_VERSION}"
  prod:
    name: "${params.PROD_PIPELINE_NAME}"
    identifier: "${params.PROD_PIPELINE_IDENTIFIER}"
    template_ref: "${params.PROD_TEMPLATE_REF}"
    version: "${params.PROD_TEMPLATE_VERSION}"
"""
                    
                    writeFile file: 'jenkins-generated-config.yaml', text: configContent
                    
                    // Display masked config without showing sensitive info
                    echo "✅ Configuration file generated with these settings (sensitive info masked):"
                    sh '''
                    cat jenkins-generated-config.yaml | grep -v "api_key" | grep -v "account_id"
                    echo "  account_id: \"********\" (masked for security)"
                    echo "  api_key: \"********\" (masked for security)"
                    '''
                }
            }
        }
        
        stage('Run Script') {
            steps {
                script {
                    def actionFlag = ""
                    def verboseFlag = params.VERBOSE_OUTPUT ? "--verbose" : ""
                    
                    if (params.ACTION == 'dry-run') {
                        actionFlag = "--dry-run"
                        echo "🧪 Running in DRY-RUN mode - no changes will be made"
                    } else if (params.ACTION == 'create-templates') {
                        actionFlag = "--create-templates"
                        echo "📋 Creating org-level templates"
                    } else {
                        echo "📦 Creating complete project"
                    }
                    
                    // Run the script with the generated config
                    sh """
                    python3 scripts/create_complete_project.py --config-file jenkins-generated-config.yaml ${actionFlag} ${verboseFlag}
                    """
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                script {
                    echo "📁 Archiving results..."
                    archiveArtifacts artifacts: 'complete_setup_results_*.json', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'template_setup_results_*.json', allowEmptyArchive: true
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
            echo "Check Harness UI: ${params.HARNESS_BASE_URL}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        }
        failure {
            echo "❌ FAILED! Harness project automation failed!"
            echo "Check the logs above for error details."
        }
        always {
            // Clean up the config file with sensitive information
            sh "rm -f jenkins-generated-config.yaml"
        }
    }
}
