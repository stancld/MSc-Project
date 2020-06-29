from django.db import models

# set max_lengths for texts of different lengths
short_text = 25
mid_text = 100
long_text = 500

# MODELS
class CompanyTable(models.Model):
    CompanyID = models.IntegerField(null=True)
    Company = models.CharField(max_length=mid_text, blank=True) # Company name
    Symbol = models.CharField(max_length=short_text, blank=True) # Stock symbol of a given company
    ListedOn = models.CharField(max_length=short_text, blank=True) # Stock index a given company is listed on
    Sector = models.CharField(max_length=mid_text, blank=True) # Sector a company operates in according to Yahoo Finance
    Industry = models.CharField(max_length=mid_text, blank=True) # Industry a company operats in according to Yahoo Finance
    Country = models.CharField(max_length=mid_text, blank=True) # Country of HQ'
    NoEmployees = models.IntegerField(null=True) # Number of employees according to Yahoo Finance
    Revenue = models.FloatField(null=True) # The most recent available total revenue of a compnay accordin to Yahoo Finance


class GlassdoorTable(models.Model):
    CompanyID = models.ForeignKey(
        CompanyTable, on_delete=models.CASCADE, null=True)
    Company = models.CharField(max_length=mid_text, blank=True) # Company name
    ReviewTitle = models.CharField(max_length=long_text, blank=True)
    Year = models.IntegerField(null=True) # Year published
    Month = models.IntegerField(null=True) # Month published
    Day = models.IntegerField(null=True) # Day published
    Rating = models.FloatField(null=True)
    JobTitle = models.CharField(max_length=long_text, blank=True) # Job title of reviewer
    EmployeeRelationship = models.CharField(max_length=mid_text, blank=True) # Differenation between current and former employees
    Location = models.CharField(max_length=mid_text, blank=True)
    Recommendation = models.CharField(max_length=short_text, blank=True) # Indication whether a reviewer recommends a given company
    Outlook = models.CharField(max_length=short_text, blank=True)
    OpinionOfCEO = models.CharField(max_length=short_text, blank=True)
    Contract = models.CharField(max_length=mid_text, blank=True) # Differenation between FT/PT employees
    ContractPeriod = models.CharField(max_length=mid_text, blank=True) # Contract period expressed as XY months/years
    Pros = models.CharField(max_length=long_text, blank=True)
    Cons = models.CharField(max_length=long_text, blank=True)
    AdviceToManagement = models.CharField(max_length=long_text, blank=True)