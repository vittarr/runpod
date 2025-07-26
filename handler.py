import runpod
from pipeline import run_img2img
from utils import decode_base64_image, encode_base64_image

def handler(job):
    input = job["input"]
    prompt = input.get("prompt", "cyberpunk cat in neon style")
    base64_image = input.get("image")

    if not base64_image:
        return {"error": "No image input provided"}

    init_image = decode_base64_image(base64_image)

    result_image = run_img2img(prompt, init_image)
    result_base64 = encode_base64_image(result_image)

    return {"image": result_base64}

runpod.serverless.start({"handler": handler})
