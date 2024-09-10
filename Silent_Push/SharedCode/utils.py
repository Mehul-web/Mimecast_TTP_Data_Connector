"""Utils File."""

import inspect
import requests
import time
from SharedCode.silentpush_exception import SilentPushException
from SharedCode.logger import applogger
from SharedCode import consts
from random import randrange


class Utils:
    """Utils Class."""

    def __init__(self, azure_function_name) -> None:
        """Init Function."""
        self.azure_function_name = azure_function_name
        self.log_format = consts.LOG_FORMAT
        self.headers = {"X-API-KEY": consts.SILENTPUSH_API_Key}

    def check_environment_var_exist(self, environment_var):
        """Check the existence of required environment variables.

        Logs the validation process and completion. Raises SilentPushException if any required field is missing.

        Args:
            environment_var(list) : variables to check for existence
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Validating Environment Variables",
                )
            )
            missing_required_field = False
            for var in environment_var:
                key, val = next(iter(var.items()))
                if not val:
                    missing_required_field = True
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Environment variable {} is not set".format(key),
                        )
                    )
            if missing_required_field:
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Validation failed",
                    )
                )
                raise SilentPushException()
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Validation Complete",
                )
            )
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

    def make_rest_call(self, method, url, params=None):
        """Make a rest call.

        Args:
            url (str): The URL to make the call to.
            method (str): The HTTP method to use for the call.
            params (dict, optional): The parameters to pass in the call (default is None).

        Returns:
            dict: The JSON response if the call is successful.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            for i in range(consts.MAX_RETRIES):
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Rest Call, Method :{}, url: {}".format(method, url),
                    )
                )
                response = requests.request(
                    method, url, headers=self.headers, params=params
                )

                if response.status_code >= 200 and response.status_code <= 299:
                    response_json = response.json()
                    applogger.info(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Success, Status code : {}".format(response.status_code),
                        )
                    )
                    return response_json
                elif response.status_code == 400:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Bad Request = {}, Status code : {}".format(
                                response.text, response.status_code
                            ),
                        )
                    )
                    # response_json = response.json()
                    raise SilentPushException()
                elif response.status_code == 401:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Unauthorized, Status code : {}".format(
                                response.status_code
                            ),
                        )
                    )
                    raise SilentPushException()
                elif response.status_code == 403:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Forbidden, Status code : {}".format(response.status_code),
                        )
                    )
                    raise SilentPushException()
                elif response.status_code == 404:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Not Found, URL : {}, Status code : {}".format(
                                url, response.status_code
                            ),
                        )
                    )
                    raise SilentPushException()
                elif response.status_code == 409:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Conflict, Status code : {}".format(response.status_code),
                        )
                    )
                    raise SilentPushException()
                elif response.status_code == 429:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Too Many Requests, Status code : {}, Retrying... {}".format(
                                response.status_code, i
                            ),
                        )
                    )
                    time.sleep(randrange(2, 10))
                    continue
                elif response.status_code == 500:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Internal Server Error, Status code : {}, Retrying... {".format(
                                response.status_code, i
                            ),
                        )
                    )
                    time.sleep(randrange(2, 10))
                    continue
                else:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Unexpected Error = {}, Status code : {}".format(
                                response.text, response.status_code
                            ),
                        )
                    )
                    raise SilentPushException()
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Max retries exceeded.",
                )
            )
            raise SilentPushException()
        except SilentPushException:
            raise SilentPushException()
        except requests.ConnectionError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.CONNECTION_ERROR_MSG.format(error),
                )
            )
            raise SilentPushException()
        except requests.HTTPError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.HTTP_ERROR_MSG.format(error),
                )
            )
            raise SilentPushException()
        except requests.RequestException as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.REQUEST_ERROR_MSG.format(error),
                )
            )
            raise SilentPushException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise SilentPushException()

    # def handle_failed_response_for_failure(self, response_json):
    #     """Handle the failed response for failure status codes.

    #     If request get authentication error it will regenerate the access token.

    #     Args:
    #         response_json (dict): The JSON response from the API.
    #     """
    #     __method_name = inspect.currentframe().f_code.co_name
    #     try:
    #         error_message = response_json
    #         fail_json = response_json.get("fail", [])
    #         error_json = response_json.get("error")
    #         if fail_json:
    #             error_message = fail_json[0].get("message")
    #         elif error_json:
    #             error_message = error_json.get("message")
    #         applogger.error(
    #             self.log_format.format(
    #                 consts.LOGS_STARTS_WITH,
    #                 __method_name,
    #                 self.azure_function_name,
    #                 error_message,
    #             )
    #         )
    #         raise SilentPushException()
    #     except SilentPushException:
    #         raise SilentPushException()
    #     except Exception as error:
    #         applogger.error(
    #             self.log_format.format(
    #                 consts.LOGS_STARTS_WITH,
    #                 __method_name,
    #                 self.azure_function_name,
    #                 consts.UNEXPECTED_ERROR_MSG.format(error),
    #             )
    #         )
    #         raise SilentPushException()
