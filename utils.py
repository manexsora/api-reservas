import base64

def encode_password(password: str) -> str:
    """Codifica la contraseña a Base64."""
    # Convierte string a bytes, codifica, y vuelve a string
    return base64.b64encode(password.encode('utf-8')).decode('utf-8')

def decode_password(encoded_password: str) -> str:
    """Decodifica la contraseña Base64."""
    # Convierte string a bytes, decodifica, y vuelve a string
    return base64.b64decode(encoded_password.encode('utf-8')).decode('utf-8')