from django.db import models

class GlassdoorTable(models.Model):
    Company = models.CharField('Company name')
    ReviewTitle = models.CharField()
    Year = models.IntegerField('Year published', null=True)
    Month = models.IntegerField('Month published', null=True)
    Day = models.IntegerField('Day published', null=True)
    Rating = models.FloatField(null=True)
    JobTitle = models.CharField('Job title of reviewer')
    EmployeeRelationship = models.CharField('Relation between a reviewer and company')
    Location = models.CharField()
    Recommendation = models.CharField('Indication whether a reviewr recommends a given company')
    Outlook = models.CharField()
