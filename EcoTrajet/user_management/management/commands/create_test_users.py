from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = "Create test users with roles"

    def handle(self, *args, **kwargs):
        roles = ["Admin", "Manager", "Employee", "Auditor"]
        for role in roles:
            Group.objects.get_or_create(name=role)

        users_info = [
            {
                "username": "admin_user",
                "email": "admin@example.com",
                "password": "Admin@1234",
                "role": "Admin",
            },
            {
                "username": "manager_user",
                "email": "manager@example.com",
                "password": "Manager@1234",
                "role": "Manager",
            },
            {
                "username": "employee_user",
                "email": "employee@example.com",
                "password": "Employee@1234",
                "role": "Employee",
            },
            {
                "username": "auditor_user",
                "email": "auditor@example.com",
                "password": "Auditor@1234",
                "role": "Auditor",
            },
        ]

        for user_info in users_info:
            if User.objects.filter(username=user_info["username"]).exists():
                self.stdout.write(f"User {user_info['username']} already exists.")
                continue

            user = User.objects.create_user(
                username=user_info["username"],
                email=user_info["email"],
                password=user_info["password"],
                is_active=True,
            )
            group = Group.objects.get(name=user_info["role"])
            user.groups.add(group)
            self.stdout.write(
                f"Created user {user.username} with role {user_info['role']}"
            )
