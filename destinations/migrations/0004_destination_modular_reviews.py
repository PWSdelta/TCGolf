# Generated by Django 5.2.3 on 2025-07-05 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0003_add_destination_guide_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='destination',
            name='modular_reviews',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
