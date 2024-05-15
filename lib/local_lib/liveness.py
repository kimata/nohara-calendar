#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import pathlib
import time


def get_file(config, worker):
    return pathlib.Path(config["file"][worker])


def update(config, worker):
    liveness_file = get_file(config, worker)
    pathlib.Path(liveness_file).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(liveness_file).touch()


def check(config, worker):
    liveness_file = get_file(config, worker)
    interval = config["interval"]

    if not liveness_file.exists():
        logging.warning("{worker} is not executed.".format(worker=worker))
        return False

    elapsed = time.time() - liveness_file.stat().st_mtime
    # NOTE: 少なくとも1分は様子を見る
    if elapsed > max(interval * 2, 60):
        logging.warning(
            "Execution interval of {worker} is too long. ({elapsed:,} sec)".format(
                worker=worker, elapsed=elapsed
            )
        )
        return False

    return True
