from langchain.tools import tool
from ..types import ToolContext
from typing import Optional

def create_search_places_tool(ctx: ToolContext):
    """Factory function to create place search tool with context bound via closure."""
    @tool("search_places", return_direct=False)
    def search_places(query: str, location: Optional[str] = None) -> str:
        """
        Search for places (restaurants, parks, businesses, etc.) based on a text query.
        Use this when the user asks for suggestions or wants to find places.
        Do NOT use this if the user provides a specific location/address - they already know where they want to go.
        
        Args:
            query: Text description of what to search for (e.g., "restaurants", "Mexican restaurants", "parks", "coffee shops")
            location: Optional location to search in (e.g., "Wilmington, DE", "New York, NY"). If not provided, searches broadly.
        
        Returns:
            Formatted string with place information including name, address, phone, and website.
        """
        if ctx.maps_client is None:
            return "Maps client not configured. Please add GOOGLE_PLACES_API_KEY to your .env file."
        
        try:
            places = ctx.maps_client.search_places(query, location=location, max_results=10)
            
            if not places:
                return f"No places found for '{query}'" + (f" in {location}" if location else "")
            
            result = f"Found {len(places)} places for '{query}'" + (f" in {location}" if location else "") + ":\n\n"
            
            for i, place in enumerate(places, 1):
                name = place.get("displayName", {}).get("text", "Unknown")
                address = place.get("formattedAddress", "Address not available")
                phone = place.get("nationalPhoneNumber", "Phone not available")
                website = place.get("websiteUri", "")
                
                result += f"{i}. {name}\n"
                result += f"   Address: {address}\n"
                result += f"   Phone: {phone}\n"
                if website:
                    result += f"   Website: {website}\n"
                result += "\n"
            
            return result
        except Exception as e:
            return f"Error searching places: {str(e)}"
    
    return search_places

def create_get_place_details_tool(ctx: ToolContext):
    """Factory function to create place details tool with context bound via closure."""
    @tool("get_place_details", return_direct=False)
    def get_place_details(place_id: str) -> str:
        """
        Get detailed information about a specific place by its ID.
        Use this when you need more information about a place that was returned from search_places.
        
        Args:
            place_id: The place ID from search results
        
        Returns:
            Detailed place information including hours, description, etc.
        """
        if ctx.maps_client is None:
            return "Maps client not configured. Please add GOOGLE_PLACES_API_KEY to your .env file."
        
        try:
            place = ctx.maps_client.get_place_details(place_id)
            
            name = place.get("displayName", {}).get("text", "Unknown")
            address = place.get("formattedAddress", "Address not available")
            phone = place.get("nationalPhoneNumber", "Phone not available")
            website = place.get("websiteUri", "")
            hours = place.get("regularOpeningHours", {})
            description = place.get("editorialSummary", {}).get("text", "")
            
            result = f"Details for {name}:\n\n"
            result += f"Address: {address}\n"
            result += f"Phone: {phone}\n"
            if website:
                result += f"Website: {website}\n"
            if hours:
                result += f"Hours: {hours}\n"
            if description:
                result += f"Description: {description}\n"
            
            return result
        except Exception as e:
            return f"Error getting place details: {str(e)}"
    
    return get_place_details


