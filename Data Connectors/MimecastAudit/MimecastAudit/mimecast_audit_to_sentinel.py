"""Get Mimecast Audit Data and Ingest into Sentinel."""

from ..SharedCode.state_manager import StateManager
import json
import datetime
import inspect
import time
from SharedCode import consts
from SharedCode.logger import applogger
from SharedCode.mimecast_exception import MimecastException, MimecastTimeoutException
from SharedCode.utils import Utils
from SharedCode import sentinel


class MimeCastAuditToSentinel(Utils):
    """This class contains methods to create object and ingest mimecast audit data to sentinel."""

    def __init__(self, start) -> None:
        """Initialize instance variable for class."""
        super().__init__(consts.AUDIT_FUNCTION_NAME)
        self.check_environment_var_exist(
            [
                {"Base_Url": consts.BASE_URL},
                {"WorkspaceID": consts.WORKSPACE_ID},
                {"WorkspaceKey": consts.WORKSPACE_KEY},
                {"Mimecast_Client_Id": consts.MIMECAST_CLIENT_ID},
                {"Mimecast_Client_Secret": consts.MIMECAST_CLIENT_SECRET},
                {"File_Path": consts.FILE_PATH},
                {"File_Share_Name": consts.FILE_SHARE_NAME},
            ]
        )
        self.state_manager = StateManager(
            connection_string=consts.CONN_STRING,
            file_path=consts.FILE_PATH,
            share_name=consts.FILE_SHARE_NAME,
        )
        self.function_start_time = start
        self.authenticate_mimecast_api()
        self.start_date = None

    def get_utc_time_in_past(self, days):
        """Generate time by subtracting days from current UTC time.

        Args:
            start_datetime (string): start of data fetching
        Returns:
            string : string of date days ago
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name
            now = datetime.datetime.utcnow()
            offset_time = now - datetime.timedelta(days=days)
            offset_time = offset_time.replace(tzinfo=datetime.timezone.utc)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Successfully generated past UTC time ",
                )
            )
            return offset_time.strftime("%Y-%m-%dT%H:%M:%S%z")
        except MimecastException:
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    def update_date_in_checkpoint(self):
        """Initialize new interval of date in checkpoint.

        Returns:
            json : Updated checkpoint.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Setting new start date and end date in checkpoint file",
                )
            )

            checkpoint = self.get_checkpoint_data(self.state_manager, load_flag=True)

            utc_timestamp = (
                datetime.datetime.utcnow()
                .replace(tzinfo=datetime.timezone.utc)
                .isoformat()
            )
            start_date = checkpoint.get("end_time")
            mimecast_start_date = datetime.datetime.strptime(
                start_date, consts.TIME_FORMAT
            )

            checkpoint["start_time"] = mimecast_start_date.strftime(consts.TIME_FORMAT)
            end_date = datetime.datetime.fromisoformat(utc_timestamp)
            mimecast_end_date = end_date.strftime(consts.TIME_FORMAT)
            checkpoint["end_time"] = mimecast_end_date
            checkpoint["next"] = ""

            self.post_checkpoint_data(
                self.state_manager, data=checkpoint, dump_flag=True
            )

            self.set_payload(checkpoint["start_time"], checkpoint["end_time"])
            self.start_date = checkpoint["start_time"]
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Checkpoint updated with new start date and end date",
                )
            )

            return checkpoint
        except MimecastException:
            raise MimecastException()
        except KeyError as key_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.KEY_ERROR_MSG.format(key_error),
                )
            )
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    def checkpoint_field(self):
        """Set the start date and end date in checkpoint file.

        Returns:
            json : Parsed checkpoint
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            checkpoint = self.get_checkpoint_data(self.state_manager, load_flag=True)

            if not checkpoint:
                checkpoint = {}

            utc_timestamp = (
                datetime.datetime.utcnow()
                .replace(tzinfo=datetime.timezone.utc)
                .isoformat()
            )

            checkpoint_updated = False
            if checkpoint.get("start_time") is None:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Checkpoint is empty ",
                    )
                )

                start_date = None
                if not consts.START_DATE:
                    start_date = self.get_utc_time_in_past(days=consts.DAYS_BACK)
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Date set to 15 days in the past",
                        )
                    )
                else:
                    start_date = (
                        datetime.datetime.strptime(consts.START_DATE, "%Y-%m-%d")
                        .replace(
                            hour=0, minute=0, second=0, tzinfo=datetime.timezone.utc
                        )
                        .strftime(consts.TIME_FORMAT)
                    )
                    now = datetime.datetime.utcnow().strftime(consts.TIME_FORMAT)
                    last_valid_date = self.get_utc_time_in_past(
                        days=consts.VALID_PREVIOUS_DAY
                    )
                    if start_date > now:
                        applogger.error(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.azure_function_name,
                                "Error Occurred while validating params. StartTime cannot be in the future.",
                            )
                        )
                        raise MimecastException()
                    elif start_date < last_valid_date:
                        applogger.info(
                            self.log_format.format(
                                consts.LOGS_STARTS_WITH,
                                __method_name,
                                self.azure_function_name,
                                "Date provided is older than 60 days. "
                                "Ingestion will start from this date: {}".format(
                                    last_valid_date
                                ),
                            )
                        )

                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Date taken from user input",
                        )
                    )

                mimecast_start_date = datetime.datetime.strptime(
                    start_date, consts.TIME_FORMAT
                ) + datetime.timedelta(seconds=1)
                checkpoint["start_time"] = mimecast_start_date.strftime(
                    consts.TIME_FORMAT
                )

                end_date = datetime.datetime.fromisoformat(
                    utc_timestamp
                ) - datetime.timedelta(seconds=15)
                mimecast_end_date = end_date.strftime(consts.TIME_FORMAT)
                checkpoint["end_time"] = mimecast_end_date

                checkpoint_updated = True
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Start and end dates initialized in the checkpoint file.",
                    )
                )

            self.start_date = checkpoint["start_time"]
            if checkpoint_updated:
                self.post_checkpoint_data(self.state_manager, data=checkpoint)

                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Checkpoint data fetched and written",
                    )
                )

            return checkpoint
        except MimecastException:
            raise MimecastException()
        except KeyError as key_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.KEY_ERROR_MSG.format(key_error),
                )
            )
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    def valid_run(self):
        """Validate run of function.

        Raises:
            MimecastTimeoutException: To limit total function run time
            MimecastException: Unknown Exception

        Returns:
            Bool: Will Decide to stop or run
        """
        try:
            __method_name = inspect.currentframe().f_code.co_name

            valid_run = True
            if (
                int(time.time())
                >= self.function_start_time + consts.FUNCTION_APP_TIMEOUT_SECONDS
            ):
                valid_run = False
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "function app has executed 9:30 mins hence breaking.",
                    )
                )
                raise MimecastTimeoutException()

            difference = datetime.datetime.now(
                datetime.timezone.utc
            ) - datetime.datetime.strptime(self.start_date, consts.TIME_FORMAT)

            if difference < datetime.timedelta(minutes=15):
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Time difference is less than 15 minutes, stopping the execution",
                    )
                )
                valid_run = False

            return valid_run
        except MimecastTimeoutException:
            raise MimecastTimeoutException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    def get_mimecast_audit_data_in_sentinel(self):
        """Fetch the audit data and push into sentinel.

        Raises:
            MimecastException: MimecastException
            MimecastException: KeyError
            MimecastException: Unknown Exception
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Fetching and Pushing Audit Data from Mimecast",
                )
            )

            checkpoint = self.checkpoint_field()
            start_date = checkpoint.get("start_time")
            end_date = checkpoint.get("end_time")

            payload = self.set_payload(start_date, end_date)

            if "next" in checkpoint and checkpoint["next"] != "":
                token = checkpoint.get("next")
                payload = self.set_payload(start_date, end_date, token=token)
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Continuing data ingestion from remaining ,from : {}".format(
                            start_date
                        ),
                    )
                )

            has_more_data = True
            while has_more_data:

                has_more_data = self.valid_run()
                if not has_more_data:
                    break

                response = self.make_rest_call(
                    method="POST",
                    url=consts.BASE_URL + consts.ENDPOINTS["AUDIT_ENDPOINT"],
                    json=payload,
                )

                data = response.get("data")
                if len(data) > 0:
                    data = json.dumps(data)
                    sentinel.post_data(data, consts.TABLE_NAME["Audit"])
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Data ingested to Sentinel",
                        )
                    )

                if "next" in response["meta"]["pagination"]:
                    token = response["meta"]["pagination"]["next"]
                    checkpoint["next"] = token
                    self.post_checkpoint_data(
                        self.state_manager, checkpoint, dump_flag=True
                    )
                    payload = self.set_payload(start_date, end_date, token=token)

                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Next token updated in checkpoint file",
                        )
                    )
                else:
                    self.update_date_in_checkpoint()
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Successfully fetched all the data from Mimecast Audit, from : {} , to : {}".format(
                                start_date, end_date
                            ),
                        )
                    )

                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Fetching data using next pageToken",
                    )
                )
        except MimecastException:
            raise MimecastException()
        except MimecastTimeoutException:
            return
        except KeyError as key_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.KEY_ERROR_MSG.format(key_error),
                )
            )
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()

    def set_payload(self, start_datetime, end_datetime, token=None):
        """Set payload for api call.

        Args:
            start_datetime (string): start of data fetching
            end_datetime (string): end date of data fetching
            token (string, optional): next token . Defaults to None.

        Raises:
            MimecastException: MimecastException
            MimecastException: KeyError
            MimecastException: Unknown error

        Returns:
            json: will be passed in body of api call
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:

            payload = {
                "meta": {"pagination": {"pageSize": consts.MAX_PAGE_SIZE}},
                "data": [
                    {"startDateTime": start_datetime, "endDateTime": end_datetime}
                ],
            }
            if token:
                payload["meta"]["pagination"]["pageToken"] = token

            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Payload set with start date : {} and end date : {}".format(
                        start_datetime, end_datetime
                    ),
                )
            )

            return payload
        except MimecastException:
            raise MimecastException()
        except KeyError as key_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.KEY_ERROR_MSG.format(key_error),
                )
            )
            raise MimecastException()
        except Exception as err:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(err),
                )
            )
            raise MimecastException()
