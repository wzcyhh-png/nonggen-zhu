# -*- coding: utf-8 -*-
"""优化版HTTP服务器：gzip压缩 + 浏览器缓存 + 预压缩"""
import http.server
import socketserver
import gzip
import os
import mimetypes
import io
import threading
import re
from pathlib import Path

PORT = 8765
BASE_DIR = r"C:\Users\atmwz\AppData\Roaming\TRAE SOLO CN\ModularData\ai-agent\work-mode-projects\6a60f6e6eedb8709673f2b9d"

# 缓存时间（秒）
CACHE_MAX_AGE_HTML = 0       # HTML不缓存，保证用户总能看到最新
CACHE_MAX_AGE_IMAGES = 86400 * 30  # 图片缓存30天
CACHE_MAX_AGE_JS_CSS = 86400      # JS/CSS缓存1天

# 预压缩文件缓存
precompressed_cache = {}
precompressed_lock = threading.Lock()

def should_gzip(filepath):
    """判断文件是否应该gzip压缩"""
    ext = os.path.splitext(filepath)[1].lower()
    return ext in ('.html', '.css', '.js', '.json', '.svg', '.txt', '.xml', '.webp', '.jpg', '.png')

def get_cache_max_age(filepath):
    """根据文件类型返回缓存时间"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ('.html', '.htm'):
        return CACHE_MAX_AGE_HTML
    elif ext in ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.ico', '.woff', '.woff2'):
        return CACHE_MAX_AGE_IMAGES
    elif ext in ('.js', '.css'):
        return CACHE_MAX_AGE_JS_CSS
    return 3600

class OptimizedHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)
    
    def end_headers(self):
        # 添加缓存头
        filepath = self.path.lstrip('/')
        cache_age = get_cache_max_age(filepath)
        self.send_header('Cache-Control', f'public, max-age={cache_age}')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()
    
    def do_GET(self):
        filepath = self.path.lstrip('/')
        full_path = os.path.join(BASE_DIR, filepath)
        
        if os.path.isfile(full_path):
            self.serve_file(full_path)
        else:
            super().do_GET()
    
    def serve_file(self, full_path):
        """提供文件，支持gzip"""
        try:
            with open(full_path, 'rb') as f:
                raw_data = f.read()
            
            content_type = self.guess_type(full_path)
            
            # 检查客户端是否接受gzip
            accept_encoding = self.headers.get('Accept-Encoding', '')
            
            if 'gzip' in accept_encoding and should_gzip(full_path):
                # 检查预压缩缓存
                cache_key = full_path
                with precompressed_lock:
                    if cache_key in precompressed_cache:
                        gz_data = precompressed_cache[cache_key]
                    else:
                        gz_data = gzip.compress(raw_data, compresslevel=6)
                        # 只缓存小于2MB的压缩结果
                        if len(gz_data) < 2 * 1024 * 1024:
                            precompressed_cache[cache_key] = gz_data
                
                if len(gz_data) < len(raw_data):
                    self.send_response(200)
                    self.send_header('Content-Type', content_type)
                    self.send_header('Content-Encoding', 'gzip')
                    self.send_header('Content-Length', str(len(gz_data)))
                    cache_age = get_cache_max_age(full_path)
                    self.send_header('Cache-Control', f'public, max-age={cache_age}')
                    self.send_header('X-Content-Type-Options', 'nosniff')
                    self.end_headers()
                    self.wfile.write(gz_data)
                    return
            
            # 不压缩或压缩后更大
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(raw_data)))
            cache_age = get_cache_max_age(full_path)
            self.send_header('Cache-Control', f'public, max-age={cache_age}')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(raw_data)
            
        except Exception as e:
            self.send_error(500, f'Internal Error: {str(e)}')
    
    def log_message(self, format, *args):
        """精简日志"""
        print(f"[{self.log_date_time_string()}] {args[0]}")

print(f"优化版服务器启动: http://localhost:{PORT}")
print(f"特性: gzip压缩 | 浏览器缓存 | WebP图片")
print(f"按 Ctrl+C 停止")

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True
    allow_reuse_port = True

with ReusableTCPServer(("", PORT), OptimizedHandler) as httpd:
    httpd.serve_forever()
