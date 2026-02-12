# path to this file: "dml-marketing-middleware/integrations/total_expert.py"

import os
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TotalExpertClient:
    """
    Client for interacting with the Total Expert API.
    
    Documentation: https://documenter.getpostman.com/view/1929166/total-expert-public-api/6Z2RYyU
    """
    
    def __init__(self):
        # Get credentials from environment
        self.client_id = os.getenv("TE_CLIENT_ID")
        self.client_secret = os.getenv("TE_CLIENT_SECRET")
        self.base_url = os.getenv("TE_API_BASE_URL", "https://api.totalexpert.net")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("TE_CLIENT_ID and TE_CLIENT_SECRET must be set in environment variables")
        
        # Token management
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self):
        """
        Get OAuth 2.0 access token using client credentials flow.
        Caches the token and only refreshes when expired.
        """
        # Return cached token if still valid
        if self.access_token and self.token_expires_at and self.token_expires_at > datetime.now():
            return self.access_token
        
        logger.info("Requesting new Total Expert access token...")
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/token",
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                },
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data['access_token']
            
            # Set expiration with 60 second buffer
            expires_in = data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            logger.info("Successfully obtained Total Expert access token")
            return self.access_token
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Total Expert access token: {e}")
            raise
    
    def create_contact(self, lead_data):
        """
        Create or update a contact in Total Expert.
        
        Args:
            lead_data (dict): Dictionary with contact information
                Required keys:
                    - first_name
                    - last_name
                    - email (or phone)
                    - te_owner_id (the LO's Total Expert user ID)
                Optional keys:
                    - phone
                    - source
                    - custom fields
        
        Returns:
            dict: Response from Total Expert API with contact ID
        """
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
        
        # Build the payload per Total Expert API spec
        payload = {
            'firstName': lead_data['first_name'],
            'lastName': lead_data['last_name'],
            'ownerId': lead_data['te_owner_id'],
            'source': lead_data.get('source', 'Web Form'),
        }
        
        # Email is required if no phone
        if lead_data.get('email'):
            payload['email'] = lead_data['email']
        
        if lead_data.get('phone'):
            payload['phone'] = lead_data['phone']
        
        # Add any additional custom fields
        for key, value in lead_data.items():
            if key not in ['first_name', 'last_name', 'email', 'phone', 'te_owner_id', 'source'] and value:
                payload[key] = value
        
        logger.info(f"Creating/updating Total Expert contact: {payload.get('email')} for owner {payload.get('ownerId')}")
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/contacts",
                headers=headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully created/updated Total Expert contact: {result.get('id')}")
            return result
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create Total Expert contact: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response body: {e.response.text}")
            raise
    
    def get_contact(self, contact_id):
        """Get a contact by ID from Total Expert"""
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
        }
        
        response = requests.get(
            f"{self.base_url}/v1/contacts/{contact_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        return response.json()
    
    def search_contacts(self, email=None, phone=None):
        """Search for contacts by email or phone"""
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
        }
        
        params = {}
        if email:
            params['email'] = email
        if phone:
            params['phone'] = phone
        
        response = requests.get(
            f"{self.base_url}/v1/contacts/search",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        return response.json()
