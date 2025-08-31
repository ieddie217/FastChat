# app/core/logging.py
import os
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from .config import settings

LOG_DIR = "logs"
APP_LOG = os.path.join(LOG_DIR, "app.log")
AUDIT_LOG = os.path.join(LOG_DIR, "audit.log")

def setup_logging():
    # create logs/ if missing
    os.makedirs(LOG_DIR, exist_ok=True)

    root = logging.getLogger()
    if root.handlers:
        return  # already configured

    root.setLevel(logging.INFO)

    # JSON formatter including our custom fields
    fmt = (
        "%(asctime)s %(levelname)s %(name)s %(message)s "
        "%(req_id)s %(client_ip)s %(method)s %(path)s "
        "%(status)s %(elapsed_ms)s %(user_agent)s "
        "%(user)s %(model)s %(tokens_prompt)s %(tokens_completion)s %(tokens_total)s "
        "%(question_preview)s"
    )
    json_formatter = jsonlogger.JsonFormatter(fmt)

    # Console handler (stdout)
    ch = logging.StreamHandler()
    ch.setFormatter(json_formatter)
    root.addHandler(ch)

    # Rotating file handler (about ~10MB per file, keep 5 backups; tune as needed)
    fh = RotatingFileHandler(APP_LOG, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    fh.setFormatter(json_formatter)
    root.addHandler(fh)

    audit_logger = logging.getLogger("audit")
    audit_logger.propagate = False  # don't duplicate into root handlers
    audit_logger.setLevel(logging.INFO)

    if settings.DEBUG_AUDIT:
        ah = RotatingFileHandler(AUDIT_LOG, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
        ah.setFormatter(json_formatter)
        audit_logger.addHandler(ah)
    # else: no handlers -> effectively disabled
    # Optional: keep uvicorn access logs separate/minimal if you like
    # logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
