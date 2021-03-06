# Generated by Django 3.0.6 on 2020-06-29 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Symbol', models.CharField(max_length=25, verbose_name='Stock symbol of a given company')),
                ('ListedOn', models.CharField(max_length=25, verbose_name='Stock index a given company is listed on')),
                ('Sector', models.CharField(max_length=100, verbose_name='Sector a company operates in according to Yahoo Finance')),
                ('Industry', models.CharField(max_length=100, verbose_name='Industry a company operats in according to Yahoo Finance')),
                ('Country', models.CharField(max_length=100, verbose_name='Country of HQ')),
                ('NoEmployees', models.IntegerField(null=True, verbose_name='Number of employees according to Yahoo Finance')),
                ('Revenue', models.FloatField(null=True, verbose_name='The most recent available total revenue of a compnay accordin to Yahoo Finance')),
            ],
        ),
        migrations.CreateModel(
            name='GlassdoorTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Company', models.CharField(max_length=100, verbose_name='Company name')),
                ('ReviewTitle', models.CharField(max_length=500)),
                ('Year', models.IntegerField(null=True, verbose_name='Year published')),
                ('Month', models.IntegerField(null=True, verbose_name='Month published')),
                ('Day', models.IntegerField(null=True, verbose_name='Day published')),
                ('Rating', models.FloatField(null=True)),
                ('JobTitle', models.CharField(max_length=500, verbose_name='Job title of reviewer')),
                ('EmployeeRelationship', models.CharField(max_length=100, verbose_name='Differenation between current and former employees')),
                ('Location', models.CharField(max_length=100)),
                ('Recommendation', models.CharField(max_length=25, verbose_name='Indication whether a reviewer recommends a given company')),
                ('Outlook', models.CharField(max_length=25)),
                ('OpinionOfCEO', models.CharField(max_length=25)),
                ('Contract', models.CharField(max_length=100, verbose_name='Differenation between FT/PT employees')),
                ('ContractPeriod', models.CharField(max_length=100, verbose_name='Contract period expressed as XY months/years')),
                ('Pros', models.CharField(max_length=500)),
                ('Cons', models.CharField(max_length=500)),
                ('AdviceToManagement', models.CharField(max_length=500)),
                ('CompanyID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tables_daniel.CompanyTable')),
            ],
        ),
    ]
