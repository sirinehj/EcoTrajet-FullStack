from django.db import models
from django.contrib.auth.models import User


class UserLoginAttempt(models.Model):
    """
    Tracks all login attempts to the system for security monitoring and audit purposes.

    This model records both successful and failed login attempts, storing information
    about the user, username attempted, IP address, success status, and timestamp.
    This data can be used for security analysis, detecting brute force attacks,
    and meeting audit/compliance requirements.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    """Reference to the User if login was successful or if user exists (null for non-existent users)"""

    username = models.CharField(max_length=150)
    """The username that was used in the login attempt"""

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    """IP address from which the login attempt originated"""

    success = models.BooleanField(default=False)
    """Whether the login attempt was successful (True) or failed (False)"""

    timestamp = models.DateTimeField(auto_now_add=True)
    """When the login attempt occurred (automatically set on creation)"""

    class Meta:
        """
        Model metadata options.
        """

        ordering = ["-timestamp"]  # Most recent attempts first
