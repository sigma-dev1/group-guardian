# voip_check.py

voip_prefixes = ["+1", "+44", "+91", "+81", "+86", "+33", "+49", "+7", "+61", "+55", "+39"]

def check_voip_prefix(phone_number):
    for prefix in voip_prefixes:
        if phone_number.startswith(prefix):
            return True
    return False
