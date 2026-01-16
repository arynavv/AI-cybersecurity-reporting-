import os
import django
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cybercrime_platform.settings')
django.setup()

from dashboard.models import UserProfile
from dashboard.views import geocode_address

profiles = UserProfile.objects.all()
print(f"Found {profiles.count()} profiles to update.")

for profile in profiles:
    print(f"Updating profile for {profile.user.username}...")
    lat, lon = geocode_address(profile.address, profile.city, profile.state, profile.pincode)
    if lat and lon:
        profile.latitude = lat
        profile.longitude = lon
        profile.save()
        print(f"  -> Success: {lat}, {lon}")
    else:
        print("  -> Failed to geocode.")
    time.sleep(1) # Be nice to the API
