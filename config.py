import os

class Config:
    SECRET_KEY = 'your-secret-key-change-this-in-production'
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Create database folder if not exists
    DB_FOLDER = os.path.join(BASE_DIR, 'database')
    os.makedirs(DB_FOLDER, exist_ok=True)
    
    # Database URI
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(DB_FOLDER, "certificates.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Folder paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    CERTIFICATE_FOLDER = os.path.join(BASE_DIR, 'certificates', 'generated')
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'certificates', 'templates')
    
    # Create folders if they don't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(CERTIFICATE_FOLDER, exist_ok=True)
    os.makedirs(TEMPLATE_FOLDER, exist_ok=True)
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'xlsx', 'csv'}
    
    # Tesseract path (change this to your installation path)
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'