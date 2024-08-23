from dotenv import load_dotenv
import os
load_dotenv(override=True)

SECRET_KEY = os.environ.get('SECRET_KEY')
FLASK_ENV = os.environ.get('FLASK_ENV')

class Config:
    PG_DESKTOP = os.environ.get('PostgreSQL_desktop')
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    GMAIL_USER = os.environ.get('gmail_user')
    GMAIL_PASSWORD = os.environ.get('gmail_password')
    FLASK_ENV = FLASK_ENV
    
class ProdConfig(Config):
    Debug = False
    
class DesktopConfig(Config):
    Debug = True
    PG_DESKTOP = os.environ.get('PostgreSQL_desktop')
    
class LaptopConfig(Config):
    Debug = True
    PG_DESKTOP = os.environ.get('PostgreSQL_local')