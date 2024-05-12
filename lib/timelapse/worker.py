#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web サイトのスクリーンショットを定期的に記録します．

Usage:
  worker.py [-c CONFIG]

Options:
  -c CONFIG     : CONFIG を設定ファイルとして読み込んで実行します．[default: config.yaml]
"""

import logging
import random
import datetime
import time
import traceback
import PIL.Image
import io

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import timelapse.handle
import local_lib.selenium_util
import local_lib.pil_util


def wait_for_loading(handle, xpath="//body", sec=1):
    driver, wait = timelapse.handle.get_selenium_driver(handle)

    wait.until(EC.visibility_of_all_elements_located((By.XPATH, xpath)))
    time.sleep(sec)


def visit_url(handle, url, xpath="//body"):
    driver, wait = timelapse.handle.get_selenium_driver(handle)
    driver.get(url)

    wait_for_loading(handle, xpath)


def get_time_str():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), "JST")).strftime(
        "%Y年%m月%d日 %H時%M分"
    )


def get_screenshot_path(handle, name):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), "JST"))

    screenshot_path = (
        timelapse.handle.get_screenshot_dir_path(handle) / name / now.strftime("%Y%m%d_%H%M_%S.png")
    )

    screenshot_path.parent.mkdir(parents=True, exist_ok=True)

    return screenshot_path


def sleep(start_time, interval_sec):
    sleep_sec = interval_sec - (datetime.datetime.now() - start_time).total_seconds()

    logging.info("Sleep {sleep_sec:,.1f} sec...".format(sleep_sec=sleep_sec))

    time.sleep(sleep_sec)


def take_screenshot(handle, name, url):
    driver, wait = timelapse.handle.get_selenium_driver(handle)

    visit_url(handle, url)

    logging.info("Take screenshot of {name} - {url}".format(name=name, url=url))

    img = PIL.Image.open(io.BytesIO(driver.get_screenshot_as_png()))
    font = timelapse.handle.get_font(handle)

    local_lib.pil_util.draw_text(
        img,
        get_time_str(),
        (img.size[0] - 10, img.size[1] - local_lib.pil_util.text_size(img, font, "あ")[1] - 10),
        font,
        align="right",
        color="#000",
        stroke_width=4,
        stroke_fill=(255, 255, 255, 255),
    )

    img.save(get_screenshot_path(handle, name))


def run(handle):
    target_list = timelapse.handle.get_target_list(handle)

    while True:
        start_time = datetime.datetime.now()

        for target in target_list:
            take_screenshot(handle, target["name"], target["url"])
            time.sleep(10)

        sleep(start_time, timelapse.handle.get_interval_sec(handle))


if __name__ == "__main__":
    from docopt import docopt

    import local_lib.logger
    import local_lib.config

    args = docopt(__doc__)

    local_lib.logger.init("test", level=logging.INFO)

    config = local_lib.config.load(args["-c"])
    handle = timelapse.handle.create(config)

    driver, wait = timelapse.handle.get_selenium_driver(handle)

    try:
        run(handle)
    except:
        driver, wait = timelapse.handle.get_selenium_driver(handle)
        logging.error(traceback.format_exc())

        local_lib.selenium_util.dump_page(
            driver, int(random.random() * 100), timelapse.handle.get_debug_dir_path(handle)
        )
