#!/usr/bin/env groovy

/**
 * Harness Project Automation - Jenkins Pipeline
 * 
 * This pipeline automates the creation of complete Harness projects
 * including pipelines, services, environments, and RBAC.
 */

pipeline {
    agent any
    
    parameters {
        choice(
            name: 'ACTION',
            choices: ['create-project', 'create-templates', 'dry-run'],
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
        PYTHON_VERSION = 'python3'
        PIP_VERSION = 'pip3'
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
        
        stage('Setup Environment') {
            steps {
                script {
                    echo "📦 Setting up Python environment..."
                    
                    // Check if python3 exists, if not try to install it
                    def hasPython = sh(script: "which ${PYTHON_VERSION} || echo 'not_found'", returnStdout: true).trim()
                    
                    if (hasPython == 'not_found') {
                        echo "⚠️ Python not found, attempting to install it..."
                        try {
                            // Try with apt-get (Debian/Ubuntu)
                            sh "apt-get update && apt-get install -y python3 python3-pip python3-yaml"
                        } catch (Exception e) {
                            echo "⚠️ apt-get install failed, trying with apk (Alpine)..."
                            try {
                                // Try with apk (Alpine)
                                sh "apk add --no-cache python3 py3-pip py3-yaml"
                            } catch (Exception e2) {
                                echo "⚠️ Could not install Python. Please install it manually on the Jenkins node."
                                error "Python installation failed. See logs for details."
                            }
                        }
                    }
                    
                    // Check Python version
                    sh "${PYTHON_VERSION} --version"
                    
                    // Install requirements
                    sh "${PIP_VERSION} install pyyaml requests"
                    echo "✅ Python environment ready"
                }
            }
        }
        
        stage('Generate Configuration') {
            steps {
                script {
                    echo "📝 Generating configuration file..."
                    
                    // Convert comma-separated emails to YAML list
                    def devEmails = params.DEVELOPER_EMAILS.split(',').collect { "    - ${it.trim()}" }.join('\n')
                    def approverEmails = params.APPROVER_EMAILS.split(',').collect { "    - ${it.trim()}" }.join('\n')
                    def operatorEmails = params.OPERATOR_EMAILS.split(',').collect { "    - ${it.trim()}" }.join('\n')
                    
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

templates:
  nonprod:
    template_ref: "${params.NONPROD_TEMPLATE_REF}"
    version: "${params.NONPROD_TEMPLATE_VERSION}"
  prod:
    template_ref: "${params.PROD_TEMPLATE_REF}"
    version: "${params.PROD_TEMPLATE_VERSION}"
"""
                    
                    writeFile file: 'jenkins-generated-config.yaml', text: configContent
                    echo "✅ Configuration file generated: jenkins-generated-config.yaml"
                }
            }
        }
        
        stage('Validate Configuration') {
            steps {
                script {
                    echo "🔍 Validating configuration..."
                    sh """
                        cat jenkins-generated-config.yaml
                        ${PYTHON_VERSION} -c "import yaml; yaml.safe_load(open('jenkins-generated-config.yaml'))"
                    """
                    echo "✅ Configuration is valid YAML"
                }
            }
        }
        
        stage('Execute Automation') {
            steps {
                script {
                    echo "🚀 Executing Harness automation..."
                    
                    def actionFlag = ''
                    if (params.ACTION == 'create-templates') {
                        actionFlag = '--create-templates'
                        echo "📋 Creating org-level templates..."
                        sh """
                            ${PYTHON_VERSION} scripts/create_with_templates.py \\
                                --config-file jenkins-generated-config.yaml \\
                                ${actionFlag}
                        """
                    } else if (params.ACTION == 'dry-run') {
                        echo "🧪 Dry run mode - no changes will be made"
                        sh """
                            ${PYTHON_VERSION} scripts/create_complete_project.py \\
                                --config-file jenkins-generated-config.yaml \\
                                --dry-run
                        """
                    } else {
                        echo "📦 Creating complete project..."
                        sh """
                            ${PYTHON_VERSION} scripts/create_complete_project.py \\
                                --config-file jenkins-generated-config.yaml
                        """
                    }
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                script {
                    echo "📁 Archiving results..."
                    archiveArtifacts artifacts: 'complete_setup_results_*.json', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'template_setup_results_*.json', allowEmptyArchive: true
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
            // Use a try-catch to ensure this cleanup always happens
            // even if there are permission issues
            script {
                try {
                    sh 'rm -f jenkins-generated-config.yaml'
                    echo "Cleanup complete"
                } catch (Exception e) {
                    echo "Note: Could not clean up config file, but this is not critical."
                }
            }
        }
    }
}
