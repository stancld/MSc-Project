# Generated by Django 3.0.6 on 2020-06-29 13:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tables_daniel', '0003_auto_20200629_1331'),
    ]

    atomic=False

    operations = [
        migrations.RenameModel(
            old_name='Companies',
            new_name='Company',
        ),
        migrations.RenameModel(
            old_name='Reviews',
            new_name='Review',
        ),
    ]
