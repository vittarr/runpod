import torch
from diffusers import StableDiffusionImg2ImgPipeline
from diffusers.utils import load_image
from PIL import Image
from runpod.serverless.modules.rp_logger import RunPodLogger

# Configure logging
logger = RunPodLogger()

class StableDiffusionModel:
    # Default model ID
    DEFAULT_MODEL_ID = "black-forest-labs/FLUX.1-Kontext-dev"
    
    def __init__(self, model_id: str = None):
        """Initialize the Stable Diffusion model.
        
        Args:
            model_id (str, optional): The model ID to load from HuggingFace or local path.
                                      If not provided, uses the default model.
        """
        self.model_id = model_id if model_id else self.DEFAULT_MODEL_ID
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = None
        
    def load_model(self):
        """Load the model into memory."""
        logger.info(f"Loading model {self.model_id} on {self.device}...")
        self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        ).to(self.device)
        
        # Optimize for memory
        self.pipe.enable_attention_slicing()
        logger.info("Model loaded successfully")
        return self
        
    def run_img2img(self, image, prompt, negative_prompt=None, 
                   guidance_scale=None, strength=None):
        """Run image-to-image generation.
        
        Args:
            image: Input image (PIL Image or path or URL)
            prompt (str): Text prompt for generation
            negative_prompt (str, optional): Negative prompt
            guidance_scale (float, optional): Guidance scale for generation
            strength (float, optional): Strength for img2img transformation
            
        Returns:
            Generated image
        """
        if self.pipe is None:
            self.load_model()
            
        # Handle different image input types
        if isinstance(image, str):
            # Assume it's a path or URL
            image = load_image(image).convert("RGB")
        elif not isinstance(image, Image.Image):
            raise ValueError("Image must be a PIL Image or a string path/URL")
                        
        # Run inference
        result = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=image,
            strength=strength,
            guidance_scale=guidance_scale,
        )
        
        return result
