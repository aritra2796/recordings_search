import pymysql
from django.conf import settings

def get_connection():
    return pymysql.connect(**settings.DATABASE_CONFIG)
import pymysql.cursors

def get_connection():
    
    return pymysql.connect(
        host=settings.DATABASE_CONFIG['host'],
        user=settings.DATABASE_CONFIG['user'],
        password=settings.DATABASE_CONFIG['password'],
        database=settings.DATABASE_CONFIG['database'],
        cursorclass=pymysql.cursors.DictCursor  # <-- ensures results are dicts
    )