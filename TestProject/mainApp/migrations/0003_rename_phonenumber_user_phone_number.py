# Generated by Django 4.2 on 2023-04-21 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0002_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='phoneNumber',
            new_name='phone_number',
        ),
    ]
