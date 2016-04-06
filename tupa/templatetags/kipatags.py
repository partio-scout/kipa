"""
Templatetags file
"""
# flake8: noqa
from django import template
REGISTER = template.Library()


def alaviiva_pois(value):
    """
    Ottaa alaviivan pois
    """
    return value.replace("_", " ")

REGISTER.filter('alaviiva_pois', alaviiva_pois)
