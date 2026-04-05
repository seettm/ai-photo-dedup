#!/usr/bin/env python3
"""
AI Photo Dedup - CLI Entry Point
AI 智能清理重复照片工具
"""
import click
import sys
from pathlib import Path

from scanner import PhotoScanner
from comparator import PhotoComparator
from cleaner import PhotoCleaner
from reporter import generate_report
from models import AIFeatureExtractor
from utils import setup_logging, parse_size


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """🧹 AI Photo Dedup - 智能重复照片清理工具"""
    pass


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--threshold", "-t", default=0.9, help="相似度阈值 (0-1)")
@click.option("--mode", "-m", type=click.Choice(["hash", "ai"]), default="hash", help="检测模式")
@click.option("--hash-type", type=click.Choice(["phash", "dhash", "ahash", "all"]), default="all", help="哈希算法")
@click.option("--workers", "-w", default=4, help="线程数")
@click.option("--extensions", "-e", multiple=True, default=["jpg", "jpeg", "png", "webp", "heic"], help="支持的图片格式")
def scan(directory, threshold, mode, hash_type, workers, extensions):
    """扫描目录，查找重复照片"""
    logger = setup_logging()
    logger.info(f"开始扫描目录: {directory}")
    
    scanner = PhotoScanner(extensions=extensions, workers=workers)
    files = scanner.scan(directory)
    logger.info(f"找到 {len(files)} 张照片")
    
    if mode == "ai":
        comparator = PhotoComparator(mode="ai")
        extractor = AIFeatureExtractor()
    else:
        comparator = PhotoComparator(mode="hash", hash_type=hash_type)
    
    duplicates = comparator.find_duplicates(files, threshold)
    
    click.echo(f"\n找到 {len(duplicates)} 组重复照片:")
    for i, dup_group in enumerate(duplicates, 1):
        click.echo(f"\n  组 {i}: {len(dup_group)} 张照片")
        for f in dup_group:
            click.echo(f"    - {f.name} ({parse_size(f.stat().st_size)})")


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--threshold", "-t", default=0.9, help="相似度阈值 (0-1)")
@click.option("--mode", "-m", type=click.Choice(["hash", "ai"]), default="hash", help="检测模式")
@click.option("--keep-best", type=click.Choice(["quality", "size", "first"]), default="quality", help="保留策略")
@click.option("--dry-run", is_flag=True, help="仅扫描，不执行")
@click.option("--workers", "-w", default=4, help="线程数")
def clean(directory, threshold, mode, keep_best, dry_run, workers):
    """扫描并自动清理重复照片"""
    logger = setup_logging()
    
    scanner = PhotoScanner(workers=workers)
    files = scanner.scan(directory)
    
    if mode == "ai":
        comparator = PhotoComparator(mode="ai")
    else:
        comparator = PhotoComparator(mode="hash")
    
    duplicates = comparator.find_duplicates(files, threshold)
    
    cleaner = PhotoCleaner(keep_strategy=keep_best)
    results = cleaner.clean(duplicates, directory, dry_run=dry_run)
    
    click.echo(f"\n清理完成！共处理 {len(results)} 组重复照片")
    click.echo(f"移动 {results.get('moved', 0)} 张到回收文件夹")
    click.echo(f"保留 {results.get('kept', 0)} 张最佳照片")


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--output", "-o", default="dedup_report.html", help="报告输出路径")
@click.option("--threshold", "-t", default=0.9, help="相似度阈值")
@click.option("--open-browser", is_flag=True, help="生成后自动打开浏览器")
def report(directory, output, threshold, open_browser):
    """生成 HTML 格式的重复照片报告"""
    logger = setup_logging()
    
    scanner = PhotoScanner()
    files = scanner.scan(directory)
    
    comparator = PhotoComparator()
    duplicates = comparator.find_duplicates(files, threshold)
    
    generate_report(duplicates, output)
    logger.info(f"报告已生成: {output}")
    
    if open_browser:
        click.launch(output)


if __name__ == "__main__":
    cli()
