#!/usr/bin/env python3
"""
Jenkins Webhook Handler for Harness Automation

Receives webhooks from GitHub/GitLab and triggers Jenkins jobs
to create Harness projects automatically.
"""

from flask import Flask, request, jsonify
import requests
import yaml
import logging
import hmac
import hashlib
import os
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
JENKINS_URL = os.getenv('JENKINS_URL', 'http://localhost:8080')
JENKINS_USER = os.getenv('JENKINS_USER', 'admin')
JENKINS_TOKEN = os.getenv('JENKINS_TOKEN', '')
JENKINS_JOB_NAME = os.getenv('JENKINS_JOB_NAME', 'harness-automation')
GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', '')
GITLAB_WEBHOOK_TOKEN = os.getenv('GITLAB_WEBHOOK_TOKEN', '')


def verify_github_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature"""
    if not GITHUB_WEBHOOK_SECRET:
        logger.warning("No GitHub webhook secret configured, skipping verification")
        return True
    
    expected_signature = 'sha256=' + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def verify_gitlab_token(token: str) -> bool:
    """Verify GitLab webhook token"""
    if not GITLAB_WEBHOOK_TOKEN:
        logger.warning("No GitLab webhook token configured, skipping verification")
        return True
    
    return hmac.compare_digest(token, GITLAB_WEBHOOK_TOKEN)


def extract_repo_info_github(payload: Dict) -> Optional[Dict]:
    """Extract repository information from GitHub webhook"""
    try:
        repo = payload.get('repository', {})
        return {
            'name': repo.get('name', ''),
            'full_name': repo.get('full_name', ''),
            'owner': repo.get('owner', {}).get('login', ''),
            'description': repo.get('description', ''),
            'default_branch': repo.get('default_branch', 'main'),
            'url': repo.get('html_url', '')
        }
    except Exception as e:
        logger.error(f"Error extracting GitHub repo info: {e}")
        return None


def extract_repo_info_gitlab(payload: Dict) -> Optional[Dict]:
    """Extract repository information from GitLab webhook"""
    try:
        project = payload.get('project', {})
        return {
            'name': project.get('name', ''),
            'full_name': project.get('path_with_namespace', ''),
            'owner': project.get('namespace', ''),
            'description': project.get('description', ''),
            'default_branch': project.get('default_branch', 'main'),
            'url': project.get('web_url', '')
        }
    except Exception as e:
        logger.error(f"Error extracting GitLab repo info: {e}")
        return None


def trigger_jenkins_job(project_name: str, repo_info: Dict) -> bool:
    """Trigger Jenkins job with parameters"""
    try:
        jenkins_build_url = f"{JENKINS_URL}/job/{JENKINS_JOB_NAME}/buildWithParameters"
        
        params = {
            'ACTION': 'create-project',
            'PROJECT_NAME': project_name.lower().replace(' ', '-'),
            'PROJECT_DESCRIPTION': repo_info.get('description', f"Auto-created from {repo_info.get('full_name')}"),
            'NONPROD_TEMPLATE_REF': 'nonprod_deployment_pipeline',
            'NONPROD_TEMPLATE_VERSION': 'v1760729233',
            'PROD_TEMPLATE_REF': 'prod_deployment_pipeline',
            'PROD_TEMPLATE_VERSION': 'v1760729233',
            'CREATE_RBAC': 'true'
        }
        
        logger.info(f"Triggering Jenkins job: {JENKINS_JOB_NAME}")
        logger.info(f"Parameters: {params}")
        
        response = requests.post(
            jenkins_build_url,
            params=params,
            auth=(JENKINS_USER, JENKINS_TOKEN)
        )
        
        response.raise_for_status()
        logger.info(f"✅ Jenkins job triggered successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to trigger Jenkins job: {e}")
        return False


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'harness-webhook-handler'}), 200


@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events"""
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not verify_github_signature(request.data, signature):
        logger.warning("Invalid GitHub webhook signature")
        return jsonify({'error': 'Invalid signature'}), 401
    
    event_type = request.headers.get('X-GitHub-Event', '')
    payload = request.json
    
    logger.info(f"Received GitHub webhook: {event_type}")
    
    # Only process repository creation events
    if event_type == 'repository':
        action = payload.get('action', '')
        
        if action == 'created':
            repo_info = extract_repo_info_github(payload)
            
            if repo_info:
                logger.info(f"New repository created: {repo_info['full_name']}")
                
                # Trigger Jenkins job
                success = trigger_jenkins_job(repo_info['name'], repo_info)
                
                if success:
                    return jsonify({
                        'status': 'success',
                        'message': f"Harness project creation triggered for {repo_info['name']}",
                        'project_name': repo_info['name']
                    }), 200
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Failed to trigger Jenkins job'
                    }), 500
    
    return jsonify({'status': 'ignored', 'message': f'Event {event_type} not processed'}), 200


@app.route('/webhook/gitlab', methods=['POST'])
def gitlab_webhook():
    """Handle GitLab webhook events"""
    # Verify token
    token = request.headers.get('X-Gitlab-Token', '')
    if not verify_gitlab_token(token):
        logger.warning("Invalid GitLab webhook token")
        return jsonify({'error': 'Invalid token'}), 401
    
    event_type = request.headers.get('X-Gitlab-Event', '')
    payload = request.json
    
    logger.info(f"Received GitLab webhook: {event_type}")
    
    # Only process project creation events
    if event_type == 'Project Create Hook':
        repo_info = extract_repo_info_gitlab(payload)
        
        if repo_info:
            logger.info(f"New project created: {repo_info['full_name']}")
            
            # Trigger Jenkins job
            success = trigger_jenkins_job(repo_info['name'], repo_info)
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f"Harness project creation triggered for {repo_info['name']}",
                    'project_name': repo_info['name']
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to trigger Jenkins job'
                }), 500
    
    return jsonify({'status': 'ignored', 'message': f'Event {event_type} not processed'}), 200


@app.route('/webhook/manual', methods=['POST'])
def manual_webhook():
    """Manual webhook endpoint for testing or custom triggers"""
    data = request.json
    
    project_name = data.get('project_name', '')
    if not project_name:
        return jsonify({'error': 'project_name is required'}), 400
    
    repo_info = {
        'name': project_name,
        'full_name': project_name,
        'description': data.get('description', 'Manual trigger'),
        'url': ''
    }
    
    logger.info(f"Manual trigger for project: {project_name}")
    
    success = trigger_jenkins_job(project_name, repo_info)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': f"Harness project creation triggered for {project_name}",
            'project_name': project_name
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to trigger Jenkins job'
        }), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Harness Automation Webhook Handler")
    logger.info("=" * 60)
    logger.info(f"Jenkins URL: {JENKINS_URL}")
    logger.info(f"Jenkins Job: {JENKINS_JOB_NAME}")
    logger.info("Endpoints:")
    logger.info("  - GET  /health              (Health check)")
    logger.info("  - POST /webhook/github      (GitHub webhooks)")
    logger.info("  - POST /webhook/gitlab      (GitLab webhooks)")
    logger.info("  - POST /webhook/manual      (Manual triggers)")
    logger.info("=" * 60)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
