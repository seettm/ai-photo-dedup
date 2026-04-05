"""
utils.py - 工具函数
"""
import logging
from pathlib import Path


def setup_logging(level=logging.INFO):
    logging.basicConfig(level=level, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    return logging.getLogger(__name__)


def parse_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def get_image_info(path):
    from PIL import Image
    with Image.open(path) as img:
        return {"width": img.width, "height": img.height, "format": img.format, "size": Path(path).stat().st_size}


def is_image_file(path):
    extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".heic"}
    return Path(path).suffix.lower() in extensions
