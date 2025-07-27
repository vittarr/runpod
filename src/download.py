#!/usr/bin/env python3
# file download.py
"""
Download script for RunPod AI worker.

This script downloads models from Hugging Face and Civitai for use in the RunPod worker.
It can be run as a standalone script or imported as a module.
"""

import argparse
import os
import requests
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict
from runpod.serverless.modules.rp_logger import RunPodLogger

# Configure logging
logger = RunPodLogger()

# Default configuration
CONFIG = {
    # Model settings
    "civitai_token": "",
    "target_dir": "/runpod-volume/my_volume",
    
    # Model lists
    "civitai_models": [
        # Format: (model_id, filename)
        # Example: (12345, "model.safetensors")
    ],
    "huggingface_models": [
        # Format: "repo_id"
        "runwayml/stable-diffusion-v1-5",  # Default model
        "black-forest-labs/FLUX.1-Kontext-dev"
    ]
}


def load_config() -> Dict:
    """Load configuration from environment variables.
    
    Returns:
        Dict containing configuration
    """
    # Start with a copy of the default configuration
    config = CONFIG.copy()
    
    # Override with environment variables
    if "CIVITAI_TOKEN" in os.environ:
        config["civitai_token"] = os.environ["CIVITAI_TOKEN"]
                
    return config


def download_civitai_models(models: List[Tuple[int, str]], token: str, target_dir: str) -> None:
    """Download models from Civitai.
    
    Args:
        models: List of tuples (model_id, filename)
        token: Civitai API token
        target_dir: Directory to save models
    """
    base_url = "https://civitai.com/api/download/models"
    target_path = Path(target_dir)
    
    for model_id, filename in models:
        path = target_path / filename
        
        if path.exists():
            logger.info(f"Model {filename} already exists, skipping")
            continue
            
        
        try:
            url = f"{base_url}/{model_id}?token={token}"
            logger.info(f"Downloading {filename} from Civitai...")
            subprocess.run(["curl", "-L", "-o", str(path), url], check=True)
            logger.info(f"Successfully downloaded {filename}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download {filename}: {e}")


def download_huggingface_models(repos: List[str], target_dir: str) -> None:
    """Download models from Hugging Face.
    
    Args:
        repos: List of Hugging Face repository IDs
        target_dir: Directory to save models
    """
    target_path = Path(target_dir)
    
    for repo in repos:
        model_name = repo.split("/")[-1]
        path = target_path / model_name
        
        if path.exists():
            logger.info(f"Model {model_name} already exists, skipping")
            continue
            
        try:
            logger.info(f"Downloading {repo} from Hugging Face...")
            from huggingface_hub import snapshot_download
            
            # Use the Python API instead of CLI
            snapshot_download(
                repo_id=repo,
                cache_dir=str(path),
                local_dir=str(path),
                local_dir_use_symlinks=False if 'local_dir_use_symlinks' in snapshot_download.__code__.co_varnames else None,
                resume_download=True
            )
            logger.info(f"Successfully downloaded {repo}")
        except Exception as e:
            logger.error(f"Failed to download {repo}: {e}")
            return False


def main(config):
    """Main function to download models.
    
    Args:
        config: Configuration dictionary
    """
    # Create target directory if it doesn't exist
    target_dir = Path(config["target_dir"])
    target_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Using target directory: {target_dir}")
    
    # Download models from Civitai
    civitai_models = config["civitai_models"]
    civitai_token = config["civitai_token"]
    
    if civitai_models and civitai_token:
        download_civitai_models(civitai_models, civitai_token, config["target_dir"])
    
    # Download models from HuggingFace
    huggingface_models = config["huggingface_models"]
    if huggingface_models:
        download_huggingface_models(huggingface_models, config["target_dir"])
    
    logger.info("Download process completed")


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Download models for RunPod AI worker")
    parser.add_argument(
        "-t", "--token",
        help="Civitai API token (overrides environment variables)"
    )
    parser.add_argument(
        "-d", "--dir",
        help="Target directory for downloaded models (overrides environment variables)"
    )
    
    # Parse arguments and load configuration
    args = parser.parse_args()
    config = load_config()
    
    # Apply command line overrides
    if args.token:
        config["civitai_token"] = args.token
    
    if args.dir:
        config["target_dir"] = args.dir
    
    # Run the main function
    main(config)