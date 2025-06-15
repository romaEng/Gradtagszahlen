import requests
from typing import Optional, Dict, Any
import logging

class CrudHandler:
    """Minimal CRUD Handler for API requests - starting with GET only"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the CRUD handler
        
        Args:
            base_url: Base URL for the API)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')  # Remove trailing slash
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Gradtagszahlen-Tool',
            'Accept': 'application/json'
        }
        
        # Setup basic logging
        self.logger = logging.getLogger(__name__)
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform GET request
        
        Args:
            endpoint: API endpoint
            params: URL parameters as dictionary
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.RequestException: For HTTP errors
            ValueError: For invalid JSON response
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            self.logger.info(f"GET request to: {url}")
            
            response = requests.get(
                url=url,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            
            # Raise exception for HTTP error status codes
            response.raise_for_status()
            
            # Try to parse JSON
            try:
                data = response.json()
                self.logger.info(f"Successful response: {response.status_code}")
                return data
            except ValueError as e:
                raise ValueError(f"Invalid JSON response: {e}")
                
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timeout after {self.timeout} seconds")
            raise
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error to {url}")
            raise
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise


# Example usage for Open-Meteo
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize handler for Open-Meteo API
    weather_api = CrudHandler("https://api.open-meteo.com/v1")
    
    try:
        # Example: Get current weather for Berlin
        params = {
            "latitude": 52.5244,
            "longitude": 13.4105,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            "timezone": "Europe/Berlin"
        }
        
        weather_data = weather_api.get("forecast", params)
        print("Weather data:", weather_data)
        
    except Exception as e:
        print(f"Error getting weather data: {e}")
