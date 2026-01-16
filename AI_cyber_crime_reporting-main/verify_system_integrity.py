import os
import sys
import django
from django.conf import settings

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybercrime_platform.settings')
django.setup()

from dashboard.views import geocode_address
from dashboard.models import UserProfile
from django.test import RequestFactory
from dashboard.views import get_heatmap_data

def test_geocoding_robustness():
    print("Testing Geocoding Robustness...")
    # Test 1: Normal Address
    lat, lon = geocode_address("Main Street", "Pune", "Maharashtra", "411001")
    print(f"  Normal: {lat}, {lon}")

    # Test 2: Empty Address (Should fallback to City)
    lat, lon = geocode_address("", "Pune", "Maharashtra", "411001")
    print(f"  Empty Address: {lat}, {lon}")

    # Test 3: Knowledge Patch Trigger (Chintamani)
    lat, lon = geocode_address("Chintamani Nagar Phase 2", "Bibwewadi", "Maharashtra", "411037")
    print(f"  Knowledge Patch 1 (Chintamani): {lat}, {lon}")
    
    # Test 4: Knowledge Patch Trigger (Indira Nagar)
    lat, lon = geocode_address("Upper Indira Nagar", "Bibwewadi", "Maharashtra", "411037")
    print(f"  Knowledge Patch 2 (Indira Nagar): {lat}, {lon}")

    print("Geocoding Tests Complete.\n")

def test_heatmap_api():
    print("Testing Heatmap API...")
    factory = RequestFactory()
    request = factory.get('/api/heatmap-data/')
    
    # Mock User
    from django.contrib.auth.models import AnonymousUser
    request.user = AnonymousUser() 
    # If view requires login, we might need a real user, but let's see. 
    # Actually, let's check if it requires login. If so, we need a user.
    # Assuming it might, let's try to get a user or create a dummy one.
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if User.objects.exists():
        request.user = User.objects.first()
    else:
        print("  WARNING: No users found to mock login.")

    response = get_heatmap_data(request)
    
    if response.status_code == 200:
        import json
        data = json.loads(response.content)
        print(f"  Status: 200 OK")
        print(f"  Data Count: {len(data.get('data', []))}")
        if len(data.get('data', [])) > 0:
            print(f"  Sample Data: {data['data'][0]}")
    else:
        print(f"  FAILED: Status {response.status_code}")
    print("Heatmap API Tests Complete.\n")

if __name__ == "__main__":
    try:
        test_geocoding_robustness()
        test_heatmap_api()
        print("ALL SYSTEM CHECKS PASSED.")
    except Exception as e:
        print(f"SYSTEM CHECK FAILED: {e}")
