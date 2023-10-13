import sys
from loguru import logger


def configure_logger() -> None:
    logger.remove()

    logger.add(
        "logs/{time:MM_D}/{time:HH_mm}.log",
        format="{time:HH:mm:ss} | {function}:{line} | {level} - {message}",
    )
    logger.add(
        sys.stdout,
        format="<level>{time:HH:mm:ss}</level> | <lk>{function}</lk>:<lk>{line}</lk> | <level>{level}</level> - 🐷 <magenta>{message}</magenta>",  # noqa: E501
        colorize=True,
    )
