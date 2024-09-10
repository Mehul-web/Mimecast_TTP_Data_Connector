"""This is init file for SilentPush IOFA Feed"""

import datetime
import logging
import inspect
import time
from .SilentPush_IOFA_to_sentinel import SilentPushIOFAToSentinel
from SharedCode.logger import applogger
from SharedCode import consts
import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    """SilentPush IOFA Feed

    Args:
        mytimer (func.TimerRequest): _description_
    """

    __method_name = inspect.currentframe().f_code.co_name
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )
    start = time.time()
    applogger.info(
        "{} : {}, Function started at {}".format(
            consts.LOGS_STARTS_WITH,
            consts.IOFA_FUNCTION_NAME,
            datetime.datetime.fromtimestamp(start),
        )
    )

    silentpushiofa = SilentPushIOFAToSentinel(int(start))
    silentpushiofa.get_silentpush_iofa_data_in_sentinel()

    end = time.time()

    applogger.info(
        "{} : {}, Function ended at {}".format(
            consts.LOGS_STARTS_WITH,
            consts.IOFA_FUNCTION_NAME,
            datetime.datetime.fromtimestamp(end),
        )
    )
    applogger.info(
        "{} : {}, Total time taken = {}".format(
            consts.LOGS_STARTS_WITH, consts.IOFA_FUNCTION_NAME, end - start
        )
    )

    if mytimer.past_due:
        applogger.info(
            "{}(method={}) : {} : The timer is past due!".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                consts.IOFA_FUNCTION_NAME,
            )
        )

    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
