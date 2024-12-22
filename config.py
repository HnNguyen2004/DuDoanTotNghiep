import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///users.db'  # Đường dẫn đến cơ sở dữ liệu
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
