"""
Harness API Client - Base HTTP client with retry logic
Based on official Harness API documentation
"""

import requests
import logging
import time
import json
from typing import Dict, Any, Optional
from .models import HarnessConfig

logger = logging.getLogger(__name__)


class HarnessAPIError(Exception):
    """Custom exception for Harness API errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class HarnessClient:
    """
    Base HTTP client for Harness API
    Implements retry logic, error handling, and request/response logging
    """
    
    def __init__(self, config: HarnessConfig):
        """Initialize Harness client with configuration"""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": config.api_key
        })
        logger.info(f"✓ Harness client initialized for org: {config.org_id}")
    
    def request(
        self,
        method: str,
        endpoint: str,
        payload: Any = None,
        content_type: str = "application/json",
        params: Optional[Dict] = None,
        retry_count: int = 3,
        timeout: int = 30
    ) -> Dict:
        """
        Make HTTP request to Harness API with retry logic
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            payload: Request payload
            content_type: Content type header
            params: Query parameters
            retry_count: Number of retry attempts
            timeout: Request timeout in seconds
            
        Returns:
            API response as dictionary
            
        Raises:
            HarnessAPIError: On API error or timeout
        """
        url = f"{self.config.base_url}{endpoint}"
        last_error = None
        
        for attempt in range(retry_count):
            try:
                # Prepare request
                headers = {
                    "x-api-key": self.config.api_key,
                    "Content-Type": content_type
                }
                
                logger.debug(f"Request: {method.upper()} {endpoint} (attempt {attempt + 1}/{retry_count})")
                if payload and content_type == "application/json":
                    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
                
                # Make request based on content type
                if content_type == "application/json":
                    response = self.session.request(
                        method, url, headers=headers, json=payload, params=params, timeout=timeout
                    )
                else:
                    response = self.session.request(
                        method, url, headers=headers, data=payload, params=params, timeout=timeout
                    )
                
                # Handle specific status codes
                if response.status_code == 409:
                    logger.info(f"✓ Resource already exists (using existing)")
                    return {"status": "already_exists", "message": "Resource already exists"}
                
                if response.status_code == 404:
                    raise HarnessAPIError(
                        f"Resource not found (404): {endpoint}",
                        status_code=404
                    )
                
                # Raise for other error status codes
                response.raise_for_status()
                
                # Return JSON response or empty dict
                if response.content:
                    return response.json()
                return {"status": "success"}
                
            except requests.exceptions.Timeout as e:
                last_error = e
                logger.warning(f"Request timeout (attempt {attempt + 1}/{retry_count})")
                if attempt < retry_count - 1:
                    # Exponential backoff
                    sleep_time = 2 ** attempt
                    logger.debug(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    continue
                    
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response else None
                response_text = e.response.text if e.response else ""
                
                logger.error(f"HTTP Error {status_code}")
                logger.error(f"Response Body ({len(response_text)} bytes): {response_text[:500]}")
                
                # Don't retry on client errors (4xx)
                if status_code and 400 <= status_code < 500:
                    # Try to get JSON error details
                    error_details = response_text
                    try:
                        if e.response.content:
                            error_json = e.response.json()
                            error_details = error_json.get('message', error_json.get('error', response_text))
                    except:
                        pass
                    
                    raise HarnessAPIError(
                        f"Client error: {error_details}",
                        status_code=status_code,
                        response=error_json if 'error_json' in locals() else None
                    )
                
                # Retry on server errors (5xx)
                last_error = e
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                last_error = e
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)
                    continue
        
        # All retries exhausted
        raise HarnessAPIError(
            f"Request failed after {retry_count} attempts: {last_error}"
        )
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Convenience method for GET requests"""
        return self.request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, payload: Any = None, content_type: str = "application/json") -> Dict:
        """Convenience method for POST requests"""
        return self.request("POST", endpoint, payload=payload, content_type=content_type)
    
    def put(self, endpoint: str, payload: Any = None) -> Dict:
        """Convenience method for PUT requests"""
        return self.request("PUT", endpoint, payload=payload)
    
    def delete(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Convenience method for DELETE requests"""
        return self.request("DELETE", endpoint, params=params)
    
    def build_query_params(self, **kwargs) -> str:
        """Build query parameter string"""
        params = {
            "accountIdentifier": self.config.account_id,
            "orgIdentifier": self.config.org_id,
            **kwargs
        }
        return "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
    
    def build_endpoint(self, base: str, project_id: Optional[str] = None, **kwargs) -> str:
        """Build complete endpoint with query parameters"""
        # Add project_id to kwargs if provided
        if project_id:
            kwargs['projectIdentifier'] = project_id
        params = self.build_query_params(**kwargs)
        return f"{base}?{params}"
    
    def handle_create_result(self, result: Dict, resource_name: str, log_prefix: str = "✓") -> Dict:
        """
        Helper to handle creation results and 409 conflicts
        Returns standardized result with status field
        """
        if result.get("status") == "already_exists":
            logger.info(f"{log_prefix} {resource_name} already exists (using existing)")
            return {"status": "existing", "data": result}
        return {"status": "created", "data": result}
