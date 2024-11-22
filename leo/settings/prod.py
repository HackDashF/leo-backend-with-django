from environs import Env

from .components.common import *
from .components.dbmysql import *

env = Env()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Secure Cookies (HTTPS Only)
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = env.list('TRUSTED_ORIGINS')
SESSION_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 360
