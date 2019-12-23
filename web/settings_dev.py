# encoding: utf-8
from settings import *

#Django testiserverillä otetaan käyttöön myös seuraavat asetukset:
# python -Wall manage.py runserver


DEBUG = True
#RECORDING=False

'''
# Cache
TAUSTALASKENTA = False # Tulokset lasketaan taustalla (Vaatii toimiakseen tomivan cachekokoonpanon)
CACHE_TULOKSET = False # Etsitaanko tuloksia cachesta
CACHE_TULOKSET_TIME = 1800 # Tuloscachen voimassaoloaika viimeisesta nayttokerrasta. [s]
#CACHE_BACKEND = 'locmem:///' # Cache system for developement
#CACHE_BACKEND = 'locmem:///' # Cache system for developement
CACHE_BACKEND = 'db://tupa_tulos_cache'
if not CACHE_TULOKSET : 
        CACHE_BACKEND = 'dummy:///' # No cache in use
        TAUSTALASENTA = False
'''
INSTALLED_APPS += [

    #'debug_toolbar', #https://django-debug-toolbar.readthedocs.io/en/stable/installation.html
]

MIDDLEWARE += [

    #'debug_toolbar.middleware.DebugToolbarMiddleware', #https://django-debug-toolbar.readthedocs.io/en/stable/installation.html
]

STATIC_ROOT = None

STATICFILES_DIRS = [
    os.path.join(hakemisto, "media"),
]

INTERNAL_IPS = [
    '127.0.0.1'
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
