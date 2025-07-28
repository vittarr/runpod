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
    model_path = Path(target_dir) / repo_id.split('/')[-1]
    if not model_path.exists():
        try:
            from huggingface_hub import snapshot_download
            logger.info(f"Downloading {repo_id} to {model_path} ...")
            snapshot_download(
                repo_id=repo_id,
                local_dir=str(model_path),
                resume_download=True,
                token=token
            )
        except ImportError:
            logger.info(f"Cloning {repo_id} to {model_path} ...")
            subprocess.run(['git', 'clone', f'https://huggingface.co/{repo_id}', str(model_path)], check=True)
    return str(model_path)

def download_civitai_model(model_id: int, filename: str, target_dir: str, token: str = None) -> str:
    """Download a model from Civitai if not already present."""
    model_path = Path(target_dir) / filename
    if not model_path.exists():
        url = f"https://civitai.com/api/download/models/{model_id}"
        if token:
            url += f"?token={token}"
        logger.info(f"Downloading {filename} from {url} ...")
        subprocess.run(['curl', '-L', '-o', str(model_path), url], check=True)
    return str(model_path)