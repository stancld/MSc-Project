"""
"""
# import and setup path 
import os, django
mysite_path = '/mnt/c/Data/UCL/@MSc Project/DB/mysite/'

try:
    os.chdir(mysite_path)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
    django.setup()
except Exception as e:
    print(e)
