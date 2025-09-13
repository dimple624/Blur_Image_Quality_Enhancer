import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_secret_key")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "jwt-secret-key"
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'originals')  # Absolute path
    ENHANCED_FOLDER = os.path.join(os.getcwd(), 'uploads', 'enhanced')  # Absolute path
