#!/usr/bin/env groovy

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
            defaultValue: 'jenkins-project-1',
            description: 'Project name (used for repo_name in config)'
        )
        string(
            name: 'PROJECT_DESCRIPTION',
            defaultValue: 'Project created via Jenkins',
            description: 'Project description'
        )
    }
    
    stages {
        stage('Run Automation') {
            steps {
                script {
                    // Checkout the code
                    checkout scm
                    
                    // Display credential IDs for verification
                    echo "Using credentials: harness-account-id and harness-api-credentials"
                    
                    // NOTE: For the credentials to work, they should be set up as:
                    // 1. harness-account-id: username = actual account ID, password doesn't matter
                    // 2. harness-api-credentials: password = actual API key, username doesn't matter
                    
                    // Use the credentials
                    withCredentials([
                        string(credentialsId: 'harness-account-id', variable: 'ACCOUNT_ID'),
                        string(credentialsId: 'harness-api-credentials', variable: 'API_KEY')
                    ]) {
                        // Generate a new config file
                        writeFile file: 'jenkins-config.yaml', text: """harness:
  account_id: "${ACCOUNT_ID}"
  api_key: "${API_KEY}"
  org_id: "default"
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
    - shlomo.daari@harness.io
  approvers:
    - shlomo.daari@harness.io
  operators:
    - shlomo.daari@harness.io

notifications:
  slack_webhook: "<+input>"
  email_domain: "example.com"

features:
  git_experience: false
  create_rbac: true
  create_pipelines: true

pipelines:
  nonprod:
    name: "NonProd Deployment Pipeline"
    identifier: "nonprod_pipeline"
    template_ref: "nonprod_deployment_pipeline"
    version: "v1760729233"
  prod:
    name: "Production Deployment Pipeline"
    identifier: "prod_pipeline"
    template_ref: "prod_deployment_pipeline"
    version: "v1760729233"
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
}
