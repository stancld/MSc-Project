# Generated by Django 3.0.6 on 2020-06-29 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tables_daniel', '0004_auto_20200629_1336'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='Timestamp',
            field=models.TimeField(null=True),
        ),
        migrations.AddField(
            model_name='review',
            name='Timestamp',
            field=models.TimeField(null=True),
        ),
    ]