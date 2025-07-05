Admin Security Interface
========================

The Shuup admin security interface provides a comprehensive web-based dashboard for monitoring and managing password security across your platform.

Accessing the Security Dashboard
---------------------------------

**Navigation**: Admin Panel → Settings → Security Dashboard

**Required Permissions**:
- Staff user status (``is_staff=True``)
- Change user permissions (``shuup.change_user``) for advanced features

**URL**: ``/admin/security/``

Security Dashboard
------------------

The main security dashboard provides an overview of your platform's password security status.

Key Metrics
~~~~~~~~~~~

**User Statistics**:
- Total active users
- Staff vs. customer user breakdown
- Recent login activity (last 30 days)

**Security Risk Assessment**:
- Number of users with potentially weak passwords
- Risk level classification (Low/Medium/High/Critical)
- Percentage of users at risk

**Risk Level Indicators**:

.. code-block:: text

    🟢 Low Risk: < 5% of users with weak passwords
    🟡 Medium Risk: 5-15% of users with weak passwords
    🟠 High Risk: 15-30% of users with weak passwords
    🔴 Critical Risk: > 30% of users with weak passwords

Quick Actions
~~~~~~~~~~~~~

**Refresh Metrics**: Update security statistics in real-time
**Quick Scan**: Perform immediate weak password analysis
**Generate Report**: Create downloadable security assessment

Recent Security Actions
~~~~~~~~~~~~~~~~~~~~~~~

View the last 10 security-related actions:
- Policy changes
- Bulk notifications sent
- Users flagged for reset
- Administrative actions

Weak Password Management
------------------------

**Navigation**: Security Dashboard → "View Weak Passwords" or ``/admin/security/weak-passwords/``

User List View
~~~~~~~~~~~~~~

The weak password list shows all users identified as having potentially weak passwords:

**Columns**:
- Username and email
- User type (Staff/Customer badge)
- Last login date
- Matched risk patterns
- Available actions

**Filtering Options**:
- Search by username or email
- Filter by user type (staff/customer)
- Sort by various criteria

**Risk Pattern Display**:

.. code-block:: html

    <!-- Example display -->
    <span class="badge badge-danger">admin</span>
    <span class="badge badge-danger">test</span>
    <span class="badge badge-light">+2 more</span>

Individual User Actions
~~~~~~~~~~~~~~~~~~~~~~~

For each user, the following actions are available:

**View Details** (👁️):
- Detailed security assessment
- Specific risk patterns matched
- Security recommendations
- Account activity summary

**Send Notification** (📧):
- Send weak password alert email
- Includes security best practices
- Links to password change process

**Flag for Reset** (🚩):
- Mark user for mandatory password reset
- User will be redirected on next login
- Sessions cleared for security

User Detail View
~~~~~~~~~~~~~~~~

**Navigation**: Click "View Details" on any user in the weak password list

**Information Displayed**:

*User Profile*:
- Basic user information
- Account status and activity
- User type and permissions

*Security Analysis*:
- Matched weak password patterns
- Risk assessment details
- User attributes analyzed

*Recommendations*:
- Specific actions for this user
- Risk mitigation strategies
- Account verification status

**Available Actions**:

.. code-block:: text

    📧 Send Notification: Weak password alert email
    🔄 Send Reset Email: Password reset link
    🚩 Flag for Reset: Force password change on next login

Bulk Actions
~~~~~~~~~~~~

**Navigation**: Security Dashboard → "Bulk Actions" or select multiple users

**Bulk Operations**:

*Send Notifications*:
- Email alerts to selected users
- Customizable message content
- Progress tracking and error reporting

*Flag for Reset*:
- Mark multiple users for mandatory password reset
- Bulk session clearing
- Confirmation required for safety

*Send Reset Emails*:
- Password reset links to multiple users
- Token generation and email delivery
- Failed delivery tracking

*Account Deactivation* (⚠️ CAUTION):
- Disable multiple user accounts
- Requires explicit confirmation
- Irreversible action warning

**Safety Features**:
- Confirmation dialogs for destructive actions
- Dry-run mode for testing
- Detailed action logging
- Rollback documentation

Configuration Interface
-----------------------

**Navigation**: Security Dashboard → "Settings" or ``/admin/security/settings/``

Middleware Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

**Weak Password Interception**:
- Enable/disable automatic interception
- Configure allowed URLs during reset
- Session handling preferences

**Login Detection**:
- Enable password analysis during login
- Configure detection sensitivity
- Set flagging thresholds

Password Policy Settings
~~~~~~~~~~~~~~~~~~~~~~~~

**Validation Rules**:
- Minimum password length
- Character requirement toggles
- Complexity scoring

**Pattern Management**:
- Update weak password pattern list
- Add organization-specific patterns
- Configure detection algorithms

Email Notification Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Automatic Notifications**:
- Enable periodic security reminders
- Configure notification frequency
- Customize email templates

**Template Management**:
- Edit email subject lines
- Customize message content
- Preview email formatting

Security Policy Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Session Management**:
- Session timeout duration
- Concurrent session limits
- Activity tracking preferences

**Access Control**:
- Failed login attempt limits
- Account lockout duration
- IP-based restrictions

User Interface Features
-----------------------

Real-time Updates
~~~~~~~~~~~~~~~~~

The dashboard automatically refreshes key metrics every 5 minutes and provides manual refresh options for immediate updates.

Responsive Design
~~~~~~~~~~~~~~~~~

The interface is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile devices

Accessibility
~~~~~~~~~~~~~

- WCAG 2.1 AA compliant
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support

Data Export
~~~~~~~~~~~

**CSV Export**:
- User lists with security status
- Detailed risk assessments
- Historical security metrics

**Report Generation**:
- Executive security summaries
- Technical security audits
- Compliance reports

Administrative Workflows
------------------------

Daily Security Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Check Dashboard**: Review key metrics and alerts
2. **Review New Risks**: Identify newly flagged users
3. **Process Notifications**: Send alerts to high-risk users
4. **Monitor Trends**: Track security improvements over time

Weekly Security Maintenance
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Bulk Analysis**: Run comprehensive weak password scans
2. **User Communication**: Send security reminders and tips
3. **Policy Review**: Update security configurations as needed
4. **Report Generation**: Create security status reports

Monthly Security Audit
~~~~~~~~~~~~~~~~~~~~~~

1. **Comprehensive Review**: Analyze all security metrics
2. **Pattern Updates**: Refresh weak password detection patterns
3. **Process Evaluation**: Review security workflow effectiveness
4. **Documentation Update**: Maintain security procedures

Integration with External Systems
----------------------------------

LDAP/Active Directory
~~~~~~~~~~~~~~~~~~~~~

The security interface can integrate with external authentication systems:
- Sync user security status
- Coordinate password policy enforcement
- Maintain consistent security standards

SIEM Integration
~~~~~~~~~~~~~~~~

Security events can be exported to SIEM systems:
- User security events
- Administrative actions
- Policy violations

Audit Logging
~~~~~~~~~~~~~

All administrative actions are logged for compliance:
- User access to security features
- Bulk action execution
- Configuration changes
- Security policy modifications

Troubleshooting Interface Issues
--------------------------------

Common Issues
~~~~~~~~~~~~~

**Dashboard Not Loading**:
- Check user permissions
- Verify staff status
- Clear browser cache

**Missing Metrics**:
- Refresh cache manually
- Check database connectivity
- Verify user query permissions

**Email Actions Failing**:
- Verify email configuration
- Check SMTP settings
- Test email connectivity

**Bulk Actions Timeout**:
- Reduce batch size
- Increase timeout settings
- Use background task processing

Getting Help
~~~~~~~~~~~~

**Built-in Help**:
- Hover tooltips on form fields
- Contextual help blocks
- Error message guidance

**Documentation Links**:
- Direct links to relevant documentation
- Quick start guides
- Best practice recommendations

**Support Channels**:
- Error reporting system
- Admin support contact
- Community forums
