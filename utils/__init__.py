import qrcode
import os
from io import BytesIO

def generate_qr_code(data, save_path=None):
    """
    Generate QR code for certificate verification
    Data should be certificate ID or verification URL
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    if save_path:
        img.save(save_path)
        return save_path
    else:
        # Return as BytesIO object
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

def get_verification_url(certificate_id, base_url="http://localhost:5000"):
    """
    Generate verification URL for QR code
    """
    return f"{base_url}/verify/{certificate_id}"