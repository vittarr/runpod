#!/usr/bin/env python3
# file handler.py
"""
RunPod Serverless Handler for AI image processing.

This module provides the handler function for processing image generation requests
using Stable Diffusion models on RunPod's serverless infrastructure.
"""

import os
import time
from pathlib import Path

import runpod
from runpod import RunpodLogger
from runpod.serverless.utils.rp_validator import validate

from model import StableDiffusionModel

logger = RunpodLogger()

# Model configuration
MODEL_DIR = Path(os.getenv("MODEL_STORAGE_PATH", "/runpod-volume/my_volume"))
MODEL_DIR.mkdir(parents=True, exist_ok=True)

model = None

def get_model_path(model_id: str) -> str:
    """Get the local path for a model, downloading if necessary."""
    # Simple path construction
    if '/' in model_id:  # HuggingFace format
        model_name = model_id.split('/')[-1]
        return str(MODEL_DIR / model_name)
    else:  # Local path or Civitai filename
        return str(MODEL_DIR / model_id)


from download import download_huggingface_model, download_civitai_model

def init_model(model_id: str = None):
    """Initialize the model, downloading if needed."""
    global model
    
    if model is None:
        model_path = get_model_path(model_id)
        if not os.path.exists(model_path):
            if '/' in model_id:  # HuggingFace
                download_huggingface_model(
                    repo_id=model_id,
                    target_dir=str(MODEL_DIR),
                    token=os.getenv("HUGGINGFACE_TOKEN")
                )
            else:
                logger.warning("Civitai download requires model_id and filename mapping. Skipping download.")
        logger.info(f"Initializing model: {model_id} at {model_path}")
        model = StableDiffusionModel(model_path)
    return model


def handler(job):
    """Handler function for processing RunPod job requests.
    
    Args:
        job (dict): Job input from RunPod
        
    Returns:
        dict: Job output with generated image or error
    """
    start_time = time.time()
    
    MODEL_ID="runwayml/stable-diffusion-v1-5"

    try:
        # Validate input
        validation_result = validate(job["input"], IMAGE_GENERATION_SCHEMA)
        if "errors" in validation_result:
            return {"error": validation_result["errors"]}
        
        input_data = validation_result["validated_input"]
                
        # Initialize model (using model_id if provided)
        sd_model = init_model(MODEL_ID)
        
        # Generate image - pass image input directly to the model
        result = sd_model.run_img2img(
            image=input_data["image"],
            prompt=input_data["prompt"],
            negative_prompt=input_data["negative_prompt"],
            guidance_scale=input_data["guidance_scale"],
            strength=input_data["strength"]
        )
        
        # Return result
        return {
            "image": encode_base64_image(result.images[0]),
            "prompt": input_data["prompt"],
            "processing_time": time.time() - start_time
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return {"error": str(e)}


# Function process_image_input removed as the model now handles image input directly


# Start the serverless worker
if __name__ == "__main__":
    logger.info("Starting RunPod Serverless Worker")
    runpod.serverless.start({"handler": handler})

