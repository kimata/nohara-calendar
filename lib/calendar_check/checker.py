#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
野原工芸のカレンダーを監視し，予約の空きが見つかった場合，通知を行います．

Usage:
  checker.py [-c CONFIG]

Options:
  -c CONFIG     : CONFIG を設定ファイルとして読み込んで実行します．[default: config.yaml]
"""

import logging
import random
import time
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import calendar_check.handle
import local_lib.selenium_util
import local_lib.notify_mail
import local_lib.liveness

CHECK_INTERVAL_SEC = 60


def wait_for_loading(handle, xpath="//body", sec=1):
    driver, wait = calendar_check.handle.get_selenium_driver(handle)

    wait.until(EC.visibility_of_all_elements_located((By.XPATH, xpath)))
    time.sleep(sec)


def visit_url(handle, url, xpath="//body"):
    driver, wait = calendar_check.handle.get_selenium_driver(handle)
    driver.get(url)

    wait_for_loading(handle, xpath)


def sleep(handle):
    sleep_sec = calendar_check.handle.get_check_interval(handle) + (10 * random.random())

    logging.info("Sleep {sleep_sec:,} sec...".format(sleep_sec=int(sleep_sec)))
    time.sleep(sleep_sec)


def check_calendar(handle):
    for _ in range(3):
        month_text = driver.find_element(By.XPATH, '//div[@id="currentDate1"]').text
        logging.info("Check {month} ...".format(month=month_text))

        reserve_list = driver.find_elements(
            By.XPATH,
            '//div[contains(@class, "month-row")]//td[contains(@class, "st-c")]'
            + '//span[contains(@class, "te-t") and contains(text(), ":")]'
            + '/following-sibling::span[contains(@class, "te-s")]',
        )
        for reserve in reserve_list:
            if reserve.text != "X":
                return True

        driver.find_element(By.XPATH, '//img[@title="次"]').click()
        time.sleep(3)

    return False


def check(handle):
    url = "https://www.nohara.jp/raitenyoyaku.html"

    visit_url(handle, url)

    iframe = driver.find_element(By.XPATH, '//div[contains(@class, "googlecal")]/iframe')

    driver.switch_to.frame(iframe)

    if check_calendar(handle):
        mail_config = calendar_check.handle.get_mail_config(handle)
        local_lib.notify_mail.send(
            mail_config,
            mail_config["content"]["message"],
            driver.find_element(By.XPATH, "//body").screenshot_as_png,
        )
        return True

    driver.switch_to.default_content()

    return False


def run(handle):

    while True:
        check(handle)

        local_lib.liveness.update(calendar_check.handle.get_liveness_config(handle), "watcher")

        sleep(handle)

    logging.info("Finished!")


if __name__ == "__main__":
    from docopt import docopt

    import local_lib.logger
    import local_lib.config

    args = docopt(__doc__)

    local_lib.logger.init("test", level=logging.INFO)

    config = local_lib.config.load(args["-c"])
    handle = calendar_check.handle.create(config)

    driver, wait = calendar_check.handle.get_selenium_driver(handle)

    try:
        run(handle)
    except:
        driver, wait = calendar_check.handle.get_selenium_driver(handle)
        logging.error(traceback.format_exc())

        local_lib.selenium_util.dump_page(
            driver,
            int(random.random() * 100),
            calendar_check.handle.get_debug_dir_path(handle),
        )
