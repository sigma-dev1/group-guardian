# voip_check.py

voip_prefixes = ["+1", "+44", "+91", "+81", "+86", "+33", "+49", "+7", "+61", "+55", "+39"]

def has_voip_prefix(phone_number):
    return any(phone_number.startswith(prefix) for prefix in voip_prefixes)
