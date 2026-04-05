"""
cleaner.py - 照片清理执行器
将重复照片移动到回收文件夹
"""
import logging
import shutil
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class PhotoCleaner:
    """照片清理执行器"""
    
    def __init__(self, keep_strategy="quality"):
        self.keep_strategy = keep_strategy
    
    def clean(self, duplicate_groups, base_directory, dry_run=False):
        base_directory = Path(base_directory)
        trash_dir = base_directory / ".dedup_trash"
        
        if not dry_run:
            trash_dir.mkdir(exist_ok=True)
            logger.info(f"回收文件夹: {trash_dir}")
        
        results = {"groups": len(duplicate_groups), "moved": 0, "kept": 0, "errors": 0}
        
        for group in duplicate_groups:
            to_keep, to_move = self._decide(group)
            
            if not dry_run:
                for path in to_move:
                    try:
                        dest = trash_dir / path.name
                        if dest.exists():
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            dest = trash_dir / f"{timestamp}_{path.name}"
                        shutil.move(str(path), str(dest))
                        results["moved"] += 1
                        logger.info(f"移动: {path.name} -> {dest}")
                    except Exception as e:
                        logger.error(f"移动失败 {path.name}: {e}")
                        results["errors"] += 1
            
            results["kept"] += len(to_keep)
        
        logger.info(f"清理完成: 保留 {results['kept']} 张，移动 {results['moved']} 张")
        return results
    
    def _decide(self, group):
        if self.keep_strategy == "first":
            return [group[0]], group[1:]
        
        if self.keep_strategy == "size":
            sorted_group = sorted(group, key=lambda p: p.stat().st_size, reverse=True)
            return [sorted_group[0]], sorted_group[1:]
        
        from PIL import Image
        best = None
        best_score = -1
        
        for path in group:
            try:
                with Image.open(path) as img:
                    score = img.width * img.height
                    if score > best_score:
                        best_score = score
                        best = path
            except Exception:
                continue
        
        if best is None:
            sorted_group = sorted(group, key=lambda p: p.stat().st_size, reverse=True)
            return [sorted_group[0]], sorted_group[1:]
        
        to_move = [p for p in group if p != best]
        return [best], to_move
