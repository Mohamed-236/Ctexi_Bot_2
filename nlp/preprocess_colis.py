import re

def est_code_colis(message):
    pattern = r'CTX\d+'
    match = re.search(pattern, message.upper())

    if match:
        return match.group()  # ✅ STRING
    return None