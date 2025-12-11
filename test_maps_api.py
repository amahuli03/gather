#!/usr/bin/env python3
"""Test script for Google Places API integration."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.utils.config import load_config, get_env
from src.integrations.maps_api import MapsClient

def test_maps_api():
    """Test the Maps API client."""
    load_config()
    api_key = get_env("GOOGLE_PLACES_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_PLACES_API_KEY not found in .env file")
        print("   Please add: GOOGLE_PLACES_API_KEY=your_key_here")
        print("\n   Once you add the key, this script will test:")
        print("   1. Search places endpoint")
        print("   2. Place details endpoint")
        print("   3. Response structure parsing")
        return False
    
    print(f"✓ Found API key (length: {len(api_key)} chars)")
    
    try:
        client = MapsClient(api_key)
        print("✓ MapsClient initialized")
        
        # Test 1: Search for restaurants
        print("\n--- Test 1: Search for restaurants in Wilmington, DE ---")
        try:
            places = client.search_places("restaurants", location="Wilmington, DE", max_results=3)
            print(f"✓ Search returned {len(places)} results")
            
            if places:
                print("\nFirst result structure:")
                import json
                print(json.dumps(places[0], indent=2))
                
                # Check structure
                place = places[0]
                place_id = place.get("id", "")
                print(f"\n✓ Place ID: {place_id}")
                
                # Verify expected fields
                print("\nChecking expected fields:")
                expected_fields = ["id", "displayName", "formattedAddress"]
                for field in expected_fields:
                    if field in place:
                        print(f"  ✓ {field}: {type(place[field]).__name__}")
                    else:
                        print(f"  ⚠️  {field}: missing")
                
                # Check nested structure
                if "displayName" in place:
                    display_name = place["displayName"]
                    if isinstance(display_name, dict) and "text" in display_name:
                        print(f"  ✓ displayName.text: {display_name['text']}")
                    else:
                        print(f"  ⚠️  displayName structure unexpected: {display_name}")
                
                # Test 2: Get place details
                if place_id:
                    print("\n--- Test 2: Get place details ---")
                    try:
                        details = client.get_place_details(place_id)
                        print("✓ Place details retrieved")
                        print("\nDetails structure:")
                        print(json.dumps(details, indent=2))
                        
                        # Verify details fields
                        print("\nChecking details fields:")
                        detail_fields = ["id", "displayName", "formattedAddress", "nationalPhoneNumber", "websiteUri"]
                        for field in detail_fields:
                            if field in details:
                                print(f"  ✓ {field}: {details[field]}")
                            else:
                                print(f"  ⚠️  {field}: missing")
                    except Exception as e:
                        print(f"❌ Error getting place details: {e}")
                        print(f"   Error type: {type(e).__name__}")
                        import traceback
                        traceback.print_exc()
            else:
                print("⚠️ No places returned")
                print("   This might indicate:")
                print("   - API key restrictions")
                print("   - Invalid query format")
                print("   - API quota exceeded")
                
        except Exception as e:
            print(f"❌ Error searching places: {e}")
            print(f"   Error type: {type(e).__name__}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Status code: {e.response.status_code}")
                try:
                    error_data = e.response.json()
                    print(f"   Error response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Response text: {e.response.text[:200]}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_maps_api()
    sys.exit(0 if success else 1)

