"""This file contains methods for creating microsoft custom log table."""

import base64
import requests
import hashlib
import hmac
import inspect
import datetime
import time
import aiohttp
from .logger import applogger
from .mimecast_exception import MimecastException
from . import consts
from .state_manager import StateManager
from urllib3.exceptions import NameResolutionError


def build_signature(
    date,
    content_length,
    method,
    content_type,
    resource,
):
    """To build signature which is required in header."""
    x_headers = "x-ms-date:" + date
    string_to_hash = (
        method
        + "\n"
        + str(content_length)
        + "\n"
        + content_type
        + "\n"
        + x_headers
        + "\n"
        + resource
    )
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(consts.WORKSPACE_KEY)
    encoded_hash = base64.b64encode(
        hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
    ).decode()
    authorization = "SharedKey {}:{}".format(consts.WORKSPACE_ID, encoded_hash)

    return authorization


def post_data(body, log_type):
    """Build and send a request to the POST API.

    Args:
        body (str): Data to post into Sentinel log analytics workspace
        log_type (str): Custom log table name in which data wil be added.

    Returns:
        status_code: Returns the response status code got while posting data to sentinel.
    """
    __method_name = inspect.currentframe().f_code.co_name
    method = "POST"
    content_type = "application/json"
    resource = "/api/logs"
    rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    content_length = len(body)
    try:
        signature = build_signature(
            rfc1123date,
            content_length,
            method,
            content_type,
            resource,
        )
    except Exception as err:
        applogger.error(
            "{}(method={}) : Error-{}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                err,
            )
        )
        raise MimecastException()
    uri = (
        "https://"
        + consts.WORKSPACE_ID
        + ".ods.opinsights.azure.com"
        + resource
        + "?api-version=2016-04-01"
    )

    headers = {
        "content-type": content_type,
        "Authorization": signature,
        "Log-Type": log_type,
        "x-ms-date": rfc1123date,
    }
    try:
        response = requests.post(uri, data=body, headers=headers)
        if response.status_code >= 200 and response.status_code <= 299:
            applogger.debug(
                "{}(method={}) : Status_code: {} Accepted: Data Posted Successfully to azure sentinel.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    response.status_code,
                )
            )
            return response.status_code
        else:
            raise MimecastException()
    except requests.RequestException as error:
        applogger.error(
            "{}(method={}) : Request error : Error-{}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                error,
            )
        )
        raise MimecastException()
    except Exception as error:
        applogger.error(
            "{}(method={}) : Error-{}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                error,
            )
        )
        raise MimecastException()


async def post_data_async(index, body, session: aiohttp.ClientSession, log_type):
    """Build and send a request to the POST API.

    Args:
        body (str): Data to post into Sentinel log analytics workspace
        log_type (str): Custom log table name in which data wil be added.

    Returns:
        status_code: Returns the response status code got while posting data to sentinel.
    """
    __method_name = inspect.currentframe().f_code.co_name
    method = "POST"
    content_type = "application/json"
    resource = "/api/logs"
    rfc1123date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    content_length = len(body)
    try:
        signature = build_signature(
            rfc1123date,
            content_length,
            method,
            content_type,
            resource,
        )
    except Exception as err:
        applogger.error(
            "{}(method={}) : Error-{} for task = {}".format(
                consts.LOGS_STARTS_WITH, __method_name, err, index
            )
        )
        raise MimecastException()
    uri = (
        "https://"
        + consts.WORKSPACE_ID
        + ".ods.opinsights.azure.com"
        + resource
        + "?api-version=2016-04-01"
    )

    headers = {
        "content-type": content_type,
        "Authorization": signature,
        "Log-Type": log_type,
        "x-ms-date": rfc1123date,
    }
    retry_count = 0
    while retry_count < consts.SENTINEL_RETRY_COUNT:
        try:

            is_internal_server_issue = False
            response = await session.post(
                uri, data=body, headers=headers, timeout=consts.MAX_TIMEOUT_SENTINEL
            )
            if response.status >= 200 and response.status <= 299:
                applogger.debug(
                    "{}(method={}) : status: {} Accepted: Data Posted Successfully to "
                    "azure sentinel for task = {}".format(
                        consts.LOGS_STARTS_WITH, __method_name, response.status, index
                    )
                )
                return response.status
            elif response.status == 400:
                applogger.error(
                    "{}(method={}) : {} : Response code: {} from posting data to log analytics. Error: {}".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        log_type,
                        response.status,
                        response.content,
                    )
                )
                curent_corrupt_data_obj = StateManager(
                    consts.CONN_STRING,
                    "{}-Ingest-To-Sentinel-Corrupt_{}".format(
                        log_type, str(int(time.time()))
                    ),
                    consts.FILE_SHARE_NAME,
                )
                curent_corrupt_data_obj.post(body)

                raise MimecastException()
            elif response.status == 403:
                applogger.error(
                    "{}(method={}) : {} : Error occurred for build signature: {} Issue with WorkspaceKey. "
                    "Kindly verify your WorkspaceKey".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        log_type,
                        response.content,
                    )
                )
                raise MimecastException()
            elif response.status == 429:
                applogger.error(
                    "{}(method={}) : {} : Error occurred: Response code : {} Too many request: {} . "
                    "sleeping for {} seconds and retrying..".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        log_type,
                        response.status,
                        response.content,
                        consts.INGESTION_ERROR_SLEEP_TIME,
                    )
                )
                time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                retry_count += 1
                continue
            elif response.status == 500:
                applogger.error(
                    "{}(method={}) : {} : Error occurred:  Response code : {} Internal Server Error: {} . "
                    "sleeping for {} seconds and retrying..".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        log_type,
                        response.status,
                        response.content,
                        consts.INGESTION_ERROR_SLEEP_TIME,
                    )
                )
                time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                retry_count += 1
                is_internal_server_issue = True
                continue
            elif response.status == 503:
                applogger.error(
                    "{}(method={}) : {} : Error occurred: Response code : {} Service Unavailable: {} . "
                    "sleeping for {} seconds and retrying..".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        log_type,
                        response.status,
                        response.content,
                        consts.INGESTION_ERROR_SLEEP_TIME,
                    )
                )
                time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                retry_count += 1
                is_internal_server_issue = True
                continue
            applogger.error(
                "{}(method={}) : {} : Response code: {} from posting data to log analytics. Error: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    response.status,
                    response.content,
                )
            )
            raise MimecastException()
        except requests.exceptions.ConnectionError as error:
            if isinstance(error.args[0].reason, NameResolutionError):
                applogger.error(
                    "{}(method={}) : {} : Workspace ID is wrong: {}, sleeping for {} seconds and retrying..".format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        log_type,
                        error,
                        consts.INGESTION_ERROR_SLEEP_TIME,
                    )
                )
                time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
                retry_count += 1
                continue
            applogger.error(
                "{}(method={}) : {} : Unknown Connection Error, sleeping for {} seconds and retrying.."
                "Error - {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    consts.INGESTION_ERROR_SLEEP_TIME,
                    error,
                )
            )
            time.sleep(consts.INGESTION_ERROR_SLEEP_TIME)
            retry_count += 1
        except requests.exceptions.Timeout as error:
            applogger.error(
                "{}(method={}) : {} : Timeout Error: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    error,
                )
            )
            raise MimecastException()
        except requests.RequestException as error:
            applogger.error(
                "{}(method={}) : {} : Request Error: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    error,
                )
            )
            raise MimecastException()
        except MimecastException as mimecast_err:
            applogger.error(
                "{}(method={}) : {} : Mimecast Error: {}".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    mimecast_err,
                )
            )
            raise MimecastException()
        except Exception as error:
            applogger.error(
                "{}(method={}) : {} : Unknown Error: {}.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    error,
                )
            )
            raise MimecastException()
    else:
        if is_internal_server_issue:
            applogger.error(
                "{}(method={}) : {} : Maximum Retry count of {} exceeded as internal server error,"
                " hence stopping execution.".format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    log_type,
                    consts.SENTINEL_RETRY_COUNT,
                )
            )
            raise MimecastException()
        applogger.error(
            "{}(method={}) : {} : Maximum Retry count of {} exceeded, hence stopping execution.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                log_type,
                consts.SENTINEL_RETRY_COUNT,
            )
        )
        raise MimecastException()