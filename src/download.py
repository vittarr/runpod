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


def download_huggingface_model(repo_id: str, target_dir: str, token: str) -> str:
    """Download a model from Hugging Face if not already present."""
    logger.info(f"[DOWNLOAD HF] Starting download for {repo_id}...")
    target_path = Path(target_dir)
    if not target_path.exists() or not any(target_path.iterdir()):
        logger.info(f"[DOWNLOAD HF] Deleting files in {target_dir} ...")
        subprocess.run(['rm', '-rf', str(target_dir)], check=True)
        target_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"[DOWNLOAD HF] Downloading {repo_id} to {target_dir} ...")
        snapshot_download(
            repo_id=repo_id,
            local_dir=str(target_path),
            resume_download=True,
            token=token
        )
    return str(target_path)


def download_civitai_model(model_id: int, filename: str, target_dir: str, token: str) -> str:
    """Download a model from Civitai if not already present."""
    logger.info(f"[DOWNLOAD Civitai] Starting download for {model_id}...")
    model_path = Path(target_dir) / filename
    if not model_path.exists():
        url = f"https://civitai.com/api/download/models/{model_id}?token={token}"
        logger.info(f"[DOWNLOAD Civitai] Downloading {filename} from {url} ...")
        subprocess.run(['curl', '-L', '-o', str(model_path), url], check=True)
    return str(model_path)