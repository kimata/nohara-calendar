#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Line を使って通知を送ります．

Usage:
  notify_line.py [-c CONFIG]

Options:
  -c CONFIG     : CONFIG を設定ファイルとして読み込んで実行します．[default: config.yaml]
"""

import logging
import linebot.v3.messaging


def get_msg_config(line_config):
    return linebot.v3.messaging.Configuration(
        host="https://api.line.me", access_token=line_config["channel"]["access_token"]
    )


def send_impl(line_config, message):
    msg_config = get_msg_config(line_config)

    with linebot.v3.messaging.ApiClient(msg_config) as client:
        api = linebot.v3.messaging.MessagingApi(client)
        try:
            api.broadcast(linebot.v3.messaging.BroadcastRequest(messages=[message]))
        except Exception as e:
            logging.error("Failed to send message: {message}".format(message=e))


def send(line_config, message):
    send_impl(line_config, linebot.v3.messaging.TemplateMessage.from_dict(message))


def error(line_config, text):
    message = linebot.v3.messaging.FlexMessage.from_dict(
        {
            "type": "flex",
            "altText": "ERROR: {text:.300}".format(text=text),
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "ERROR",
                            "weight": "bold",
                            "color": "#FF3300",
                            "size": "sm",
                        },
                        {"type": "separator", "margin": "sm"},
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "lg",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": text,
                                    "size": "xs",
                                    "color": "#000000",
                                    "wrap": True,
                                    "flex": 0,
                                }
                            ],
                        },
                    ],
                },
                "styles": {"footer": {"separator": True}},
            },
        },
    )

    send_impl(line_config, message)


def info(line_config, text):
    message = linebot.v3.messaging.FlexMessage.from_dict(
        {
            "type": "flex",
            "altText": "INFO: {text}".format(text=text),
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "INFO",
                            "weight": "bold",
                            "color": "#1DB446",
                            "size": "sm",
                        },
                        {"type": "separator", "margin": "sm"},
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "margin": "lg",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": text,
                                    "size": "xs",
                                    "color": "#000000",
                                    "wrap": True,
                                    "flex": 0,
                                }
                            ],
                        },
                    ],
                },
                "styles": {"footer": {"separator": True}},
            },
        },
    )

    send_impl(line_config, message)


if __name__ == "__main__":
    from docopt import docopt

    import local_lib.logger
    import local_lib.config

    args = docopt(__doc__)

    local_lib.logger.init("test", level=logging.INFO)

    config = local_lib.config.load(args["-c"])

    item_info = {
        "name": "Dream Machine Pro",
        "url": "https://jp.store.ui.com/products/udm-pro-u",
        "image": "https://jp.store.ui.com/cdn/shop/products/UDM-Pro-005_grande.png",
    }

    message = {
        "type": "template",
        "altText": "【テスト】{name}の在庫が復活しました！".format(name=item_info["name"]),
        "template": {
            "type": "buttons",
            "thumbnailImageUrl": item_info["image"],
            "imageAspectRatio": "rectangle",
            "imageSize": "cover",
            "imageBackgroundColor": "#FFFFFF",
            "title": item_info["name"],
            "text": "【テスト】在庫が復活しました．",
            "defaultAction": {"type": "uri", "label": "販売ページに行く", "uri": item_info["url"]},
            "actions": [
                {"type": "uri", "label": "販売ページに行く", "uri": item_info["url"]},
            ],
        },
    }

    send(config["notify"]["line"], message)
    error(config["notify"]["line"], "Test")
