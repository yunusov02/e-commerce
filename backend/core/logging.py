import logging
import structlog
from structlog import BoundLogger
from pathlib import Path

_configured = False


def configure_structlog():

    global _configured

    if _configured:
        return
    

    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "app.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ]

    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    _configured = True



def get_logger(name: str | None = None) -> BoundLogger:

    return structlog.get_logger(name)
