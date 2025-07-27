"""
Schema definitions for RunPod AI worker.

This module contains the input validation schemas used by the handler.
"""

# Input validation schema for image generation
IMAGE_GENERATION_SCHEMA = {
    "image": {
        "type": str, 
        "required": True, 
        "description": "URL or base64 encoded image"
    },
    "prompt": {
        "type": str, 
        "required": True, 
        "description": "Text prompt for image generation"
    },
    "negative_prompt": {
        "type": str, 
        "required": False, 
        "default": None, 
        "description": "Negative text prompt"
    },
    "guidance_scale": {
        "type": float, 
        "required": False, 
        "default": 7.5, 
        "description": "Guidance scale (1-20)"
    },
    "strength": {
        "type": float, 
        "required": False, 
        "default": 0.75, 
        "description": "Transformation strength (0-1)"
    },
}

# Add more schemas here as needed
