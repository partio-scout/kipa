#!/usr/bin/python2
import sys, os
from tupa.dia2django import luoMallienRungot

#import settings #
#import legacySettings # Legacy settings for exporting an legacy db


if __name__ == "__main__":
    if len(sys.argv) and sys.argv[1] == 'dumpdata':
        del sys.argv[1]
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "legacySettings")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings_dev")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


