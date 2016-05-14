from autodous.settings import *
import os
DEBUG = True

TEMPLATE_DEUBG = True

ALLOWED_HOSTS = (
    'autodous.azurewebsites.net',
    'autodo.us',
    'autodo.me'
)
DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
AZURE_ACCOUNT_NAME = 'autodous'
AZURE_ACCOUNT_KEY = os.getenv('STORAGE_KEY') 
AZURE_CONTAINER = 'static'

# Driver={SQL Server Native Client 11.0};Server=tcp:autodous.database.windows.net,1433;Database=autodous_dev;Uid=autodo-database@autodous;Pwd={your_password_here};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
DATABASES = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'autodous_dev',
        'USER': 'autodo-database@autodous',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'autodous.database.windows.net',
        'PORT': '1433',
    }
}
