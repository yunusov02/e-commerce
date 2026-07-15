import logging
import structlog

from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging() -> None:

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=[
            RotatingFileHandler(log_dir / "app.log", maxBytes=1_000_000, backupCount=5, encoding='utf-8'),
            logging.StreamHandler()
        ])

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),

        cache_logger_on_first_use=True
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(indent=4),
    )
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)

