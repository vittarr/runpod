#!/usr/bin/env python3
"""
Model download utility for RunPod AI worker.

This module provides functions for downloading models from Hugging Face and Civitai.
"""

import subprocess
from pathlib import Path

from runpod import RunpodLogger

logger = RunpodLogger()

def download_huggingface_model(repo_id: str, target_dir: str, token: str = None) -> str:
    """Download a model from Hugging Face if not already present."""
    logger.info(f"[DOWNLOAD HF] Starting download for {repo_id}...")
    model_path = Path(target_dir) / repo_id.split('/')[-1]
    if not model_path.exists():
        # Use git clone for Hugging Face model download
        if token:
            url = f"https://{token}@huggingface.co/{repo_id}.git"
        else:
            url = f"https://huggingface.co/{repo_id}.git"
        logger.info(f"[DOWNLOAD HF] Cloning {repo_id} from {url} to {model_path} ...")
        subprocess.run(["git", "clone", "--depth", "1", url, str(model_path)], check=True)
    return str(model_path)

def download_civitai_model(model_id: int, filename: str, target_dir: str, token: str = None) -> str:
    """Download a model from Civitai if not already present."""
    logger.info(f"[DOWNLOAD Civitai] Starting download for {model_id}...")
    model_path = Path(target_dir) / filename
    if not model_path.exists():
        url = f"https://civitai.com/api/download/models/{model_id}?token={token}"
        logger.info(f"[DOWNLOAD Civitai] Downloading {filename} from {url} ...")
        subprocess.run(['curl', '-L', '-o', str(model_path), url], check=True)
    return str(model_path)