from django.http import HttpResponse
from django.shortcuts import render

from .models import Company, Review

def index(request):
    return HttpResponse('Hello, world. This is the tables_daniel index')

def CompanyView(request):
    company_list = Company.objects.all()
    return render(company_list, 'company_list.html', locals())