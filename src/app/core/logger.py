from datetime import datetime, timezone
from logging.config import dictConfig
import logging
import json

# Define structure of logging configuration
class JsonFormatter(logging.Formatter):
  def format(self, record):
    log_record = {
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "level": record.levelname,
      "logger": record.name,
      "module": record.module,
      "line": record.lineno,
      "message": record.getMessage()
    }

    # Add exception info if available
    if record.exc_info:
      log_record["exception"] = self.formatException(record.exc_info)

    return json.dumps(log_record)
    
# Define the logging configuration
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": JsonFormatter
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "app": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
    "root": {"handlers": ["console"], "level": "DEBUG"},
}


# Apply the configuration
dictConfig(log_config)

logger = logging.getLogger("app")
