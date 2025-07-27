#!/usr/bin/env python3
# file handler.py
"""
RunPod Serverless Handler for AI image processing.

This module provides the handler function for processing image generation requests
using Stable Diffusion models on RunPod's serverless infrastructure.
"""

import time
import runpod
from runpod.serverless.utils.rp_validator import validate
from runpod.serverless.modules.rp_logger import RunPodLogger

# Import our modules
from schema import IMAGE_GENERATION_SCHEMA
from model import StableDiffusionModel
from utils import encode_base64_image

# Configure logging
logger = RunPodLogger()

# Initialize the model (will be loaded on first request)
model = None


def init_model(model_id=None):
    """Initialize the model if not already loaded or if a different model is requested.
    
    Args:
        model_id (str, optional): ID of the model to load. If None, uses the default model.
        
    Returns:
        Initialized StableDiffusionModel instance
    """
    global model
    
    # Initialize or switch model if needed
    if model is None or (model_id and model.model_id != model_id):
        model_name = model_id if model_id else StableDiffusionModel.DEFAULT_MODEL_ID
        logger.info(f"{'Initializing' if model is None else 'Switching to'} model: {model_name}")
        model = StableDiffusionModel(model_id=model_id)
        
    return model


def handler(job):
    """Handler function for processing RunPod job requests.
    
    Args:
        job (dict): Job input from RunPod
        
    Returns:
        dict: Job output with generated image or error
    """
    start_time = time.time()
    
    try:
        # Validate input
        validation_result = validate(job["input"], IMAGE_GENERATION_SCHEMA)
        if "errors" in validation_result:
            return {"error": validation_result["errors"]}
        
        input_data = validation_result["validated_input"]
        
        # Initialize model (using model_id if provided, otherwise using default)
        sd_model = init_model(input_data.get("model_id"))
        
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

