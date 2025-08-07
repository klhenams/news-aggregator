from typing import Any, Dict, Optional

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class HTTPClientError(Exception):
    """Base exception for HTTP client errors."""

    pass


class HTTPTimeoutError(HTTPClientError):
    """Raised when HTTP request times out."""

    pass


class HTTPRetryableError(HTTPClientError):
    """Raised for errors that should trigger a retry."""

    pass


class AsyncHTTPClient:
    """Async HTTP client with retry logic, timeouts, and proper error handling."""

    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _ensure_client(self):
        """Ensure HTTP client is initialized."""
        if self._client is None or self._client.is_closed:
            timeout = httpx.Timeout(self.settings.request_timeout)
            self._client = httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers=self._get_default_headers(),
            )

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        return {
            "User-Agent": self.settings.reddit_user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _get_auth_headers(self, api_key: str) -> Dict[str, str]:
        """Get authentication headers."""
        headers = self._get_default_headers()
        headers["Authorization"] = f"Bearer {api_key}"
        return headers

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    )
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_required: bool = False,
        api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Make an async GET request with retry logic.

        Args:
            url: The URL to request
            params: Query parameters
            headers: Additional headers
            auth_required: Whether authentication is required
            api_key: API key for authentication

        Returns:
            JSON response as dictionary

        Raises:
            HTTPClientError: For client errors
            HTTPTimeoutError: For timeout errors
            HTTPRetryableError: For retryable errors
        """
        await self._ensure_client()

        try:
            # Prepare headers
            request_headers = headers or {}
            if auth_required and api_key:
                request_headers.update(self._get_auth_headers(api_key))
            elif not auth_required:
                request_headers.update(self._get_default_headers())

            logger.info(f"Making GET request to {url}", extra={"params": params})

            response = await self._client.get(  # type: ignore[union-attr]
                url, params=params, headers=request_headers
            )

            # Check for HTTP errors
            if response.status_code >= 400:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"HTTP error for {url}: {error_msg}")

                if response.status_code >= 500:
                    raise HTTPRetryableError(error_msg)
                else:
                    raise HTTPClientError(error_msg)

            logger.info(f"Successful request to {url}")
            return response.json()  # type: ignore[no-any-return]

        except httpx.TimeoutException as e:
            error_msg = f"Request timeout for {url}: {str(e)}"
            logger.error(error_msg)
            raise HTTPTimeoutError(error_msg) from e

        except httpx.ConnectError as e:
            error_msg = f"Connection error for {url}: {str(e)}"
            logger.error(error_msg)
            raise HTTPRetryableError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error for {url}: {str(e)}"
            logger.error(error_msg)
            raise HTTPClientError(error_msg) from e

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_required: bool = True,
        api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Make an async POST request.

        Args:
            url: The URL to request
            data: Form data
            json_data: JSON data
            headers: Additional headers
            auth_required: Whether authentication is required
            api_key: API key for authentication

        Returns:
            JSON response as dictionary
        """
        await self._ensure_client()

        try:
            # Prepare headers
            request_headers = headers or {}
            if auth_required and api_key:
                request_headers.update(self._get_auth_headers(api_key))
            else:
                request_headers.update(self._get_default_headers())

            logger.info(f"Making POST request to {url}")

            response = await self._client.post(  # type: ignore[union-attr]
                url, data=data, json=json_data, headers=request_headers
            )

            response.raise_for_status()
            logger.info(f"Successful POST request to {url}")
            return response.json()  # type: ignore[no-any-return]

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"HTTP error for POST {url}: {error_msg}")
            raise HTTPClientError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error for POST {url}: {str(e)}"
            logger.error(error_msg)
            raise HTTPClientError(error_msg) from e


# Singleton instance
_http_client: Optional[AsyncHTTPClient] = None


async def get_http_client() -> AsyncHTTPClient:
    """Get the singleton HTTP client instance."""
    global _http_client
    if _http_client is None:
        _http_client = AsyncHTTPClient()
    await _http_client._ensure_client()
    return _http_client


async def close_http_client():
    """Close the singleton HTTP client."""
    global _http_client
    if _http_client:
        await _http_client.close()
        _http_client = None
