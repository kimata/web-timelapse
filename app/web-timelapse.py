#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web サイトのスクリーンショットを定期的に記録します．

Usage:
  timelapse.py [-c CONFIG]

Options:
  -c CONFIG     : CONFIG を設定ファイルとして読み込んで実行します．[default: config.yaml]
"""

import logging
import time
import signal
import sys

import local_lib.selenium_util
import local_lib.notify_line
import timelapse.handle
import timelapse.worker


NAME = "web-timelapse"
VERSION = "0.1.0"


def execute_impl(handle):
    try:
        timelapse.worker.run(handle)
    except:
        logging.error(traceback.format_exc())


def execute(config):
    handle = timelapse.handle.create(config)

    logging.info("Start...")

    while True:
        execute_impl(handle)
        timelapse.handle.finish(handle)

        time.sleep(60)


def sig_handler(signum, frame):
    global config

    logging.error("Terminated...")

    sys.exit(1)


######################################################################
if __name__ == "__main__":
    from docopt import docopt
    import traceback

    import local_lib.logger
    import local_lib.config

    args = docopt(__doc__)

    local_lib.logger.init("timelapse", level=logging.INFO)

    config_file = args["-c"]
    config = local_lib.config.load(args["-c"])

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    execute(config)
