"""
comparator.py - 照片比较引擎
支持感知哈希和 AI 深度特征两种模式
"""
import logging
from pathlib import Path
from collections import defaultdict

import imagehash
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class PhotoComparator:
    """照片比较引擎"""
    
    def __init__(self, mode="hash", hash_type="all"):
        self.mode = mode
        self.hash_type = hash_type
        self._hash_cache = {}
    
    def find_duplicates(self, file_paths, threshold=0.9):
        if self.mode == "ai":
            return self._find_by_ai_features(file_paths, threshold)
        else:
            return self._find_by_hash(file_paths, threshold)
    
    def _find_by_hash(self, file_paths, threshold):
        logger.info("正在计算感知哈希...")
        hashes = self._compute_hashes(file_paths)
        hamming_threshold = int(64 * (1 - threshold))
        logger.info(f"正在比较 {len(hashes)} 张照片...")
        groups = []
        used = set()
        hashes_list = list(hashes.items())
        for i, (path1, hash1) in enumerate(hashes_list):
            if path1 in used:
                continue
            group = [path1]
            used.add(path1)
            for j, (path2, hash2) in enumerate(hashes_list[i+1:], i+1):
                if path2 in used:
                    continue
                distance = self._hamming_distance(hash1, hash2)
                if distance <= hamming_threshold:
                    group.append(path2)
                    used.add(path2)
            if len(group) > 1:
                groups.append(group)
        logger.info(f"找到 {len(groups)} 组重复照片")
        return groups
    
    def _compute_hashes(self, file_paths):
        hashes = {}
        for path in file_paths:
            if path in self._hash_cache:
                hashes[path] = self._hash_cache[path]
                continue
            try:
                with Image.open(path) as img:
                    if self.hash_type == "phash":
                        h = {"phash": imagehash.phash(img)}
                    elif self.hash_type == "dhash":
                        h = {"dhash": imagehash.dhash(img)}
                    elif self.hash_type == "ahash":
                        h = {"ahash": imagehash.average_hash(img)}
                    else:
                        h = {"phash": imagehash.phash(img), "dhash": imagehash.dhash(img), "ahash": imagehash.average_hash(img)}
                    self._hash_cache[path] = h
                    hashes[path] = h
            except Exception as e:
                logger.warning(f"无法计算哈希 {path}: {e}")
        return hashes
    
    def _hamming_distance(self, hash1, hash2):
        distances = []
        for key in hash1:
            if key in hash2:
                d = hash1[key] - hash2[key]
                distances.append(d)
        return sum(distances) // len(distances) if distances else 64
    
    def _find_by_ai_features(self, file_paths, threshold):
        try:
            from models import AIFeatureExtractor
        except ImportError:
            logger.error("AI 模式需要安装 torch 和 torchvision")
            return []
        extractor = AIFeatureExtractor()
        features = extractor.extract_batch(file_paths)
        logger.info(f"正在计算相似度矩阵...")
        groups = []
        used = set()
        paths = list(features.keys())
        for i, path1 in enumerate(paths):
            if path1 in used:
                continue
            group = [path1]
            used.add(path1)
            vec1 = features[path1]
            for path2 in paths[i+1:]:
                if path2 in used:
                    continue
                vec2 = features[path2]
                similarity = self._cosine_similarity(vec1, vec2)
                if similarity >= threshold:
                    group.append(path2)
                    used.add(path2)
            if len(group) > 1:
                groups.append(group)
        return groups
    
    @staticmethod
    def _cosine_similarity(v1, v2):
        v1 = np.array(v1)
        v2 = np.array(v2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
