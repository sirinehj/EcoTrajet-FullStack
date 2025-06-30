"""
Management command to create default user groups required by the application.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    """
    Django command to create predefined user groups for role-based permissions.
    Creates Admin, Manager, Employee, and Auditor groups if they don't exist.
    """

    help = "Create default user groups"

    def handle(self, *args, **options):
        groups = ["Admin", "Manager", "Employee", "Auditor"]

        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f'Successfully created group "{group_name}"')
            else:
                self.stdout.write(f'Group "{group_name}" already exists')
