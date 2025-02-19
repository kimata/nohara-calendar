#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import pathlib
import smtplib
import time
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

INTERVAL_MIN = 60 * 8

STAT_DIR_PATH = pathlib.Path("/dev/shm")
STAT_PATH_NOTIFY = STAT_DIR_PATH / "notify_mail"


def send_impl(mail_config, message, png_data=None):
    smtp = smtplib.SMTP(mail_config["smtp"]["hostname"], mail_config["smtp"]["port"])
    smtp.starttls()
    smtp.login(mail_config["smtp"]["user"], mail_config["smtp"]["pass"])

    msg = MIMEMultipart()
    msg["Subject"] = mail_config["content"]["subject"]
    msg["To"] = mail_config["content"]["to"]
    msg["From"] = mail_config["content"]["from"]

    if png_data is not None:
        cid = "image"
        img = MIMEImage(png_data, name="image.png")
        img.add_header("Content-ID", "<" + cid + ">")
        msg.attach(img)

        message += '<br/><img src="cid:{cid}"/>'.format(cid=cid)

    msg.attach(MIMEText(message, "html"))

    smtp.send_message(msg)

    logging.info("sendmail")

    smtp.quit()


def send(mail_config, message, png_data=None, is_log_message=True, is_force=False):
    if is_log_message:
        logging.info("notify: {message}".format(message=message))

    if (
        (not is_force)
        and STAT_PATH_NOTIFY.exists()
        and ((time.time() - STAT_PATH_NOTIFY.stat().st_mtime) / 60) < INTERVAL_MIN
    ):
        return

    send_impl(mail_config, message, png_data)

    STAT_PATH_NOTIFY.touch()


if __name__ == "__main__":
    from config import load_config

    config = load_config()

    send(config, "Testです")
