# Generated by Django 5.0 on 2025-01-03 20:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("documentation", "0006_document_search_vector_alter_document_author_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="document",
            name="views_count",
        ),
        migrations.AddField(
            model_name="document",
            name="views",
            field=models.PositiveIntegerField(default=0),
        ),
    ]