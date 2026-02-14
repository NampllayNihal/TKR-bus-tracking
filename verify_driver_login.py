#!/usr/bin/env python
"""
DRIVER LOGIN VERIFICATION SCRIPT
Run in Django shell to verify all components
"""

print("\n" + "="*70)
print("🚗 DRIVER LOGIN VERIFICATION")
print("="*70 + "\n")

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from busapp.models import Profile
from users.models import Driver
from transport.models import Route

# 1. Check User
print("1️⃣  CHECKING USER...")
try:
    user = User.objects.get(username='testdriver')
    print(f"   ✅ User exists: {user.username}")
    print(f"   ✅ Email: {user.email}")
    print(f"   ✅ Name: {user.first_name} {user.last_name}")
except User.DoesNotExist:
    print(f"   ❌ User not found!")
    exit(1)

# 2. Check Profile
print("\n2️⃣  CHECKING PROFILE...")
try:
    profile = Profile.objects.get(user=user)
    print(f"   ✅ Profile exists")
    print(f"   ✅ Role: {profile.role}")
    if profile.role != 'driver':
        print(f"   ❌ ERROR: Role should be 'driver', got '{profile.role}'")
        exit(1)
except Profile.DoesNotExist:
    print(f"   ❌ Profile not found!")
    exit(1)

# 3. Check Driver Model
print("\n3️⃣  CHECKING DRIVER MODEL...")
try:
    driver = Driver.objects.get(user=user)
    print(f"   ✅ Driver exists")
    print(f"   ✅ License: {driver.license_number}")
    print(f"   ✅ Active: {driver.is_active}")
    print(f"   ✅ Verified: {driver.is_verified}")
except Driver.DoesNotExist:
    print(f"   ❌ Driver not found!")
    exit(1)

# 4. Check Route Assignment
print("\n4️⃣  CHECKING ROUTE ASSIGNMENT...")
if driver.assigned_route:
    print(f"   ✅ Route: {driver.assigned_route.name}")
    print(f"   ✅ Bus Number: {driver.assigned_route.bus_number}")
    print(f"   ✅ Active: {driver.assigned_route.is_active}")
else:
    print(f"   ❌ No route assigned to driver!")
    exit(1)

# 5. Test Authentication
print("\n5️⃣  TESTING AUTHENTICATION...")
auth_user = authenticate(username='testdriver', password='testdriver123')
if auth_user and auth_user.id == user.id:
    print(f"   ✅ Password authentication works")
else:
    print(f"   ❌ Authentication failed!")
    exit(1)

# 6. Check Student for comparison
print("\n6️⃣  CHECKING STUDENT (for comparison)...")
try:
    student_user = User.objects.get(username='teststudent')
    student_profile = Profile.objects.get(user=student_user)
    print(f"   ✅ Student user: {student_user.username}")
    print(f"   ✅ Student role: {student_profile.role}")
except:
    print(f"   ⚠️  Student not found (optional)")

# 7. Summary
print("\n" + "="*70)
print("✅ ALL CHECKS PASSED!")
print("="*70)
print("\n📋 READY TO LOGIN AS DRIVER:")
print("\n   URL:      http://localhost:8000/")
print("   Role:     Driver (select button)")
print("   Username: testdriver")
print("   Password: testdriver123")
print("\n✅ After login → http://localhost:8000/driver-tracker/")
print("✅ Click '▶ Start Tracking' → Allow GPS → Broadcasting live!")
print("\n" + "="*70 + "\n")
