from environs import Env

env = Env()

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': { 'ENGINE': 'django.db.backends.mysql',
        'HOST': env.str('DB_HOST'),
        'PORT': env.str('DB_PORT'),
        'NAME': env.str('DB_NAME'),
        'USER': env.str('DB_USER'),
        'PASSWORD': env.str('DB_PASS'),
    }
}
