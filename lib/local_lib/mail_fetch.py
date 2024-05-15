#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAP サーバから条件に合致するメールの文面を抜き出します．

Usage:
  mail_fetch.py [-c CONFIG]

Options:
  -c CONFIG    : CONFIG を設定ファイルとして読み込んで実行します．[default: config.yaml]
"""

import imaplib
import email
import datetime
import logging
import re


def login(imap_config):
    con = imaplib.IMAP4_SSL(imap_config["server"])

    con.login(imap_config["user"], imap_config["pass"])
    con.select("INBOX")

    return con


def fetch_impl(con, search_cond, subject_regex, extract_regex, days_before):
    query_list = []
    for key in search_cond.keys():
        query_list.append('HEADER "{key}" "{value}"'.format(key=key, value=search_cond[key]))

    query_list.append(
        "SINCE {date}".format(
            date=(datetime.date.today() - datetime.timedelta(days=days_before)).strftime("%d-%b-%Y")
        )
    )

    result, data = con.search(None, "({query})".format(query=" ".join(query_list)))

    if result != "OK":
        raise Exception("検索に失敗しました．")

    candidate = []

    for num in data[0].split():
        result, data = con.fetch(num, "(RFC822)")

        if result != "OK":
            raise Exception("メールの取得に失敗しました．")

        message = email.message_from_bytes(data[0][1])
        subject = email.header.decode_header(message.get("Subject"))[0][0].decode()

        if not re.match(subject_regex, subject):
            logging.info("Skip message: {subject}".format(subject=subject))
            continue

        if message.is_multipart() == False:
            raise Exception("対応していないメール形式です．")

        body = message.get_payload()[0].get_payload(decode=True).decode("utf-8")

        for line in body.split("\n"):
            m = re.match(extract_regex, line)

            if m is None:
                continue

            candidate.append(m.group(1))

    if len(candidate) == 0:
        return None
    else:
        return candidate[-1]


def extract(imap_config, search_cond, subject_regex, extract_regex, days_before=1):
    con = login(imap_config)

    return fetch_impl(con, search_cond, subject_regex, extract_regex, days_before)


if __name__ == "__main__":
    from docopt import docopt

    import local_lib.logger
    import local_lib.config

    args = docopt(__doc__)

    local_lib.logger.init("test", level=logging.INFO)

    config = local_lib.config.load(args["-c"])

    logging.info(
        extract(
            config["mail_auth"]["imap"],
            {"From": "shipment-tracking@amazon.co.jp"},
            r"Amazon.co.jp",
            r"注文番号 #([\d-]+)",
            10,
        )
    )
