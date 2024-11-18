from .common import *
from .dbmysql import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Secure Cookies (HTTPS Only)
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = ['https://*.leoapps.us'] 
SESSION_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 360
