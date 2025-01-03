from django.core.management.base import BaseCommand
from documentation.models import Category

class Command(BaseCommand):
    help = 'Creates default categories for the documentation system'

    def handle(self, *args, **kwargs):
        default_categories = [
            {
                'name': 'Getting Started',
                'description': 'Basic guides and tutorials for new users',
            },
            {
                'name': 'User Guides',
                'description': 'Detailed guides for using the system',
            },
            {
                'name': 'API Documentation',
                'description': 'API references and integration guides',
            },
            {
                'name': 'Best Practices',
                'description': 'Recommended practices and patterns',
            },
            {
                'name': 'Troubleshooting',
                'description': 'Common issues and their solutions',
            },
            {
                'name': 'Release Notes',
                'description': 'Version history and changelog',
            },
        ]

        for category_data in default_categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created category "{category.name}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category "{category.name}" already exists')
                )
