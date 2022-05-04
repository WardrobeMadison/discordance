import os
import sys
from datetime import datetime
from pathlib import Path
import logging

HOME = Path.home() / "Documents/DissconaceLogs"

def init_log(logdir:Path = HOME):
    # SET UP PATH INFORMATION
    logdir.mkdir(parents=True, exist_ok=True)
    pathlog = Path(f"log_{datetime.now().strftime(r'%Y%m%d_%H%M%S')}.txt")

    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s : %(levelname)s -%(name)s : %(message)s',datefmt='%Y%m%d %I:%M:%S %p')

    # FILE HANDLER
    fh = logging.FileHandler(logdir/pathlog, mode="w+")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    # STREAM HANDLER
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)

    logger.addHandler(fh)
    logger.addHandler(sh)

    return logger