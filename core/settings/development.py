from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Base de datos
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        ssl_require=False,
    )
}

DATABASES['default']['OPTIONS'] = {'options': '-c search_path=public'}

cors_hosts = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
CORS_ALLOWED_ORIGINS = cors_hosts.split(",")