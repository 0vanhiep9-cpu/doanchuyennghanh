import re
from django.core.exceptions import ValidationError

def validate_gmail_email(email):
    """
    Kiểm tra email phải có đuôi @gmail.com
    """
    if not email.endswith('@gmail.com'):
        raise ValidationError('Email phải có đuôi @gmail.com')
    return True

def validate_password_strength(password):
    """
    Kiểm tra mật khẩu phải có cả chữ và số, tối thiểu 6 ký tự
    """
    errors = []
    
    if len(password) < 6:
        errors.append('Mật khẩu phải có ít nhất 6 ký tự')
    
    if not re.search(r'[A-Za-z]', password):
        errors.append('Mật khẩu phải chứa ít nhất một chữ cái')
    
    if not re.search(r'\d', password):
        errors.append('Mật khẩu phải chứa ít nhất một chữ số')
    
    if errors:
        raise ValidationError(errors)
    
    return True

def validate_registration_data(data):
    """
    Validation tổng hợp cho dữ liệu đăng ký
    """
    errors = []
    
    # Kiểm tra các trường bắt buộc
    required_fields = ['hoten', 'tendangnhap', 'password', 'email']
    for field in required_fields:
        if not data.get(field):
            errors.append(f'{field} là trường bắt buộc')
    
    # Kiểm tra email
    email = data.get('email', '')
    if email:
        try:
            validate_gmail_email(email)
        except ValidationError as e:
            errors.extend(e.messages)
    
    # Kiểm tra mật khẩu
    password = data.get('password', '')
    if password:
        try:
            validate_password_strength(password)
        except ValidationError as e:
            errors.extend(e.messages)
    
    # Kiểm tra tên đăng nhập
    tendangnhap = data.get('tendangnhap', '')
    if tendangnhap:
        if len(tendangnhap) < 3:
            errors.append('Tên đăng nhập phải có ít nhất 3 ký tự')
        if not re.match(r'^[a-zA-Z0-9_]+$', tendangnhap):
            errors.append('Tên đăng nhập chỉ được chứa chữ cái, số và dấu gạch dưới')
    
    return errors