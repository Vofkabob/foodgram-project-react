# Generated by Django 2.2.16 on 2022-04-04 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20220330_2134'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='unit_of_measurement',
            new_name='measurement_unit',
        ),
    ]
