import re

def est_code_colis(message):
    pattern = r'CTX[0-9]+'
    return re.match(pattern,message.upper().strip())
