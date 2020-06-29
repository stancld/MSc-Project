from django.contrib import admin

from .models import CompanyTable, GlassdoorTable

# Register your models here.
admin.site.register(CompanyTable)
admin.site.register(GlassdoorTable)