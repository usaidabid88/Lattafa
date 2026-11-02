"""
gunicorn_config.py - Production WSGI Configuration for Online Shopping System (Phase 13A)
WHY: Directs Gunicorn to manage worker processes, bind network ports, handle timeouts,
     and format structured access logs in production environments (Render, Linux VPS, Docker).
"""

import os
import multiprocessing

# Network Binding
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# Worker Processes
workers = int(os.getenv('WEB_CONCURRENCY', 2))
threads = int(os.getenv('PYTHON_MAX_THREADS', 2))
worker_class = 'gthread'
worker_connections = 1000
timeout = 60
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" (%(D)s µs)'

# Process Management
proc_name = 'muet_online_shop_wsgi'
preload_app = False
max_requests = 1000
max_requests_jitter = 50
