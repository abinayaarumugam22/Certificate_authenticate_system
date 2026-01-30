from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from models import db, Institution, Student, Certificate, VerificationLog
from config import Config
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import json
from datetime import datetime

# Import our utility functions
from utils.certificate_generator import CertificateGenerator
from utils.hash_generator import generate_hash
from utils import generate_qr_code, get_verification_url

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    print("✅ Database initialized successfully!")

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Institution routes
@app.route('/institution/login', methods=['GET', 'POST'])
def institution_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        institution = Institution.query.filter_by(email=email).first()
        
        if institution and institution.check_password(password):
            session['institution_id'] = institution.id
            session['user_type'] = 'institution'
            flash('Login successful!', 'success')
            return redirect(url_for('institution_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('institution_login.html')

@app.route('/institution/register', methods=['GET', 'POST'])
def institution_register():
    if request.method == 'POST':
        institution = Institution(
            institution_name=request.form.get('name'),
            institution_type=request.form.get('type'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            phone=request.form.get('phone')
        )
        institution.set_password(request.form.get('password'))
        
        try:
            db.session.add(institution)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('institution_login'))
        except:
            flash('Email already exists!', 'error')
    
    return render_template('institution_register.html')

@app.route('/institution/dashboard')
def institution_dashboard():
    if 'institution_id' not in session:
        return redirect(url_for('institution_login'))
    
    institution = Institution.query.get(session['institution_id'])
    certificates = Certificate.query.filter_by(institution_id=institution.id).all()
    
    return render_template('institution_dashboard.html', 
                         institution=institution, 
                         certificates=certificates)

# Student routes
@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        student = Student.query.filter_by(email=email).first()
        
        if student and student.check_password(password):
            session['student_id'] = student.id
            session['user_type'] = 'student'
            flash('Login successful!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('student_login.html')
@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    """
    Student self-registration (optional feature)
    Usually students are created when institution uploads certificates
    """
    if request.method == 'POST':
        try:
            student = Student(
                student_id=request.form.get('student_id'),
                name=request.form.get('name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                dob=request.form.get('dob')
            )
            student.set_password(request.form.get('password'))
            
            db.session.add(student)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('student_login'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('student_register.html')

@app.route('/student/dashboard')
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))
    
    student = Student.query.get(session['student_id'])
    certificates = Certificate.query.filter_by(student_id=student.id).all()
    
    return render_template('student_dashboard.html', 
                         student=student, 
                         certificates=certificates)

# Verifier routes
@app.route('/verifier/dashboard', methods=['GET', 'POST'])
def verifier_dashboard():
    if request.method == 'POST':
        # Handle certificate verification
        pass
    
    return render_template('verifier_dashboard.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))
# Certificate Upload and Generation
@app.route('/institution/upload_certificates', methods=['POST'])
def upload_certificates():
    if 'institution_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        cert_type = request.form.get('cert_type')
        file = request.files.get('file')
        
        if not file or not cert_type:
            flash('Please select file and certificate type!', 'error')
            return redirect(url_for('institution_dashboard'))
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # Read Excel file
        if filename.endswith('.xlsx'):
            df = pd.read_excel(upload_path)
        elif filename.endswith('.csv'):
            df = pd.read_csv(upload_path)
        else:
            flash('Invalid file format! Use .xlsx or .csv', 'error')
            return redirect(url_for('institution_dashboard'))
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('__', '_')
        
        print("Available columns:", df.columns.tolist())
        
        institution = Institution.query.get(session['institution_id'])
        generator = CertificateGenerator(app.config['CERTIFICATE_FOLDER'])
        
        # Get existing certificate count for unique IDs
        existing_count = Certificate.query.filter_by(
            institution_id=institution.id,
            certificate_type=cert_type
        ).count()
        
        certificates_created = 0
        errors = []
        
        # Process each student row
        for index, row in df.iterrows():
            try:
                # Generate unique certificate ID with existing count
                cert_id = f"{cert_type.upper()}/{datetime.now().year}/{institution.id:03d}/{existing_count + index + 1:04d}"
                
                # Map column names
                student_data = {}
                
                column_mapping = {
                    'stu_id': 'student_id',
                    'student_id': 'student_id',
                    'name': 'name',
                    'father_name': 'father_name',
                    'fathername': 'father_name',
                    'mother_name': 'mother_name',
                    'mothername': 'mother_name',
                    'dob': 'dob',
                    'date_of_birth': 'dob',
                    'email': 'email',
                    'phone': 'phone',
                    'mobile': 'phone',
                    'school_name': 'school_name',
                    'schoolname': 'school_name',
                    'board': 'board',
                    'year_of_passing': 'year_of_passing',
                    'yearofpassing': 'year_of_passing',
                    'passing_year': 'year_of_passing',
                    'tamil': 'tamil',
                    'english': 'english',
                    'maths': 'mathematics',
                    'mathematics': 'mathematics',
                    'math': 'mathematics',
                    'science': 'science',
                    'social': 'social_science',
                    'social_science': 'social_science',
                    'socialscience': 'social_science',
                    'total': 'total_marks',
                    'total_marks': 'total_marks',
                    'totalmarks': 'total_marks',
                    'percentage': 'percentage',
                    'percent': 'percentage',
                    'grade': 'grade',
                    'physics': 'physics',
                    'chemistry': 'chemistry',
                    'computer_science': 'computer_science',
                    'computerscience': 'computer_science',
                    'cs': 'computer_science',
                    'college_name': 'college_name',
                    'university': 'university',
                    'degree': 'degree',
                    'specialization': 'specialization',
                    'cgpa': 'cgpa',
                    'class': 'class',
                    'stream': 'stream',
                }
                
                for col in df.columns:
                    clean_col = col.lower().strip().replace(' ', '_')
                    if clean_col in column_mapping:
                        mapped_name = column_mapping[clean_col]
                        student_data[mapped_name] = row[col]
                    else:
                        student_data[clean_col] = row[col]
                
                student_data['board'] = student_data.get('board', institution.institution_name)
                student_data['school_name'] = student_data.get('school_name', institution.institution_name)
                
                # Check if student exists
                email = student_data.get('email', f"student{existing_count + index}@temp.com")
                student = Student.query.filter_by(email=email).first()
                
                if not student:
                    student = Student(
                        student_id=student_data.get('student_id', f'STU{existing_count + index:04d}'),
                        name=student_data.get('name', 'Unknown'),
                        email=email,
                        phone=student_data.get('phone', ''),
                        dob=str(student_data.get('dob', ''))
                    )
                    student.set_password('student123')
                    db.session.add(student)
                    db.session.flush()
                
                # Generate QR code
                qr_data = get_verification_url(cert_id)
                qr_filename = f"{cert_id.replace('/', '_')}_qr.png"
                qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
                generate_qr_code(qr_data, qr_path)
                
                # Generate PDF
                pdf_path = None
                if cert_type == '10th':
                    pdf_path = generator.generate_10th_certificate(student_data, cert_id, qr_path)
                elif cert_type == '12th':
                    pdf_path = generator.generate_12th_certificate(student_data, cert_id, qr_path)
                elif cert_type == 'Degree':
                    pdf_path = generator.generate_degree_certificate(student_data, cert_id, qr_path)
                
                if not pdf_path:
                    errors.append(f"Row {index+1}: Invalid certificate type")
                    continue
                
                # Generate hash
                hash_code = generate_hash(pdf_path)
                
                if not hash_code:
                    errors.append(f"Row {index+1}: Failed to generate hash")
                    continue
                
                # Check if certificate already exists
                existing_cert = Certificate.query.filter_by(certificate_id=cert_id).first()
                
                if existing_cert:
                    # Update existing
                    existing_cert.certificate_data = json.dumps(student_data, default=str)
                    existing_cert.pdf_path = pdf_path
                    existing_cert.hash_code = hash_code
                    existing_cert.qr_code = qr_path
                    existing_cert.issue_date = datetime.utcnow()
                else:
                    # Create new
                    certificate = Certificate(
                        certificate_id=cert_id,
                        student_id=student.id,
                        institution_id=institution.id,
                        certificate_type=cert_type,
                        certificate_data=json.dumps(student_data, default=str),
                        pdf_path=pdf_path,
                        hash_code=hash_code,
                        qr_code=qr_path
                    )
                    db.session.add(certificate)
                
                certificates_created += 1
                
            except Exception as e:
                errors.append(f"Row {index+1}: {str(e)}")
                print(f"Error processing row {index}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        db.session.commit()
        
        if certificates_created > 0:
            flash(f'Successfully created {certificates_created} certificates!', 'success')
        
        if errors:
            flash(f'Errors: {"; ".join(errors[:5])}', 'warning')
        
        if certificates_created == 0:
            flash('No certificates created! Check your Excel file format.', 'error')
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('institution_dashboard'))
# Download Certificate
@app.route('/download_certificate/<int:cert_id>')
def download_certificate(cert_id):
    """
    Download certificate PDF file
    """
    try:
        certificate = Certificate.query.get_or_404(cert_id)
        
        # Check if user has permission
        if 'institution_id' in session:
            if certificate.institution_id != session['institution_id']:
                flash('Unauthorized access!', 'error')
                return redirect(url_for('institution_dashboard'))
        elif 'student_id' in session:
            if certificate.student_id != session['student_id']:
                flash('Unauthorized access!', 'error')
                return redirect(url_for('student_dashboard'))
        else:
            flash('Please login to download!', 'error')
            return redirect(url_for('index'))
        
        # Check if file exists
        if not os.path.exists(certificate.pdf_path):
            flash('Certificate file not found!', 'error')
            return redirect(request.referrer or url_for('index'))
        
        # Send file for download
        return send_file(
            certificate.pdf_path,
            as_attachment=True,
            download_name=f"{certificate.certificate_id.replace('/', '_')}.pdf"
        )
        
    except Exception as e:
        flash(f'Error downloading certificate: {str(e)}', 'error')
        return redirect(request.referrer or url_for('index'))


# View Certificate (in browser)
@app.route('/view_certificate/<int:cert_id>')
def view_certificate(cert_id):
    """
    View certificate in browser
    """
    try:
        certificate = Certificate.query.get_or_404(cert_id)
        
        # Check permissions
        if 'institution_id' in session:
            if certificate.institution_id != session['institution_id']:
                flash('Unauthorized access!', 'error')
                return redirect(url_for('institution_dashboard'))
        elif 'student_id' in session:
            if certificate.student_id != session['student_id']:
                flash('Unauthorized access!', 'error')
                return redirect(url_for('student_dashboard'))
        else:
            flash('Please login to view!', 'error')
            return redirect(url_for('index'))
        
        # Check if file exists
        if not os.path.exists(certificate.pdf_path):
            flash('Certificate file not found!', 'error')
            return redirect(request.referrer or url_for('index'))
        
        # Send file to view in browser
        return send_file(
            certificate.pdf_path,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Error viewing certificate: {str(e)}', 'error')
        return redirect(request.referrer or url_for('index'))


# View QR Code
@app.route('/view_qr/<int:cert_id>')
def view_qr(cert_id):
    """
    View QR code image
    """
    try:
        certificate = Certificate.query.get_or_404(cert_id)
        
        if not os.path.exists(certificate.qr_code):
            flash('QR code not found!', 'error')
            return redirect(request.referrer or url_for('index'))
        
        return send_file(certificate.qr_code, mimetype='image/png')
        
    except Exception as e:
        flash(f'Error viewing QR code: {str(e)}', 'error')
        return redirect(request.referrer or url_for('index'))
if __name__ == '__main__':
    app.run(debug=True, port=5000)