#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib

from selenium.webdriver.support.wait import WebDriverWait

import local_lib.selenium_util


def create(config):
    handle = {
        "config": config,
    }

    prepare_directory(handle)

    return handle


def get_mail_config(handle):
    return handle["config"]["notify"]["mail"]


def get_check_interval(handle):
    return handle["config"]["check"]["interval_sec"]


def get_liveness_config(handle):
    return handle["config"]["liveness"]


def prepare_directory(handle):
    get_selenium_data_dir_path(handle).mkdir(parents=True, exist_ok=True)
    get_work_dir_path(handle).mkdir(parents=True, exist_ok=True)
    get_debug_dir_path(handle).mkdir(parents=True, exist_ok=True)


def get_selenium_data_dir_path(handle):
    return pathlib.Path(handle["config"]["base_dir"], handle["config"]["data"]["selenium"])


def get_work_dir_path(handle):
    return pathlib.Path(handle["config"]["base_dir"], handle["config"]["data"]["work"])


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


def finish(handle):
    if "selenium" in handle:
        handle["selenium"]["driver"].quit()
        handle.pop("selenium")
