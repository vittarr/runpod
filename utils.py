import base64
from io import BytesIO
from PIL import Image

def decode_base64_image(base64_str: str) -> Image.Image:
    return Image.open(BytesIO(base64.b64decode(base64_str.split(",")[-1])))

def encode_base64_image(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
