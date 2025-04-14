import re

def is_strong_password(password):
    """Check if the password meets strength requirements."""
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):  # Uppercase letter
        return False
    if not re.search(r'[a-z]', password):  # Lowercase letter
        return False
    if not re.search(r'\d', password):     # Digit
        return False
    if not re.search(r'\W', password):     # Special character
        return False
    return True

def format_singapore_phone(phone):
    """Ensure phone number starts with +65."""
    phone = phone.strip()
    if not phone.startswith('+65'):
        return '+65' + phone
    return phone

def validate_otp(session_otp, input_otp):
    """Match the OTP from session with user input."""
    try:
        return session_otp == int(input_otp)
    except:
        return False

def is_valid_sg_number(phone):
    """Checks for a valid Singapore number, excluding country code."""
    return re.fullmatch(r'[689]\d{7}', phone) is not None
