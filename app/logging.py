import logging
import sys
from typing import Literal


def configure_logging(debug: bool = False) -> None:
    level: Literal[10, 20] = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
    )
