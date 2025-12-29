"""Shared dependencies for FastAPI routes."""
from functools import lru_cache
from typing import Optional
from src.utils.config import load_config, get_env
from src.integrations.weather_api import OpenWeatherClient
from src.integrations.n8n_api import N8NClient
from src.integrations.calendar_api import CalendarClient
from src.integrations.maps_api import MapsClient
from src.agent.types import ToolContext
from src.agent.memory import get_memory


@lru_cache()
def get_tool_context() -> ToolContext:
    """
    Create and cache ToolContext for the API.
    This is called once at startup and reused for all requests.
    """
    load_config()
    
    # Get API keys
    w_key = get_env("OPENWEATHERMAP_API_KEY")
    n8n_url = get_env("N8N_WEBHOOK_URL")
    maps_key = get_env("GOOGLE_PLACES_API_KEY")
    
    # Create clients
    weather_client = OpenWeatherClient(api_key=w_key) if w_key else None
    n8n_client = N8NClient(webhook_url=n8n_url) if n8n_url else None
    maps_client = MapsClient(api_key=maps_key) if maps_key else None
    
    # Calendar client is created per-user (needs user_id)
    # So we'll create it in the route handler
    
    return ToolContext(
        weather_client=weather_client,
        n8n_client=n8n_client,
        calendar_client=None,  # Created per request with user_id
        maps_client=maps_client,
    )


def get_user_tool_context(user_id: str, base_context: ToolContext, oauth_token: Optional[str] = None) -> ToolContext:
    """
    Create a ToolContext for a specific user.
    Calendar client needs user_id, so we create it here.
    
    Args:
        user_id: User identifier
        base_context: Base tool context
        oauth_token: Optional OAuth access token from Apps Script
    """
    calendar_client = CalendarClient(user_id=user_id, oauth_token=oauth_token)
    
    return ToolContext(
        weather_client=base_context.weather_client,
        n8n_client=base_context.n8n_client,
        calendar_client=calendar_client,
        maps_client=base_context.maps_client,
    )

