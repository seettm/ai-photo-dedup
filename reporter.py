"""
reporter.py - HTML 报告生成器
"""
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_report(duplicate_groups, output_path):
    html = _generate_html(duplicate_groups)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"报告已生成: {output_path}")


def _generate_html(groups):
    from jinja2 import Template
    template = '''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>AI Photo Dedup 报告</title>
<style>body{font-family:sans-serif;background:#f5f5f5;padding:20px}.container{max-width:1200px;margin:0 auto}.group{background:white;padding:20px;margin-bottom:20px;border-radius:8px}.photo{display:inline-block;margin:10px}.photo img{max-width:200px;border-radius:6px}</style>
</head>
<body><div class="container"><h1>AI Photo Dedup 报告</h1>
<p>找到 {{ total_groups }} 组重复照片</p>
{% for group in groups %}<div class="group"><h2>组 {{ loop.index }} ({{ group|length }} 张)</h2>{% for photo in group %}<div class="photo"><div>{{ photo.name }}</div></div>{% endfor %}</div>{% endfor %}</div></body>
</html>'''
    return Template(template).render(groups=groups, total_groups=len(groups))
