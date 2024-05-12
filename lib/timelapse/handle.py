#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib

from selenium.webdriver.support.wait import WebDriverWait

import local_lib.selenium_util
import local_lib.pil_util


def create(config):
    handle = {
        "config": config,
    }

    prepare_directory(handle)

    return handle


def get_check_interval(handle):
    return handle["config"]["interval_sec"]


def prepare_directory(handle):
    get_selenium_data_dir_path(handle).mkdir(parents=True, exist_ok=True)
    get_screenshot_dir_path(handle).mkdir(parents=True, exist_ok=True)
    get_debug_dir_path(handle).mkdir(parents=True, exist_ok=True)


def get_selenium_data_dir_path(handle):
    return pathlib.Path(handle["config"]["base_dir"], handle["config"]["data"]["selenium"])


def get_screenshot_dir_path(handle):
    return pathlib.Path(handle["config"]["base_dir"], handle["config"]["data"]["screenshot"])


def get_debug_dir_path(handle):
    return pathlib.Path(handle["config"]["base_dir"], handle["config"]["data"]["debug"])


def get_selenium_driver(handle):
    if "selenium" in handle:
        return (handle["selenium"]["driver"], handle["selenium"]["wait"])
    else:
        driver = local_lib.selenium_util.create_driver("Merhist", get_selenium_data_dir_path(handle))
        wait = WebDriverWait(driver, 5)

        local_lib.selenium_util.clear_cache(driver)

        handle["selenium"] = {
            "driver": driver,
            "wait": wait,
        }

        return (driver, wait)


def get_font(handle):
    return local_lib.pil_util.get_font(
        pathlib.Path(handle["config"]["base_dir"], handle["config"]["font"]["path"])
        / handle["config"]["font"]["name"],
        handle["config"]["font"]["size"],
    )


def get_target_list(handle):
    return handle["config"]["target"]


def get_interval_sec(handle):
    return handle["config"]["interval_sec"]


def finish(handle):
    if "selenium" in handle:
        handle["selenium"]["driver"].quit()
        handle.pop("selenium")
