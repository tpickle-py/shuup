#!/usr/bin/env python
"""
Script to create a default superuser for development.
This script is intended to be run during Docker container setup.
"""

from django.contrib.auth import get_user_model

def create_superuser():
    """Create a default superuser if it doesn't already exist."""
    User = get_user_model()
    username = "admin"
    email = "admin@admin.com"
    password = "adm!nTHISNEED1"
    
    try:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            print(f"Superuser '{username}' created successfully.")
        else:
            print(f"Superuser '{username}' already exists.")
    except Exception as e:
        print(f"Error creating superuser: {e}")
        pass

if __name__ == "__main__":
    create_superuser()
