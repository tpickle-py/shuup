"""
Weak password detection utilities for existing users.

This module provides functionality to detect and handle users with weak passwords
that were created before password validation was implemented.
"""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Import User model inside functions to avoid Django setup issues


def has_weak_password(user, password):
    """
    Check if a user's password is weak according to current validation rules.

    Args:
        user: User instance
        password: Plain text password to validate

    Returns:
        bool: True if password is weak, False if strong
    """
    try:
        validate_password(password, user)
        return False  # Password is strong
    except ValidationError:
        return True  # Password is weak


def is_user_flagged_for_password_reset(user):
    """
    Check if a user is flagged for mandatory password reset due to weak password.

    Args:
        user: User instance

    Returns:
        bool: True if user needs forced password reset
    """
    # Check if user has a flag indicating weak password
    return getattr(user, "_weak_password_detected", False)


def flag_user_for_password_reset(user):
    """
    Flag a user for mandatory password reset.

    Args:
        user: User instance
    """
    # Set a temporary attribute (in a real implementation, this might be stored in the database)
    user._weak_password_detected = True


def clear_user_password_reset_flag(user):
    """
    Clear the password reset flag for a user.

    Args:
        user: User instance
    """
    if hasattr(user, "_weak_password_detected"):
        delattr(user, "_weak_password_detected")


def get_weak_password_patterns():
    """
    Get common weak password patterns that existing users might have.

    Returns:
        list: List of common weak passwords to check
    """
    return [
        # Common weak passwords that might exist in the system
        "password",
        "123456",
        "12345678",
        "qwerty",
        "abc123",
        "password123",
        "admin",
        "letmein",
        "welcome",
        "monkey",
        "1234567890",
        "password1",
        "123123",
        "superman",
        "michael",
        "football",
        "baseball",
        "1234",
        "12345",
        "123456789",
        "test",
        "user",
        "guest",
        "demo",
        "sample",
    ]


def check_user_against_weak_patterns(user):
    """
    Check if a user likely has a weak password based on common patterns.
    This is used for proactive identification without knowing the actual password.

    Args:
        user: User instance

    Returns:
        bool: True if user likely has a weak password
    """
    # This is a heuristic check - in practice, we can only definitively know
    # when the user logs in with their actual password

    # Check for obvious patterns that can be detected from user attributes
    username = getattr(user, "username", "").lower()
    email = getattr(user, "email", "").lower().split("@")[0]
    first_name = getattr(user, "first_name", "").lower()
    last_name = getattr(user, "last_name", "").lower()

    weak_patterns = get_weak_password_patterns()

    # Check if any user attributes match common weak passwords
    user_attributes = [attr for attr in [username, email, first_name, last_name] if attr]

    for pattern in weak_patterns:
        if any(pattern in attr or attr in pattern for attr in user_attributes):
            return True

    return False


def should_force_password_reset(user):
    """
    Determine if a user should be forced to reset their password.

    Args:
        user: User instance

    Returns:
        bool: True if user should be forced to reset password
    """
    # Check if user is already flagged
    if is_user_flagged_for_password_reset(user):
        return True

    # Check if user matches weak password patterns
    if check_user_against_weak_patterns(user):
        return True

    # Additional checks can be added here
    # For example: check password age, check against breach databases, etc.

    return False


def mark_password_as_updated(user):
    """
    Mark that a user has updated their password and no longer needs forced reset.

    Args:
        user: User instance
    """
    clear_user_password_reset_flag(user)

    # In a real implementation, you might also:
    # - Update a database field indicating password was updated
    # - Log the password update event
    # - Clear any cached flags
