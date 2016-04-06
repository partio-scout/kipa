"""
File: lint.py
Author: Leo Lahti
Email: leo@niinu.com
Github: https://github.com/TileHalo
Description: This is linter module for kipa
"""

from subprocess import call
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Linter class
    """
    help = 'Runs linters flake8 and  for kipa'

    def handle(self, *args, **options):
        print(args, options)
        call(["flake8", "tupa"])
        call(["flake8", "kipa"])
