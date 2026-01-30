from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Institution Model (Admin)
class Institution(db.Model):
    __tablename__ = 'institutions'
    
    id = db.Column(db.Integer, primary_key=True)
    institution_name = db.Column(db.String(200), nullable=False)
    institution_type = db.Column(db.String(50), nullable=False)  # School/College
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(15))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    certificates = db.relationship('Certificate', backref='institution', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Student Model
class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(15))
    dob = db.Column(db.String(20))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    certificates = db.relationship('Certificate', backref='student', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Certificate Model (Core)
class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(100), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    certificate_type = db.Column(db.String(50), nullable=False)  # 10th/12th/Degree
    certificate_data = db.Column(db.Text)  # JSON data
    pdf_path = db.Column(db.String(300))
    hash_code = db.Column(db.String(64), nullable=False)
    qr_code = db.Column(db.String(300))
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active/revoked


# Verification Log Model
class VerificationLog(db.Model):
    __tablename__ = 'verification_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    verifier_email = db.Column(db.String(120))
    certificate_id = db.Column(db.String(100))
    uploaded_hash = db.Column(db.String(64))
    original_hash = db.Column(db.String(64))
    match_status = db.Column(db.String(20))  # valid/invalid
    ai_tamper_score = db.Column(db.Float)
    tamper_details = db.Column(db.Text)  # JSON
    verification_date = db.Column(db.DateTime, default=datetime.utcnow)