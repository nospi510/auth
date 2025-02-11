import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    DB_HOST = 'localhost'
    DB_USER = 'nick'
    DB_PASSWORD = 'passer'
    DB_NAME = 'auth'