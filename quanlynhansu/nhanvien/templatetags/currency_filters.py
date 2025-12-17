from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def currency_vnd(value):
    """
    Định dạng số tiền thành VNĐ với dấu phẩy phân cách
    Ví dụ: 50000000 -> 50,000,000 VNĐ
    """
    if value is None or value == '':
        return '--'
    
    try:
        # Chuyển về số nguyên và định dạng
        amount = int(float(value))
        if amount == 0:
            return '0 VNĐ'
        
        # Sử dụng intcomma để thêm dấu phẩy
        formatted = intcomma(amount)
        return f"{formatted} VNĐ"
    except (ValueError, TypeError):
        return str(value)

@register.filter
def currency_vnd_short(value):
    """
    Định dạng số tiền ngắn gọn (không có VNĐ)
    Ví dụ: 50000000 -> 50,000,000
    """
    if value is None or value == '':
        return '--'
    
    try:
        amount = int(float(value))
        return intcomma(amount)
    except (ValueError, TypeError):
        return str(value)

@register.filter
def currency_with_sign(value):
    """
    Định dạng số tiền với dấu + hoặc -
    Ví dụ: 50000000 -> +50,000,000 VNĐ, -50000000 -> -50,000,000 VNĐ
    """
    if value is None or value == '':
        return '--'
    
    try:
        amount = float(value)
        if amount == 0:
            return '0 VNĐ'
        
        formatted = intcomma(int(abs(amount)))
        sign = '+' if amount > 0 else '-'
        return f"{sign}{formatted} VNĐ"
    except (ValueError, TypeError):
        return str(value)

@register.filter
def currency_color_class(value):
    """
    Trả về CSS class dựa trên giá trị tiền (dương/âm/zero)
    """
    try:
        amount = float(value)
        if amount > 0:
            return 'text-green-600'
        elif amount < 0:
            return 'text-red-600'
        else:
            return 'text-gray-600'
    except (ValueError, TypeError):
        return 'text-gray-600'