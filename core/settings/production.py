from .base import *
import os
import dj_database_url

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'api-wj-private.onrender.com')]

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True