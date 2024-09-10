"""Get SilentPush IOFA Data and Ingest into Sentinel."""

import json
import inspect
import time
from SharedCode import consts
from SharedCode.logger import applogger
from SharedCode.silentpush_exception import (
    SilentPushException,
    SilentPushTimeoutException,
)
from SharedCode.utils import Utils
from SharedCode.sentinel import post_data


class SilentPushIOFAToSentinel(Utils):
    """This class contains methods to create object and ingest SilentPush IOFA data to sentinel."""

    def __init__(self, start_time) -> None:
        """Initialize instance variable for class."""
        super().__init__(consts.IOFA_FUNCTION_NAME)
        self.check_environment_var_exist(
            [
                {"Base_Url": consts.BASE_URL},
                {"WorkspaceID": consts.WORKSPACE_ID},
                {"WorkspaceKey": consts.WORKSPACE_KEY},
                {"SilentPush_API_Key": consts.SILENTPUSH_API_Key},
            ]
        )
        self.start = start_time
        # self.authenticate_mimecast_api()

    def get_silentpush_iofa_data_in_sentinel(self):
        """Get the IOFA Feed Data from SilentPush."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            while True:
                if int(time.time()) >= self.start + consts.FUNCTION_APP_TIMEOUT_SECONDS:
                    raise SilentPushTimeoutException()
                # Entry point of starting to get and ingest data to sentinel
                self.get_and_ingest_data_to_sentinel(consts.SOURCE_UUID)
        except SilentPushTimeoutException:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "9:30 mins executed hence breaking.",
                )
            )
            return
        except SilentPushException:
            raise SilentPushException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise SilentPushException()

    def get_and_ingest_data_to_sentinel(self, source_uuid=None):
        """Iterate through pages and get Threat Ranking data and ingest data to sentinel.

        Args:
            source_uuid (str): The source_uuid for threat ranking retrieval.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            threat_ranking_count = self.make_rest_call(
                "GET",
                url="{}{}".format(
                    consts.BASE_URL, consts.ENDPOINTS["THREAT_RANKING_COUNT"]
                ),
                params={
                    "source_uuids": source_uuid,
                    "limit": consts.MAX_PAGE_SIZE,
                    "order": "-total_ioc,-total_source_score",
                    "state": "Feed",
                },
            )
            threat_ranking_count = threat_ranking_count.get("count", 0)
            page = 1
            list_indicators = []
            total_ingested_data_count = 0
            while threat_ranking_count > 0:
                if int(time.time()) >= self.start + consts.FUNCTION_APP_TIMEOUT_SECONDS:
                    raise SilentPushTimeoutException()
                threat_ranking = self.make_rest_call(
                    "GET",
                    url="{}{}".format(
                        consts.BASE_URL, consts.ENDPOINTS["THREAT_RANKING"]
                    ),
                    params={
                        "source_uuids": source_uuid,
                        "limit": consts.MAX_PAGE_SIZE,
                        "order": "-total_ioc,-total_source_score",
                        "state": "Feed",
                        "page": page,
                    },
                )
                for threat in threat_ranking:
                    list_indicators.append(threat["name"])
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Data count to ingest = {}".format(len(threat_ranking)),
                    )
                )
                total_ingested_data_count += len(threat_ranking)
                if len(threat_ranking) > 0:
                    post_data(
                        json.dumps(threat_ranking), consts.TABLE_NAME["THREAT_RANKING"]
                    )
                    # with open("data.json", "a+") as file:
                    #     json.dump(file, threat_ranking, indent=4)
                threat_ranking_count -= consts.MAX_PAGE_SIZE
                page += 1
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Total ingested count = {}".format(total_ingested_data_count),
                )
            )
            return list_indicators
        except SilentPushTimeoutException:
            raise SilentPushTimeoutException()
        except SilentPushException:
            raise SilentPushException()
        except ValueError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.VALUE_ERROR_MSG.format(err),
                )
            )
            raise SilentPushException()
        except TypeError as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.TYPE_ERROR_MSG.format(err),
                )
            )
            raise SilentPushException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise SilentPushException()
