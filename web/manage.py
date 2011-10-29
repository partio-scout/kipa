#!/usr/bin/python
import sys
from tupa.dia2django import luoMallienRungot
from django.core.management import execute_manager
#try:
import settings #
import legacySettings # Legacy settings for exporting an legacy db
#except ImportError:
#import sys
#    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
#    sys.exit(1)

if __name__ == "__main__":
    set=settings
    if len(sys.argv) :
            if sys.argv[1] == 'dumpdata':
                set=legacySettings
    execute_manager(set)

