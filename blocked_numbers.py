# blocked_numbers.py

blocked_numbers = [
    "371",   # Numeri che contengono "371"
    "+39"    # Numeri che contengono "+39"
]

def is_blocked_number(phone_number):
    for number in blocked_numbers:
        if number in phone_number:
            return True
    return False
