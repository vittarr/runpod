from diffusers import StableDiffusionImg2ImgPipeline
import torch

# Load once at startup
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")

pipe.enable_attention_slicing()

def run_img2img(prompt: str, init_image, strength=0.75, guidance_scale=7.5):
    return pipe(prompt=prompt, image=init_image, strength=strength, guidance_scale=guidance_scale).images[0]
