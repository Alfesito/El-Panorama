import hashlib
import base64
import re

class IDUtils:
    @staticmethod
    def generateshortid(newspaper, datetimestr, title):
        """Genera ID base62 de 6 caracteres único por artículo."""
        content = f"{datetimestr}{title[:30]}{newspaper}"
        hashobj = hashlib.md5(content.encode('utf-8'))
        b64 = base64.b64encode(hashobj.digest()).decode('utf-8')
        # Base62 seguro para URLs
        base62 = re.sub(r'[+/=]', lambda m: {'+':'-', '/':'_', '=':''}[m.group()], b64)
        return base62[:6].upper()
