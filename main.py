import sys

from loguru import logger

from src import main


logger.remove()
logger.add(sys.stdout, format='[{time:HH:mm:ss}] <lvl>{message}</lvl>', level="INFO")


if __name__ == "__main__":
    main()
