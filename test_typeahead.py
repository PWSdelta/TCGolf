#!/usr/bin/env python
"""
Test script for typeahead search functionality
"""

import requests
import json

def test_typeahead_search():
    """Test the typeahead search API endpoint"""
    base_url = "http://127.0.0.1:8000"
    
    test_queries = [
        "Aberdeen",
        "Madrid", 
        "Dublin",
        "Tokyo",
        "Sydney",
        "UAE",
        "USA",
        "golf"
    ]
    
    print("🔍 Testing GolfPlex Typeahead Search API")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n🎯 Testing query: '{query}'")
        
        try:
            response = requests.get(f"{base_url}/api/typeahead-search/", params={'q': query})
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if results:
                print(f"✅ Found {len(results)} results:")
                for result in results[:3]:  # Show first 3 results
                    flag = result.get('country_flag', '🌍')
                    name = result.get('display_text', '')
                    location = result.get('location_text', '')
                    print(f"   {flag} {name}")
                    print(f"      📍 {location}")
            else:
                print(f"❌ No results found")
                
        except requests.RequestException as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Typeahead search test completed!")

if __name__ == "__main__":
    test_typeahead_search()
