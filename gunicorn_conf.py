import json
import logging
import multiprocessing
import os

# See https://docs.gunicorn.org/en/stable/settings.html for details
# note parameters explicitly via gunicorn cmd line overrides what are set here
#  e.g. even though default here is info, "gunicorn --log-level=debug -c [this file]
#       would mean the debug level is debug, not info

workers_per_core_str = os.getenv("WORKERS_PER_CORE", "2")
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
bind_env = os.getenv("BIND", None)
if bind_env:
    use_bind = bind_env
else:
    use_bind = f"{host}:{port}"

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 2)

# Gunicorn config variables
workers = web_concurrency
worker_class = 'uvicorn.workers.UvicornWorker'
bind = use_bind
keepalive = os.getenv("GUNICORN_KEEPALIVE", 120)
errorlog = "-"
threads = os.getenv("GUNICORN_THREADS", 120)

valid_loglevel = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
valid_logformat = ['json', 'generic']
# loglevel controls the granularity of the gunicorn error log
use_loglevel = os.getenv("DEFAULT_LOG_LEVEL", "INFO").upper()
if use_loglevel not in valid_loglevel:
    use_loglevel = 'INFO'
use_logformat = os.getenv("DEFAULT_LOG_FORMAT", "generic").lower()
if use_logformat not in valid_logformat:
    use_logformat = 'generic'

logconfig_dict = {
    'version': 1,
    'formatters': {
        'generic': {
            'format': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'class': 'logging.Formatter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': use_logformat,
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        },
        'gunicorn.error': {
            'level': use_loglevel,
            'handlers': ['console'],
            'propagate': False,
            'qualname': 'gunicorn.error'
        }
    }
}

# For debugging and testing
log_data = {
    "loglevel": use_loglevel,
    "logformat": use_logformat,
    "workers": workers,
    "bind": bind,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
    "host": host,
    "port": port,
}
logging.warning(json.dumps(log_data))
