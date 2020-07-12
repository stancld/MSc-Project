# import and setup path 
import os
import sys
import django

def set_django_db(mysite_path):
    """
    :param mysite_path: an absolute path to django app (outter mysite folder); type=str
    """
    cwd = os.getcwd()

    sys.path.append(mysite_path) # add path to djnago mysite
    sys.path.append(mysite_path + 'tables_daniel\\') # add path to django app

    try:
        os.chdir(mysite_path)
        
        os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
        django.setup()

        os.chdir(cwd)
    except Exception as e:
        print(e)