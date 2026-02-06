import os
import django
import sys

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()

def check_rrhh():
    username = "rrhh"
    print(f"--- Diagnosing user: {username} ---")
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"ERROR: User '{username}' not found.")
        return

    print(f"User ID: {user.id}")
    print(f"Is Superuser: {user.is_superuser}")
    print(f"Is Staff: {user.is_staff}")
    print(f"Is Active: {user.is_active}")
    print(f"Custom Role Field: {user.role}")

    print("\n[Assigned Groups]")
    groups = user.groups.all()
    if not groups:
        print("  <None>")
    else:
        for g in groups:
            print(f"  - {g.name} (ID: {g.id})")
            print("    Permissions in Group:")
            perms = g.permissions.all()
            if not perms:
                print("      <None>")
            else:
                for p in perms:
                    print(f"      - {p.content_type.app_label}.{p.codename}")

    print("\n[Direct User Permissions]")
    user_perms = user.user_permissions.all()
    if not user_perms:
        print("  <None>")
    else:
        for p in user_perms:
            print(f"  - {p.content_type.app_label}.{p.codename}")

    print("\n[Effective Permissions (get_all_permissions)]")
    all_perms = user.get_all_permissions()
    if not all_perms:
        print("  <None>")
    else:
        for p in sorted(all_perms):
            print(f"  - {p}")

    # Check specific expected permissions
    expected = [
        'gestion.view_cliente',
        'auth.view_user',
        'auth.view_group',
    ]
    print("\n[Check Specific Permissions]")
    for perm in expected:
        has_perm = user.has_perm(perm)
        print(f"  - {perm}: {'✅ YES' if has_perm else '❌ NO'}")

if __name__ == "__main__":
    check_rrhh()
