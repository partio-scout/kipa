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
    os.path.join(BASE_DIR, "web/media"),
]

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

INTERNAL_IPS = [
    '127.0.0.1'
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
