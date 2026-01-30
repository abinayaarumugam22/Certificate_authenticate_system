from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import os

class CertificateGenerator:
    """
    Generate DigiLocker-style professional academic certificates
    """
    
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.width, self.height = A4
        
    def generate_10th_certificate(self, student_data, cert_id, qr_path=None):
        """
        Generate 10th Standard DigiLocker-style Certificate
        """
        filename = f"{cert_id}_10th.pdf".replace('/', '_')
        filepath = os.path.join(self.output_folder, filename)
        
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # ---------- OUTER BORDER ----------
        c.setStrokeColor(colors.HexColor('#003366'))
        c.setLineWidth(3)
        c.rect(1*cm, 1*cm, width - 2*cm, height - 2*cm)
        
        c.setLineWidth(1)
        c.rect(1.2*cm, 1.2*cm, width - 2.4*cm, height - 2.4*cm)
        
        # ---------- HEADER ----------
        # Government Emblem placeholder (you can add logo later)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height - 3*cm, "☸")  # Placeholder emblem
        
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2, height - 3.8*cm,
                           "STATE BOARD OF SCHOOL EXAMINATIONS, TAMIL NADU")
        
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height - 4.5*cm,
                           "DEPARTMENT OF GOVERNMENT EXAMINATIONS, CHENNAI – 600 006")
        
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(width/2, height - 5.5*cm,
                           "SECONDARY SCHOOL LEAVING CERTIFICATE")
        
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width/2, height - 6.2*cm, "X STANDARD")
        
        # ---------- CERTIFICATE NUMBER (Top Right) ----------
        c.setFont("Helvetica", 9)
        c.drawRightString(width - 2*cm, height - 2*cm, f"Certificate No: {cert_id}")
        
        # ---------- STUDENT DETAILS ----------
        y = height - 7.5*cm
        gap = 0.7*cm
        
        c.setFont("Helvetica-Bold", 10)
        
        details = [
            ("NAME OF THE CANDIDATE", student_data.get('name', 'N/A').upper()),
            ("REGISTER NUMBER", student_data.get('student_id', 'N/A').upper()),
            ("DATE OF BIRTH", str(student_data.get('dob', 'N/A'))),
            ("SESSION", f"{student_data.get('board', 'STATE BOARD')} - {student_data.get('year_of_passing', '2024')}"),
            ("SCHOOL NAME", student_data.get('school_name', 'N/A').upper())
        ]
        
        for label, value in details:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(2.5*cm, y, f"{label}")
            c.setFont("Helvetica", 9)
            c.drawString(2.5*cm, y - 0.35*cm, f": {value}")
            y -= gap
        
        # ---------- MARKS TABLE ----------
        table_y = y - 1*cm
        
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor('#003366'))
        c.rect(2.5*cm, table_y - 0.5*cm, width - 5*cm, 0.7*cm, fill=1)
        
        c.setFillColor(colors.white)
        headers = ["SUBJECT", "THEORY", "PRACTICAL", "TOTAL", "RESULT"]
        x_positions = [3*cm, 9*cm, 11.5*cm, 14*cm, 16.5*cm]
        
        for i, header in enumerate(headers):
            c.drawString(x_positions[i], table_y - 0.25*cm, header)
        
        # Table rows
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        
        subjects = [
            ("TAMIL", str(student_data.get('tamil', '0')), "-", str(student_data.get('tamil', '0')), "P"),
            ("ENGLISH", str(student_data.get('english', '0')), "-", str(student_data.get('english', '0')), "P"),
            ("MATHEMATICS", str(student_data.get('mathematics', student_data.get('maths', '0'))), "-", 
             str(student_data.get('mathematics', student_data.get('maths', '0'))), "P"),
            ("SCIENCE", str(student_data.get('science', '0')), "-", str(student_data.get('science', '0')), "P"),
            ("SOCIAL SCIENCE", str(student_data.get('social_science', student_data.get('social', '0'))), "-", 
             str(student_data.get('social_science', student_data.get('social', '0'))), "P"),
        ]
        
        row_y = table_y - 1.2*cm
        for sub in subjects:
            # Alternate row background
            if subjects.index(sub) % 2 == 0:
                c.setFillColor(colors.HexColor('#f0f0f0'))
                c.rect(2.5*cm, row_y - 0.15*cm, width - 5*cm, 0.6*cm, fill=1)
            
            c.setFillColor(colors.black)
            for i, value in enumerate(sub):
                c.drawString(x_positions[i], row_y, value)
            row_y -= 0.7*cm
        
        # ---------- TOTAL MARKS ----------
        c.setFont("Helvetica-Bold", 11)
        total_marks = student_data.get('total_marks', student_data.get('total', '0'))
        c.drawString(2.5*cm, row_y - 0.8*cm, f"TOTAL MARKS : {total_marks}")
        
        # Percentage and Grade
        percentage = student_data.get('percentage', '0')
        grade = student_data.get('grade', 'N/A')
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2.5*cm, row_y - 1.5*cm, f"PERCENTAGE : {percentage}%")
        c.drawString(10*cm, row_y - 1.5*cm, f"GRADE : {grade}")
        
        # ---------- QR CODE ----------
        if qr_path and os.path.exists(qr_path):
            try:
                c.drawImage(qr_path, width - 4.5*cm, 3*cm, 
                           width=3*cm, height=3*cm)
                c.setFont("Helvetica", 7)
                c.drawCentredString(width - 3*cm, 2.5*cm, "Scan to Verify")
            except:
                pass
        
        # ---------- FOOTER ----------
        c.setFont("Helvetica", 8)
        c.drawString(2.5*cm, 2*cm, f"Issue Date: {datetime.now().strftime('%d-%b-%Y')}")
        c.drawString(2.5*cm, 1.5*cm, "This is a digitally generated certificate")
        
        # Verification status
        c.setFillColor(colors.HexColor('#00AA00'))
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(width - 2.5*cm, 2*cm, "✓ VERIFIED")
        
        # Signature
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 8)
        c.drawRightString(width - 2.5*cm, 3.5*cm, "_____________________")
        c.drawRightString(width - 2.5*cm, 3*cm, "Controller of Examinations")
        
        c.showPage()
        c.save()
        return filepath
    
    def generate_12th_certificate(self, student_data, cert_id, qr_path=None):
        """
        Generate 12th Standard DigiLocker-style Certificate
        """
        filename = f"{cert_id}_12th.pdf".replace('/', '_')
        filepath = os.path.join(self.output_folder, filename)
        
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # ---------- OUTER BORDER ----------
        c.setStrokeColor(colors.HexColor('#8B0000'))  # Maroon for 12th
        c.setLineWidth(3)
        c.rect(1*cm, 1*cm, width - 2*cm, height - 2*cm)
        
        c.setLineWidth(1)
        c.rect(1.2*cm, 1.2*cm, width - 2.4*cm, height - 2.4*cm)
        
        # ---------- HEADER ----------
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height - 3*cm, "☸")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2, height - 3.8*cm,
                           "STATE BOARD OF HIGHER SECONDARY EXAMINATIONS")
        
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height - 4.5*cm,
                           "DEPARTMENT OF GOVERNMENT EXAMINATIONS, TAMIL NADU")
        
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(width/2, height - 5.5*cm,
                           "HIGHER SECONDARY CERTIFICATE")
        
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width/2, height - 6.2*cm, "XII STANDARD")
        
        # Certificate Number
        c.setFont("Helvetica", 9)
        c.drawRightString(width - 2*cm, height - 2*cm, f"Certificate No: {cert_id}")
        
        # ---------- STUDENT DETAILS ----------
        y = height - 7.5*cm
        gap = 0.7*cm
        
        details = [
            ("NAME OF THE CANDIDATE", student_data.get('name', 'N/A').upper()),
            ("REGISTER NUMBER", student_data.get('student_id', 'N/A').upper()),
            ("DATE OF BIRTH", str(student_data.get('dob', 'N/A'))),
            ("STREAM", student_data.get('stream', 'SCIENCE').upper()),
            ("SESSION", f"{student_data.get('board', 'STATE BOARD')} - {student_data.get('year_of_passing', '2024')}"),
            ("SCHOOL NAME", student_data.get('school_name', 'N/A').upper())
        ]
        
        for label, value in details:
            c.setFont("Helvetica-Bold", 9)
            c.drawString(2.5*cm, y, f"{label}")
            c.setFont("Helvetica", 9)
            c.drawString(2.5*cm, y - 0.35*cm, f": {value}")
            y -= gap
        
        # ---------- MARKS TABLE ----------
        table_y = y - 1*cm
        
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor('#8B0000'))
        c.rect(2.5*cm, table_y - 0.5*cm, width - 5*cm, 0.7*cm, fill=1)
        
        c.setFillColor(colors.white)
        headers = ["SUBJECT", "THEORY", "PRACTICAL", "TOTAL", "RESULT"]
        x_positions = [3*cm, 9*cm, 11.5*cm, 14*cm, 16.5*cm]
        
        for i, header in enumerate(headers):
            c.drawString(x_positions[i], table_y - 0.25*cm, header)
        
        # Table rows for Science stream
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        
        subjects = [
            ("TAMIL", str(student_data.get('tamil', '0')), "-", str(student_data.get('tamil', '0')), "P"),
            ("ENGLISH", str(student_data.get('english', '0')), "-", str(student_data.get('english', '0')), "P"),
            ("PHYSICS", str(student_data.get('physics', '0')), "-", str(student_data.get('physics', '0')), "P"),
            ("CHEMISTRY", str(student_data.get('chemistry', '0')), "-", str(student_data.get('chemistry', '0')), "P"),
            ("MATHEMATICS", str(student_data.get('mathematics', student_data.get('maths', '0'))), "-",
             str(student_data.get('mathematics', student_data.get('maths', '0'))), "P"),
            ("COMPUTER SCIENCE", str(student_data.get('computer_science', '0')), "-", 
             str(student_data.get('computer_science', '0')), "P"),
        ]
        
        row_y = table_y - 1.2*cm
        for sub in subjects:
            if subjects.index(sub) % 2 == 0:
                c.setFillColor(colors.HexColor('#f0f0f0'))
                c.rect(2.5*cm, row_y - 0.15*cm, width - 5*cm, 0.6*cm, fill=1)
            
            c.setFillColor(colors.black)
            for i, value in enumerate(sub):
                c.drawString(x_positions[i], row_y, value)
            row_y -= 0.7*cm
        
        # ---------- TOTAL MARKS ----------
        c.setFont("Helvetica-Bold", 11)
        total_marks = student_data.get('total_marks', student_data.get('total', '0'))
        c.drawString(2.5*cm, row_y - 0.8*cm, f"TOTAL MARKS : {total_marks}")
        
        percentage = student_data.get('percentage', '0')
        grade = student_data.get('grade', 'N/A')
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2.5*cm, row_y - 1.5*cm, f"PERCENTAGE : {percentage}%")
        c.drawString(10*cm, row_y - 1.5*cm, f"GRADE : {grade}")
        
        # ---------- QR CODE ----------
        if qr_path and os.path.exists(qr_path):
            try:
                c.drawImage(qr_path, width - 4.5*cm, 3*cm, 
                           width=3*cm, height=3*cm)
                c.setFont("Helvetica", 7)
                c.drawCentredString(width - 3*cm, 2.5*cm, "Scan to Verify")
            except:
                pass
        
        # ---------- FOOTER ----------
        c.setFont("Helvetica", 8)
        c.drawString(2.5*cm, 2*cm, f"Issue Date: {datetime.now().strftime('%d-%b-%Y')}")
        c.drawString(2.5*cm, 1.5*cm, "This is a digitally generated certificate")
        
        c.setFillColor(colors.HexColor('#00AA00'))
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(width - 2.5*cm, 2*cm, "✓ VERIFIED")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 8)
        c.drawRightString(width - 2.5*cm, 3.5*cm, "_____________________")
        c.drawRightString(width - 2.5*cm, 3*cm, "Controller of Examinations")
        
        c.showPage()
        c.save()
        return filepath
    
    def generate_degree_certificate(self, student_data, cert_id, qr_path=None):
        """
        Generate University Degree Certificate
        """
        filename = f"{cert_id}_degree.pdf".replace('/', '_')
        filepath = os.path.join(self.output_folder, filename)
        
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # ---------- DECORATIVE BORDER ----------
        c.setStrokeColor(colors.HexColor('#1a237e'))
        c.setLineWidth(4)
        c.rect(1*cm, 1*cm, width - 2*cm, height - 2*cm)
        
        c.setLineWidth(2)
        c.setStrokeColor(colors.HexColor('#FFD700'))  # Gold
        c.rect(1.3*cm, 1.3*cm, width - 2.6*cm, height - 2.6*cm)
        
        c.setLineWidth(1)
        c.setStrokeColor(colors.HexColor('#1a237e'))
        c.rect(1.5*cm, 1.5*cm, width - 3*cm, height - 3*cm)
        
        # ---------- HEADER ----------
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height - 3*cm, "☸")
        
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height - 4*cm,
                           str(student_data.get('university', 'ANNA UNIVERSITY')).upper())
        
        c.setFont("Helvetica", 11)
        c.drawCentredString(width/2, height - 4.7*cm,
                           str(student_data.get('college_name', 'Engineering College')).upper())
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height - 6*cm, "DEGREE CERTIFICATE")
        
        # Certificate Number
        c.setFont("Helvetica", 9)
        c.drawRightString(width - 2*cm, height - 2*cm, f"Certificate No: {cert_id}")
        
        # ---------- MAIN CONTENT ----------
        y = height - 8*cm
        
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, y, "This is to certify that")
        
        y -= 1.2*cm
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, y, str(student_data.get('name', 'Student Name')).upper())
        
        y -= 1*cm
        c.setFont("Helvetica", 11)
        reg_no = str(student_data.get('student_id', 'N/A'))
        c.drawCentredString(width/2, y, f"Register No: {reg_no}")
        
        y -= 1.2*cm
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, y, "has successfully completed the degree of")
        
        y -= 1.2*cm
        c.setFont("Helvetica-Bold", 14)
        degree = f"{student_data.get('degree', 'Bachelor of Engineering')}"
        c.drawCentredString(width/2, y, degree)
        
        y -= 0.8*cm
        c.setFont("Helvetica-Bold", 13)
        specialization = f"in {student_data.get('specialization', 'Computer Science and Engineering')}"
        c.drawCentredString(width/2, y, specialization)
        
        y -= 1.5*cm
        c.setFont("Helvetica", 11)
        year = str(student_data.get('year_of_passing', '2024'))
        c.drawCentredString(width/2, y, f"in the academic year ending {year}")
        
        # ---------- CGPA & CLASS ----------
        y -= 2*cm
        c.setFont("Helvetica-Bold", 13)
        cgpa = str(student_data.get('cgpa', '0.00'))
        c.drawCentredString(width/2, y, f"CGPA: {cgpa} / 10.00")
        
        y -= 0.8*cm
        class_obtained = str(student_data.get('class', 'First Class with Distinction'))
        c.drawCentredString(width/2, y, f"Class: {class_obtained}")
        
        # ---------- QR CODE ----------
        if qr_path and os.path.exists(qr_path):
            try:
                c.drawImage(qr_path, width - 4.5*cm, 2.5*cm, 
                           width=3*cm, height=3*cm)
                c.setFont("Helvetica", 7)
                c.drawCentredString(width - 3*cm, 2*cm, "Scan to Verify")
            except:
                pass
        
        # ---------- FOOTER & SIGNATURES ----------
        c.setFont("Helvetica", 9)
        c.drawCentredString(width/2, 3.5*cm, f"Date of Issue: {datetime.now().strftime('%d %B %Y')}")
        
        c.setFont("Helvetica", 8)
        c.drawString(3*cm, 2.5*cm, "____________________")
        c.drawString(3*cm, 2*cm, "Principal")
        
        c.drawRightString(width - 3*cm, 2.5*cm, "____________________")
        c.drawRightString(width - 3*cm, 2*cm, "Controller of Examinations")
        
        c.showPage()
        c.save()
        return filepath