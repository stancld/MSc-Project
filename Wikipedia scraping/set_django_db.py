"""
"""
# import and setup path 
import os
import sys
import django

if __name__=="__main__":
    cwd = os.getcwd()
    mysite_path = '/mnt/c/Data/UCL/@MSc Project/DB/mysite/'

    sys.path.append('/mnt/c/Data/UCL/@MSc Project/DB/mysite/')
    sys.path.append('/mnt/c/Data/UCL/@MSc Project/DB/mysite/tables_daniel/')

    try:
        os.chdir(mysite_path)
        
        os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
        django.setup()

        os.chdir(cwd)
    except Exception as e:
        print(e)