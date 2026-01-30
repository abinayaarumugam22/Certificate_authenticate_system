import hashlib
import os

def generate_hash(file_path):
    """
    Generate SHA-256 hash from PDF file
    This hash is used to verify certificate authenticity
    """
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error generating hash: {e}")
        return None

def generate_hash_from_data(data):
    """
    Generate hash directly from data (for verification)
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()

def verify_hash(file_path, original_hash):
    """
    Verify if file hash matches original hash
    Returns True if valid, False if tampered
    """
    current_hash = generate_hash(file_path)
    
    if current_hash is None:
        return False
    
    return current_hash == original_hash