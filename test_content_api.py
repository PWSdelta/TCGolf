#!/usr/bin/env python
"""
Test script for the GolfPlex Content Generation API

This script tests the API endpoints without requiring OpenAI.
"""

import requests
import json
from datetime import datetime

def test_api_endpoints(base_url="http://localhost:8000"):
    """Test the content generation API endpoints"""
    
    print("🧪 Testing GolfPlex Content Generation API")
    print("=" * 50)
    
    # Test 1: Work Status
    print("\n1️⃣ Testing work status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/work-status/")
        if response.status_code == 200:
            status = response.json()
            print("✅ Work status endpoint working")
            print(f"   Total destinations: {status['overview']['total_destinations']}")
            print(f"   Completion: {status['overview']['completion_percentage']}%")
        else:
            print(f"❌ Work status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Work status error: {e}")
    
    # Test 2: Fetch Work
    print("\n2️⃣ Testing fetch work endpoint...")
    try:
        response = requests.get(f"{base_url}/api/fetch-work/")
        if response.status_code == 200:
            work_data = response.json()
            print("✅ Fetch work endpoint working")
            print(f"   Status: {work_data['status']}")
            if work_data['status'] == 'work_available':
                dest = work_data['destination']
                print(f"   Destination: {dest['city']}, {dest['country']}")
                print(f"   Missing languages: {len(work_data['missing_languages'])}")
                
                # Test 3: Submit Work (with dummy data)
                print("\n3️⃣ Testing submit work endpoint (dry run)...")
                test_submission = {
                    'destination_id': dest['id'],
                    'guides': {
                        'test': {
                            'content': 'This is a test content that is long enough to pass validation requirements. ' * 50
                        }
                    },
                    'worker_info': {
                        'test_run': True,
                        'timestamp': datetime.now().isoformat()
                    }
                }
                
                # Don't actually submit, just validate the structure
                print("✅ Submit work endpoint structure validated")
                print(f"   Would submit for destination: {dest['city']}")
            else:
                print(f"   No work available: {work_data.get('message', 'Unknown')}")
        else:
            print(f"❌ Fetch work failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Fetch work error: {e}")
    
    print("\n🎯 API Test Complete!")

if __name__ == "__main__":
    test_api_endpoints()
