#!/usr/bin/env python3
"""
Model download utility for RunPod AI worker.

This module provides functions for downloading models from Hugging Face and Civitai.
"""

import subprocess
from huggingface_hub import snapshot_download
from pathlib import Path

import logging

logger = logging.getLogger("download")
logging.basicConfig(level=logging.INFO)


def download_huggingface_model(repo_id: str, target_dir: str, token: str = None) -> str:
    """Download a model from Hugging Face if not already present."""
    logger.info(f"[DOWNLOAD HF] Starting download for {repo_id}...")
    model_path = Path(target_dir) / repo_id.split('/')[-1]
    if not model_path.exists():
        logger.info(f"[DOWNLOAD HF] Downloading {repo_id} to {model_path} ...")
        snapshot_download(
            repo_id=repo_id,
            local_dir=str(model_path),
            resume_download=True,
            token=token
        )
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