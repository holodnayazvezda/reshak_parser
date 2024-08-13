import requests
import base64
import io

from config import get_headers


async def encode_image_to_base64(url: str) -> str:
    try:
        r = requests.get(url, headers=await get_headers())
        if r.status_code == 200:
            image_content = r.content
            base64_encoded = str(base64.b64encode(image_content))
            return base64_encoded
        else:
            return ""
    except Exception:
        return ""


async def decode_base64_image(base64_image: str) -> io.BytesIO:
    image_data = base64.b64decode(base64_image)
    image = io.BytesIO(image_data)
    image.seek(0)
    return image
