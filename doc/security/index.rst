Password Security System
=======================

Shuup includes a comprehensive password security system designed to protect user accounts and prevent unauthorized access. This system addresses both preventive measures for new passwords and remediation tools for existing weak passwords.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   configuration
   admin-interface
   management-commands
   middleware
   troubleshooting

Key Features
------------

- **Password Validation**: Enforces strong password requirements for new users and password changes
- **Weak Password Detection**: Identifies existing users with potentially weak passwords using heuristic analysis
- **Admin Dashboard**: Provides a visual interface for security monitoring and management
- **Automated Remediation**: Middleware to intercept and redirect users with weak passwords
- **Email Notifications**: Comprehensive email templates for security communications
- **Management Commands**: Command-line tools for bulk security operations

Quick Start
-----------

1. **Enable Password Validation** (See :doc:`configuration`)::

    # In your settings.py
    AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
        {'NAME': 'shuup.core.validators.StrongPasswordValidator'},
    ]

2. **Access Admin Dashboard**:
   Navigate to Admin → Settings → Security Dashboard

3. **Identify Weak Passwords**::

    uv run shuup_workbench identify_weak_passwords --dry-run

4. **Enable Middleware** (Optional)::

    MIDDLEWARE = [
        # ... other middleware
        'shuup.core.middlewares.weak_password_middleware.WeakPasswordInterceptMiddleware',
    ]

Security Best Practices
-----------------------

- Regularly audit user passwords using the management commands
- Monitor the security dashboard for trends and anomalies
- Send periodic security reminders to users
- Keep the weak password pattern list updated
- Test password reset workflows regularly

Getting Help
------------

- Review the troubleshooting guide: :doc:`troubleshooting`
- Check management command help: ``uv run shuup_workbench identify_weak_passwords --help``
- Contact support with security-specific questions
