#!/usr/bin/env python
"""Quick driver login verification"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'busproject.settings')

if __name__ == '__main__':
    import django
    django.setup()
    
    from django.contrib.auth.models import User
    from django.contrib.auth import authenticate
    from busapp.models import Profile
    from users.models import Driver

    print("\n" + "="*70)
    print("✅ DRIVER LOGIN TEST")
    print("="*70)

    # Check driver user
    try:
        user = User.objects.get(username='testdriver')
        profile = Profile.objects.get(user=user)
        driver = Driver.objects.get(user=user)
        
        print(f"\n✅ User: {user.username}")
        print(f"✅ Profile Role: {profile.role}")
        print(f"✅ Driver Route: {driver.assigned_route}")
        print(f"✅ Bus Number: {driver.assigned_route.bus_number if driver.assigned_route else 'None'}")
        
        # Test authentication
        auth = authenticate(username='testdriver', password='testdriver123')
        if auth:
            print(f"✅ Authentication: WORKS")
        else:
            print(f"❌ Authentication: FAILED")
            
        print("\n" + "="*70)
        print("📖 HOW TO LOGIN AS DRIVER:")
        print("="*70)
        print("\n1. Visit: http://localhost:8000/")
        print("2. Click 'Driver' in the role selector")
        print("3. Username: testdriver")
        print("4. Password: testdriver123")
        print("5. Click 'Login'")
        print("\n✅ You should be redirected to: /driver-tracker/")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
