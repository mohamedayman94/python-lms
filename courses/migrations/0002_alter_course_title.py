# Generated by Django 5.1.4 on 2024-12-24 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='title',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
