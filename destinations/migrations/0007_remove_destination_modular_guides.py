# Generated by Django 5.2.3 on 2025-07-07 06:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0006_destinationguide_destination_destina_7d3987_idx_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='destination',
            name='modular_guides',
        ),
    ]
