import re
def check_str(data):
    if data.isalpha() and not data.isspace():
        return data.lstrip().rstrip()
    else:
        return False

def check_mail(data):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if re.match(regex, data):
        return data.strip()
    else:
        return False

def check_passw(data):
    if data == data.strip():
        return data
    else:
        return False