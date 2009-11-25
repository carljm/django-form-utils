from os.path import dirname, join

INSTALLED_APPS = ('form_utils', 'tests')
DATABASE_ENGINE = 'sqlite3'

MEDIA_ROOT = join(dirname(__file__), 'media')
MEDIA_URL = '/media/'
