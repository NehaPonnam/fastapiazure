import os

BASE_DIR2 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'OPTIONS': {
            'options': '-c search_path=nm,queue'
        },
        'HOST': 'cxpdev01.postgres.database.azure.com',
        'PORT': '5432',
        'NAME': 'cxpdev',
        'USER': 'neha_dev@cxpdev01',
        'PASSWORD': 'hu8jmn3',
        'MAX_CONNECTION_POOL': '5'
    }
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s.%(msecs)03d] | %(levelname)s | [%(name)s:%(lineno)s] : %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'process_logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'backupCount': 10,
            'filename': os.path.join(BASE_DIR2, 'log', 'attachment_log.log'),
            'formatter': 'standard',
        },
    },
    'loggers': {
        'app': {
            'handlers': ['process_logfile'],
            'level': 'INFO',
        },
    }
}


AZURE_STORAGE_ACCOUNT_URL = 'https://demo1995.blob.core.windows.net'
AZURE_STORAGE_ACCOUNT_KEY = 'ki3oWbKgeK5qy9s3TmkGV9Ez0dHZsTjGmZArLHbgkU4Zt0+qVDnKuCNQLF73jN3r0EHuKmSGq8j0JOi2Vo84Ug=='

# STORAGE_APP_NAME = 'UnoBot'
# STORAGE_APP_NAME1 = 'UnoApp'
CONTAINER_NAME = 'blobstore'
