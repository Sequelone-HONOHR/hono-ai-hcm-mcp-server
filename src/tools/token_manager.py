import os
import requests
import time
from dotenv import load_dotenv
from config import settings
import logging
# Setup logger
logger = logging.getLogger("token_manager")
logging.basicConfig(level=logging.INFO)
load_dotenv()

class TokenManager:
    def __init__(self):
        # Allow explicit env override, otherwise use centralized settings
        self.base_url = os.getenv('BASE_URL', settings.BASE_API_URL)
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self._current_token = None
        self._current_emp_code = None
        self._token_generated_time = None
        self._token_expiry_hours = settings.TOKEN_EXPIRY_HOURS  # Tokens expiry configured centrally
    
    def generate_token(self, emp_code: str, domain_url: str) -> str:
        """Generate bearer token for employee"""
        url = f"{self.base_url}/auth/generatetokenforuser"
        
        headers = {
            'clientid': self.client_id,
            'domainurl': domain_url,
            'granttype': 'client_credentials',
            'clientsecret': self.client_secret,
            'contextempcode': emp_code,
        }
        
        try:
            logger.info(f"🔄 Generating new token for employee: {emp_code}")
            response = requests.post(url, headers=headers)
            
            if response.status_code == 200:
                # Token generated successfully
                token_data = response.json()
                self._current_token = token_data.get('data')
                self._current_emp_code = emp_code
                self._token_generated_time = time.time()
                logger.info(f"✅ Token generated successfully for {emp_code}")
                return self._current_token
            else:
                logger.error(f"❌ Token generation failed: {response.status_code} - {response.text}")
                raise Exception(f"❌ Token generation failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"❌ Token generation error: {str(e)}")
            raise Exception(f"❌ Token generation error: {str(e)}")
    
    def is_token_expired(self) -> bool:
        """Check if current token has expired (24 hours)"""
        # If no token exists or token generation time is not available, consider it expired
        logger.info("🔍 Checking if token is expired...")
        if not self._current_token or not self._token_generated_time:
            logger.info("✅ Token is expired or not available")
            return True
        
        current_time = time.time()
        elapsed_hours = (current_time - self._token_generated_time) / 3600  # Convert to hours
        
        # Consider token expired if it's been more than 23.5 hours (for safety margin)
        return elapsed_hours >= 23.5
    
    def get_token(self, emp_code: str = None, domain_url: str = None) -> str:
        """Get current token or generate new one if expired/not available"""
        logger.info("🔍 Getting token...")
        # If no token exists or token is expired, generate new one
        if not self._current_token or self.is_token_expired():
            if not emp_code:
                logger.error("❌ Employee code is required to generate token")
                raise Exception("Employee code is required to generate token")
            return self.generate_token(emp_code, domain_url)
        
        # If token exists but for different employee, generate new one
        if emp_code and emp_code != self._current_emp_code:
            logger.info(f"🔄 Generating new token for employee: {emp_code}")
            return self.generate_token(emp_code, domain_url)
        
        # Return existing valid token
        elapsed_hours = (time.time() - self._token_generated_time) / 3600
        logger.info(f"🔄 Using existing token (generated {elapsed_hours:.1f} hours ago)")
        return self._current_token
    
    def get_token_info(self) -> dict:
        """Get information about current token"""
        if not self._current_token:
            logger.info("❌ No token generated")
            return {"status": "No token generated"}
        
        elapsed_seconds = time.time() - self._token_generated_time
        elapsed_hours = elapsed_seconds / 3600
        remaining_hours = self._token_expiry_hours - elapsed_hours
        logger.info("🔍 Retrieving token information...")
        return {
            "employee_code": self._current_emp_code,
            "generated_time": time.ctime(self._token_generated_time),
            "elapsed_hours": round(elapsed_hours, 2),
            "remaining_hours": round(remaining_hours, 2),
            "is_expired": self.is_token_expired()
        }

# Global token manager instance
token_manager = TokenManager()