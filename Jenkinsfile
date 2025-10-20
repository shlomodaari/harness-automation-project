#!/usr/bin/env groovy

/**
 * Harness Project Automation - Jenkins Pipeline
 * With comprehensive parameter options and secure credential handling
 */

pipeline {
    agent any  // Agent is required for all stages
    
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
        // Add more parameters as needed...
    }
    
    environment {
        // Properly bind credentials without requiring pre-created credentials
        HARNESS_ACCOUNT_ID = credentials('harness-account-id')
        HARNESS_API_KEY = credentials('harness-api-key')
    }
    
    stages {
        stage('Checkout') {
            steps {
                // This automatically checks out from the repository where Jenkinsfile is located
                checkout scm
                
                // Verify we have the script files
                sh "ls -la scripts/ || true"
            }
        }
        
        stage('Copy and Update Config') {
            steps {
                script {
                    // Copy the example config file that we know works
                    sh "cp example-project-config.yaml my-config.yaml"
                    
                    // Update project information
                    sh """
                    sed -i 's/repo_name: \"test-users-and-pipelines\"/repo_name: \"${params.PROJECT_NAME}\"/' my-config.yaml
                    sed -i 's/description: \"Testing user assignment and multiple pipelines\"/description: \"${params.PROJECT_DESCRIPTION}\"/' my-config.yaml
                    """
                    
                    // Update account_id and api_key securely
                    sh """
                    sed -i 's/account_id: \"H18sdO-ETQS9O3oO9Ksu0A\"/account_id: \"${HARNESS_ACCOUNT_ID}\"/' my-config.yaml
                    sed -i 's/api_key: \"pat.H18sdO-ETQS9O3oO9Ksu0A.68f28f3c170cd3247f105140.TDJi2AKBcr5OdSMGGFFF\"/api_key: \"${HARNESS_API_KEY}\"/' my-config.yaml
                    """
                    
                    // Print config without showing sensitive info
                    sh """
                    grep -v 'api_key' my-config.yaml | grep -v 'account_id' || true
                    echo "account_id: \"******\" (hidden for security)"
                    echo "api_key: \"******\" (hidden for security)"
                    """
                }
            }
        }
        
        stage('Run Script') {
            steps {
                script {
                    def actionFlag = ""
                    
                    if (params.ACTION == 'dry-run') {
                        actionFlag = "--dry-run"
                    } else if (params.ACTION == 'create-templates') {
                        actionFlag = "--create-templates"
                    }
                    
                    // Run the existing script with the copied config
                    sh """
                    python3 scripts/create_complete_project.py --config-file my-config.yaml ${actionFlag}
                    """
                }
            }
        }
    }
    
    post {
        success {
            node {  // Important: wrap post actions in a node block
                echo "✅ SUCCESS! Harness project automation completed successfully!"
            }
        }
        failure {
            node {  // Important: wrap post actions in a node block
                echo "❌ FAILED! Harness project automation failed!"
                echo "Check the logs above for error details."
            }
        }
        always {
            node {  // Important: wrap post actions in a node block
                // Clean up the config file that contains sensitive information
                sh "rm -f my-config.yaml || true"
            }
        }
    }
}
