# Gunicorn configuration for FCC ULS Web App
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/tmp/fcc-webapp-access.log"
errorlog = "/tmp/fcc-webapp-error.log"
loglevel = "info"

# Process naming
proc_name = "fcc-uls-webapp"

# Daemon mode
daemon = False
pidfile = "/tmp/fcc-webapp.pid"

# User/group to run as (optional, for security)
# user = "www-data"
# group = "www-data"
