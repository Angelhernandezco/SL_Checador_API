import base64
from typing import Optional

def photo_to_base64(photo: Optional[bytes]) -> Optional[str]:
    """
    Convierte un BLOB de foto a base64.
    Si la foto es None, devuelve None.
    """
    if photo:
        return base64.b64encode(photo).decode("utf-8")
    return None
