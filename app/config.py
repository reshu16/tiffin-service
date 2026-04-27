import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    SECRET_KEY     = os.getenv('SECRET_KEY', 'fallback-secret')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fallback-jwt-secret')

    # Railway provides DATABASE_URL directly
    # Local uses individual DB_ variables
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        # Railway format: mysql://user:pass@host:port/dbname
        SQLALCHEMY_DATABASE_URI = database_url.replace(
            'mysql://', 'mysql+pymysql://')
    else:
        _db_password = quote_plus(os.getenv('DB_PASSWORD', ''))
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{os.getenv('DB_USER')}:{_db_password}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES  = 3600
    JWT_REFRESH_TOKEN_EXPIRES = 86400 * 7

    MAIL_SERVER   = os.getenv('MAIL_SERVER')
    MAIL_PORT     = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig
}