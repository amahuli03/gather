import requests
from typing import Optional, Dict, List

class MapsClient:
    """Client for Google Places API (New)."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://places.googleapis.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.regularOpeningHours,places.types,places.location"
        }
    
    def _make_request(self, endpoint: str, payload: Dict) -> Dict:
        """Make a request to the Places API."""
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, headers=self.headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    
    def search_places(
        self, 
        query: str, 
        location: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search for places using text query.
        
        Args:
            query: Text query (e.g., "restaurants in Wilmington, DE")
            location: Optional location bias (e.g., "Wilmington, DE" or coordinates)
            max_results: Maximum number of results (default 10, max 20)
        
        Returns:
            List of place dictionaries with id, displayName, formattedAddress, etc.
        """
        payload = {
            "textQuery": query,
            "maxResultCount": min(max_results, 20)
        }
        
        # Add location bias if provided
        if location:
            # Try to parse as coordinates (lat,lng) or use as location text
            if "," in location and location.replace(",", "").replace(".", "").replace("-", "").strip().replace(" ", "").isdigit():
                try:
                    lat, lng = map(float, location.split(","))
                    payload["locationBias"] = {
                        "circle": {
                            "center": {
                                "latitude": lat,
                                "longitude": lng
                            },
                            "radius": 5000.0  # 5km radius
                        }
                    }
                except ValueError:
                    # If not coordinates, use as included region
                    payload["includedRegion"] = location
            else:
                payload["includedRegion"] = location
        
        try:
            result = self._make_request("places:searchText", payload)
            places = result.get("places", [])
            
            # Ensure place IDs are in the correct format for get_place_details
            # Places API (New) returns IDs that may need "places/" prefix
            for place in places:
                place_id = place.get("id", "")
                if place_id and not place_id.startswith("places/"):
                    # Store the raw ID, we'll format it in get_place_details if needed
                    pass
            
            return places
        except requests.exceptions.HTTPError as e:
            error_msg = f"Invalid search query: {query}"
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except:
                    pass
            raise ValueError(error_msg) from e
    
    def get_place_details(self, place_id: str) -> Dict:
        """
        Get detailed information about a place by its ID.
        
        Args:
            place_id: The place ID from search results (format: "places/ChIJ..." or just "ChIJ...")
        
        Returns:
            Place details dictionary
        """
        # Request additional fields for details
        details_headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "id,displayName,formattedAddress,nationalPhoneNumber,websiteUri,regularOpeningHours,types,location,editorialSummary"
        }
        
        # Places API (New) uses GET with name parameter
        # Format place_id correctly (should be "places/{id}" format)
        if not place_id.startswith("places/"):
            place_name = f"places/{place_id}"
        else:
            place_name = place_id
        
        # Use GET request - Places API (New) format
        url = f"{self.base_url}/{place_name}"
        response = requests.get(url, headers=details_headers, timeout=15)
        response.raise_for_status()
        return response.json()
    
    def search_places_by_type(
        self,
        place_type: str,
        location: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Search for places by type (e.g., "restaurant", "park", "cafe").
        
        Args:
            place_type: Type of place (e.g., "restaurant", "park", "cafe", "gym")
            location: Location to search (e.g., "Wilmington, DE")
            max_results: Maximum number of results
        
        Returns:
            List of place dictionaries
        """
        query = f"{place_type} in {location}"
        return self.search_places(query, location=location, max_results=max_results)

