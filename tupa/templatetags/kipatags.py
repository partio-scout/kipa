"""
Templatetags file
"""
# flake8: noqa
from django import template
register = template.Library()


def alaviiva_pois(value):
    """
    Ottaa alaviivan pois
    """
    return str(value).replace("_", " ")

register.filter('alaviiva_pois', alaviiva_pois)
