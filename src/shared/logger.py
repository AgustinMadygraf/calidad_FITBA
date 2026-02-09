import logging
import logging.config
from typing import Dict, Union


class LevelPrefixFormatter(logging.Formatter):
    """Uvicorn/FastAPI-like level prefix (e.g. "INFO:")."""

    _width = 10

    def format(self, record: logging.LogRecord) -> str:
        prefix = f"{record.levelname}:".ljust(self._width)
        record.levelprefix = prefix
        return super().format(record)


_configured = False


def _build_logging_config(level: Union[int, str]) -> Dict[str, object]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": LevelPrefixFormatter,
                "fmt": "%(levelprefix)s %(message)s",
            }
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stderr",
            }
        },
        "loggers": {
            "": {"handlers": ["default"], "level": level},
        },
    }


def configure_logging(level: Union[int, str] = logging.INFO) -> None:
    global _configured
    if _configured:
        logging.getLogger().setLevel(level)
        return
    logging.config.dictConfig(_build_logging_config(level))
    _configured = True


def get_logger(name: str = "app", level: Union[int, str] = logging.INFO) -> logging.Logger:
    configure_logging(level)
    return logging.getLogger(name)
