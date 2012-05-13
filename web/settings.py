import os

import time
try :
        fin = open("templates/version.html", "r")
        revision_line=fin.readline() ;
        fin.close()
        fout = open("templates/version.html", "w") 
        fout.write( revision_line )
        fout.write( "{% comment %} " +time.strftime('%X %x') +" {% endcomment %}" ) # Add clock to force svn commit 
        fout.close()
except: pass

hakemisto=os.path.normpath(os.path.dirname(__file__))
tarkistus= os.getcwd()

DEBUG = True
TEMPLATE_DEBUG = DEBUG
RECORDING=False
if not hakemisto == tarkistus :
        #Viittaisi siihen etta kyseessa on apachen alta toimiva, joten pakotetaan debugit pois
        DEBUG=False
        TEMPLATE_DEBUG = False

ADMINS = (
     #('frans korhonen', 'frans.korhonen@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'django.db.backends.sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = hakemisto + '/tupa.db'     # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

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

# Local time zone for this installation. 
TIME_ZONE = 'Europe/Helsinki'

# Language code for this installation. 
LANGUAGE_CODE = 'fi-FI'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = hakemisto + "/media/"

STATIC_DOC_ROOT = hakemisto + "/media/"

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

FILE_UPLOAD_HANDLERS= ("django.core.files.uploadhandler.MemoryFileUploadHandler",
 "django.core.files.uploadhandler.TemporaryFileUploadHandler",)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'shbtq($_^om(xep=5f97k2+ntb3!cqn+)%8r#s6udzqnhj$5p6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    hakemisto + '/templates',
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'tupa',
    'django.contrib.admin',
    #'django.contrib.formtools',
    'django.template',
    'django.contrib.databrowse'     

]

LOGIN_URL = ('/kipa/')
LOGIN_REDIRECT_URL = ('/kipa/')

TEST_RUNNER = ('tupa.tests.run_one_fixture')

