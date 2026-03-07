import logging
import time
from logging.handlers import RotatingFileHandler
import os
from game.menu.menu_terminal import menu


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s UTC | %(levelname)s | %(name)s | %(message)s",
)

logging.Formatter.converter = time.gmtime  # keep timestamps in UTC

# if the logs directory does not exist, creates it
os.makedirs("logs", exist_ok=True)

# define the path for the log file
LOG_PATH = "logs/game.log"

# create rotating file handler (prevents infinite file growth)
file_handler = RotatingFileHandler(
    LOG_PATH,
    maxBytes=20_000_000,  # max size 20MB per file
    backupCount=5,  # keep up to 5 old log files
    encoding="utf-8",  # ensure logs are readable
)

# apply formatting to the file handler
file_handler.setFormatter(
    logging.Formatter("%(asctime)s UTC | %(levelname)s | %(name)s | %(message)s")
)

# get the root logger (the central logger used by everything)
log = logging.getLogger()

# remove the default console handler created by basicConfig
log.handlers.clear()  # ensures no terminal logs

# add our file handler
log.addHandler(file_handler)  # now all logs go to file only


menu()
