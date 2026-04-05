"""
scanner.py - 照片文件扫描器
递归扫描目录，过滤支持的图片格式
"""
import logging
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

logger = logging.getLogger(__name__)

DEFAULT_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp", ".tiff"}

# HEIC 支持依赖 pillow-heif
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False
    logger.warning("pillow-heif not installed, HEIC files will be skipped")


class InvalidImageError(Exception):
    """无效图片文件"""
    pass


class PhotoScanner:
    """照片文件扫描器"""
    
    def __init__(self, extensions=None, workers=4, min_size=1024):
        if extensions:
            self.extensions = {f".{ext.lower()}" for ext in extensions}
        else:
            self.extensions = DEFAULT_EXTENSIONS
        
        self.workers = workers
        self.min_size = min_size
    
    def scan(self, directory):
        directory = Path(directory)
        if not directory.is_dir():
            raise ValueError(f"不是有效目录: {directory}")
        
        candidates = []
        for root, _, files in os.walk(directory):
            for f in files:
                path = Path(root) / f
                if path.suffix.lower() in self.extensions:
                    candidates.append(path)
        
        logger.info(f"找到 {len(candidates)} 个候选图片文件，正在验证...")
        valid_files = self._validate_images(candidates)
        logger.info(f"验证完成，{len(valid_files)} 张有效图片")
        return sorted(valid_files)
    
    def _validate_images(self, file_paths):
        valid = []
        
        def validate(path):
            try:
                if path.stat().st_size < self.min_size:
                    return None, f"文件过小 ({path.stat().st_size} bytes)"
                if path.suffix.lower() in {".heic"} and not HEIC_SUPPORTED:
                    return None, "HEIC 不支持 (安装 pillow-heif)"
                with Image.open(path) as img:
                    img.verify()
                return path, None
            except Exception as e:
                return None, str(e)
        
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(validate, p): p for p in file_paths}
            for future in as_completed(futures):
                path, error = future.result()
                if path:
                    valid.append(path)
                else:
                    logger.debug(f"跳过 {futures[future].name}: {error}")
        
        return valid
