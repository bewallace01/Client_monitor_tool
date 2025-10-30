"""
API Connection Testing Service
Tests connectivity to various API providers
"""
import time
from datetime import datetime
from typing import Tuple

import httpx
from sqlalchemy.orm import Session

from app.models.api_config import APIConfig
from app.schemas.api_config import APIProvider, APIConfigTestResponse
from app.services.api_config_service import encryption_service


class APITester:
    """Service for testing API connections"""

    @staticmethod
    async def test_connection(
        db: Session,
        api_config: APIConfig
    ) -> APIConfigTestResponse:
        """Test API connection based on provider"""
        start_time = time.time()

        try:
            # Decrypt API key
            api_key = encryption_service.decrypt(api_config.api_key) if api_config.api_key else None

            if not api_key:
                return APIConfigTestResponse(
                    success=False,
                    status="failed",
                    message="No API key configured",
                    tested_at=datetime.utcnow()
                )

            # Test based on provider
            if api_config.provider == APIProvider.NEWSAPI:
                success, message = await APITester._test_newsapi(api_key)
            elif api_config.provider == APIProvider.OPENAI:
                success, message = await APITester._test_openai(api_key)
            elif api_config.provider == APIProvider.GOOGLE_SEARCH:
                search_engine_id = encryption_service.decrypt(api_config.api_secret) if api_config.api_secret else None
                success, message = await APITester._test_google_search(api_key, search_engine_id)
            elif api_config.provider == APIProvider.SERPER:
                success, message = await APITester._test_serper(api_key)
            elif api_config.provider == APIProvider.ANTHROPIC:
                success, message = await APITester._test_anthropic(api_key)
            elif api_config.provider == APIProvider.HUBSPOT:
                success, message = await APITester._test_hubspot(api_key)
            elif api_config.provider == APIProvider.SALESFORCE:
                success, message = await APITester._test_salesforce(api_config)
            else:
                success = False
                message = f"Testing not implemented for provider: {api_config.provider}"

            response_time = (time.time() - start_time) * 1000  # Convert to ms

            # Update database with test results
            api_config.last_tested_at = datetime.utcnow()
            api_config.last_test_status = "success" if success else "failed"
            api_config.last_test_message = message
            db.commit()

            return APIConfigTestResponse(
                success=success,
                status="success" if success else "failed",
                message=message,
                response_time_ms=round(response_time, 2),
                tested_at=datetime.utcnow()
            )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000

            # Update database with error
            api_config.last_tested_at = datetime.utcnow()
            api_config.last_test_status = "failed"
            api_config.last_test_message = str(e)
            db.commit()

            return APIConfigTestResponse(
                success=False,
                status="failed",
                message=f"Connection test failed: {str(e)}",
                response_time_ms=round(response_time, 2),
                tested_at=datetime.utcnow()
            )

    @staticmethod
    async def _test_newsapi(api_key: str) -> Tuple[bool, str]:
        """Test NewsAPI connection"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={
                        "apiKey": api_key,
                        "country": "us",
                        "pageSize": 1
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "ok":
                        return True, "Connection successful. API key is valid."
                    else:
                        return False, f"API returned error: {data.get('message', 'Unknown error')}"
                elif response.status_code == 401:
                    return False, "Invalid API key. Please check your credentials."
                elif response.status_code == 429:
                    return False, "Rate limit exceeded. Your API key is valid but has no remaining requests."
                else:
                    return False, f"API returned status code {response.status_code}"

        except httpx.TimeoutException:
            return False, "Connection timed out. Please check your internet connection."
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    @staticmethod
    async def _test_openai(api_key: str) -> Tuple[bool, str]:
        """Test OpenAI API connection"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )

                if response.status_code == 200:
                    return True, "Connection successful. API key is valid."
                elif response.status_code == 401:
                    return False, "Invalid API key. Please check your credentials."
                elif response.status_code == 429:
                    return False, "Rate limit exceeded. Your API key is valid but has no remaining quota."
                else:
                    return False, f"API returned status code {response.status_code}"

        except httpx.TimeoutException:
            return False, "Connection timed out. Please check your internet connection."
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    @staticmethod
    async def _test_google_search(api_key: str, search_engine_id: str) -> Tuple[bool, str]:
        """Test Google Custom Search API connection"""
        try:
            if not search_engine_id:
                return False, "Search Engine ID is required for Google Custom Search"

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params={
                        "key": api_key,
                        "cx": search_engine_id,
                        "q": "test",
                        "num": 1
                    }
                )

                if response.status_code == 200:
                    return True, "Connection successful. API credentials are valid."
                elif response.status_code == 400:
                    data = response.json()
                    return False, f"Invalid configuration: {data.get('error', {}).get('message', 'Unknown error')}"
                elif response.status_code == 403:
                    return False, "Access forbidden. Check your API key and Search Engine ID."
                else:
                    return False, f"API returned status code {response.status_code}"

        except httpx.TimeoutException:
            return False, "Connection timed out. Please check your internet connection."
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    @staticmethod
    async def _test_serper(api_key: str) -> Tuple[bool, str]:
        """Test Serper Dev API connection"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://google.serper.dev/search",
                    json={"q": "test", "num": 1},
                    headers={
                        "X-API-KEY": api_key,
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code == 200:
                    return True, "Connection successful. API key is valid."
                elif response.status_code == 401:
                    return False, "Invalid API key. Please check your credentials."
                elif response.status_code == 429:
                    return False, "Rate limit exceeded. Your API key is valid but has no remaining credits."
                else:
                    return False, f"API returned status code {response.status_code}"

        except httpx.TimeoutException:
            return False, "Connection timed out. Please check your internet connection."
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    @staticmethod
    async def _test_anthropic(api_key: str) -> Tuple[bool, str]:
        """Test Anthropic API connection"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    json={
                        "model": "claude-3-haiku-20240307",
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "test"}]
                    },
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    }
                )

                if response.status_code == 200:
                    return True, "Connection successful. API key is valid."
                elif response.status_code == 401:
                    return False, "Invalid API key. Please check your credentials."
                elif response.status_code == 429:
                    return False, "Rate limit exceeded. Your API key is valid but has no remaining quota."
                else:
                    return False, f"API returned status code {response.status_code}"

        except httpx.TimeoutException:
            return False, "Connection timed out. Please check your internet connection."
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    @staticmethod
    async def _test_hubspot(api_key: str) -> Tuple[bool, str]:
        """Test HubSpot API connection"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.hubapi.com/crm/v3/objects/contacts",
                    params={"limit": 1},
                    headers={"Authorization": f"Bearer {api_key}"}
                )

                if response.status_code == 200:
                    return True, "Connection successful. API key is valid."
                elif response.status_code == 401:
                    return False, "Invalid API key. Please check your credentials."
                else:
                    return False, f"API returned status code {response.status_code}"

        except httpx.TimeoutException:
            return False, "Connection timed out. Please check your internet connection."
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    @staticmethod
    async def _test_salesforce(api_config: APIConfig) -> Tuple[bool, str]:
        """Test Salesforce API connection"""
        # Salesforce requires OAuth flow, so we test if access token is valid
        try:
            access_token = encryption_service.decrypt(api_config.access_token) if api_config.access_token else None

            if not access_token:
                return False, "No access token configured. Please complete OAuth flow."

            # Parse instance URL from config_data
            import json
            config_data = json.loads(api_config.config_data) if api_config.config_data else {}
            instance_url = config_data.get("instance_url", "https://login.salesforce.com")

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{instance_url}/services/data/v57.0/sobjects",
                    headers={"Authorization": f"Bearer {access_token}"}
                )

                if response.status_code == 200:
                    return True, "Connection successful. Access token is valid."
                elif response.status_code == 401:
                    return False, "Access token expired or invalid. Please re-authenticate."
                else:
                    return False, f"API returned status code {response.status_code}"

        except httpx.TimeoutException:
            return False, "Connection timed out. Please check your internet connection."
        except Exception as e:
            return False, f"Connection error: {str(e)}"
