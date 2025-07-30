#!/usr/bin/env python3
"""
Model download utility for RunPod AI worker.

This module provides functions for downloading models from Hugging Face and Civitai.
"""

import os
import shutil
import subprocess
from huggingface_hub import snapshot_download
from pathlib import Path
import logging

# Set HF_HUB_CACHE to use the network volume
HF_HUB_CACHE = "/runpod-volume/my_volume/hf_cache"
os.environ["HF_HUB_CACHE"] = HF_HUB_CACHE
# Ensure the cache directory exists
Path(HF_HUB_CACHE).mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("download")
logging.basicConfig(level=logging.INFO)

def log_disk_usage(path, label):
    total, used, free = shutil.disk_usage(path)
    logger.info(f"[DISK USAGE] {label} - Total: {total // (1024**3)}GB, Used: {used // (1024**3)}GB, Free: {free // (1024**3)}GB")


def download_huggingface_model(repo_id: str, target_dir: str, token: str | None = None) -> str:
    """Download a model from Hugging Face if not already present."""
    logger.info(f"[DOWNLOAD HF] Starting download for {repo_id}...")
    target_path = Path(target_dir)

    # Log disk usage before download
    log_disk_usage(target_dir if target_path.exists() else '/', 'Target Directory')
    log_disk_usage(HF_HUB_CACHE, 'HF_HUB_CACHE')

    if not target_path.exists() or not any(target_path.iterdir()):
        logger.info(f"[DOWNLOAD HF] Deleting files in {target_dir} ...")
        subprocess.run(['rm', '-rf', str(target_dir)], check=True)
        target_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"[DOWNLOAD HF] Downloading {repo_id} to {target_dir} ...")
        actual_model_path = snapshot_download(
            repo_id=repo_id,
            local_dir=str(target_path),
            resume_download=True,
            token=token
        )
        logger.info(f"[DOWNLOAD HF] snapshot_download returned path: {actual_model_path}")
        # Log directory contents after download
        files = list(Path(actual_model_path).glob('**/*'))
        logger.info(f"[DOWNLOAD HF] Files in {actual_model_path} after download: {[str(f) for f in files]}")
        log_disk_usage(target_dir, 'Target Directory (after download)')
        log_disk_usage(HF_HUB_CACHE, 'HF_HUB_CACHE (after download)')
        # Warn if directory is empty or missing expected files
        if not files:
            logger.warning(f"[DOWNLOAD HF] Directory {actual_model_path} is empty after download!")
        else:
            expected_files = ['config.json', 'model_index.json']
            present_files = [f.name for f in files]
            for ef in expected_files:
                if ef not in present_files:
                    logger.warning(f"[DOWNLOAD HF] Expected file {ef} not found in {actual_model_path}!")
    else:
        actual_model_path = str(target_path)
    return actual_model_path



def download_civitai_model(model_id: int, filename: str, target_dir: str, token: str | None = None) -> str:
    """Download a model from Civitai if not already present."""
    logger.info(f"[DOWNLOAD Civitai] Starting download for {model_id}...")
    model_path = Path(target_dir) / filename
    if not model_path.exists():
        url = f"https://civitai.com/api/download/models/{model_id}?token={token}"
        logger.info(f"[DOWNLOAD Civitai] Downloading {filename} from {url} ...")
        subprocess.run(['curl', '-L', '-o', str(model_path), url], check=True)
    return str(model_path)