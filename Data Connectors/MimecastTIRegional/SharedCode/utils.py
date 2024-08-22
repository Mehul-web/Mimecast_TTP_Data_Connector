"""Utils File."""

import inspect
import requests
import time
import json
from .state_manager import StateManager
from .mimecast_exception import MimecastException
from .logger import applogger
from . import consts
from random import randrange


class Utils:
    """Utils Class."""

    def __init__(self, azure_function_name) -> None:
        """Init Function."""
        self.azure_function_name = azure_function_name
        self.log_format = consts.LOG_FORMAT
        self.headers = {}

    def check_environment_var_exist(self, environment_var):
        """Check the existence of required environment variables.

        Logs the validation process and completion. Raises MimecastException if any required field is missing.

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
                raise MimecastException()
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
            raise MimecastException()

    def get_checkpoint_data(self, checkpoint_obj: StateManager, load_flag=True):
        """Get checkpoint data from a StateManager object.

        Args:
            checkpoint_obj (StateManager): The StateManager object to retrieve checkpoint data from.
            load_flag (bool): A flag indicating whether to load the data as JSON (default is True).

        Returns:
            The retrieved checkpoint data.

        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Fetching checkpoint data",
                )
            )
            checkpoint_data = checkpoint_obj.get()
            if load_flag and checkpoint_data:
                checkpoint_data = json.loads(checkpoint_data)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Checkpoint data = {}".format(checkpoint_data),
                )
            )
            return checkpoint_data
        except json.decoder.JSONDecodeError as json_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.JSON_DECODE_ERROR_MSG.format(json_error),
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

    def post_checkpoint_data(self, checkpoint_obj: StateManager, data, dump_flag=True):
        """Post checkpoint data.

        It post the data to a checkpoint object based on the dump_flag parameter.

        Args:
            checkpoint_obj (StateManager): The StateManager object to post data to.
            data: The data to be posted.
            dump_flag (bool): A flag indicating whether to dump the data as JSON before posting (default is True).
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Posting checkpoint data = {}".format(data),
                )
            )
            if dump_flag:
                checkpoint_obj.post(json.dumps(data))
            else:
                checkpoint_obj.post(data)
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Data posted to azure storage",
                )
            )
        except TypeError as type_error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.TYPE_ERROR_MSG.format(type_error),
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

    def make_rest_call(self, method, url, params=None, data=None, json=None):
        """Make a rest call.

        Args:
            url (str): The URL to make the call to.
            method (str): The HTTP method to use for the call.
            params (dict, optional): The parameters to pass in the call (default is None).
            data (dict, optional): The body(in x-www-form-urlencoded formate) of the request (default is None).
            json (dict, optional): The body(in row formate) of the request (default is None).

        Returns:
            dict: The JSON response if the call is successful.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            for i in range(consts.MAX_RETRIES):
                applogger.debug(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Rest Call, Method :{}, url: {}".format(method, url),
                    )
                )
                response = requests.request(
                    method,
                    url,
                    headers=self.headers,
                    params=params,
                    data=data,
                    json=json,
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
                    self.handle_failed_response_for_success(response_json)
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
                    raise MimecastException()
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
                    response_json = response.json()
                    self.handle_failed_response_for_failure(response_json)
                    continue
                elif response.status_code == 403:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Forbidden, Status code : {}".format(response.status_code),
                        )
                    )
                    response_json = response.json()
                    self.handle_failed_response_for_failure(response_json)
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
                    raise MimecastException()
                elif response.status_code == 409:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "Conflict, Status code : {}".format(response.status_code),
                        )
                    )
                    response_json = response.json()
                    self.handle_failed_response_for_failure(response_json)
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
                            "Internal Server Error, Status code : {}".format(
                                response.status_code
                            ),
                        )
                    )
                    response_json = response.json()
                    self.handle_failed_response_for_failure(response_json)
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
                    raise MimecastException()
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Max retries exceeded.",
                )
            )
            raise MimecastException()
        except MimecastException:
            raise MimecastException()
        except requests.ConnectionError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.CONNECTION_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()
        except requests.HTTPError as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.HTTP_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()
        except requests.RequestException as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.REQUEST_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()

    def handle_failed_response_for_failure(self, response_json):
        """Handle the failed response for failure.

        If request get authentication error it will regenerate the access token.

        Args:
            response_json (dict): The JSON response from the API.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            error_message = response_json
            fail_json = response_json.get("fail", [])
            error_json = response_json.get("error")
            if fail_json:
                error_code = fail_json[0].get("code")
                error_message = fail_json[0].get("message")
                # *For regenerating access token
                if error_code in ["invalid_access_token", "InvalidAccessToken"]:
                    applogger.error(
                        self.log_format.format(
                            consts.LOGS_STARTS_WITH,
                            __method_name,
                            self.azure_function_name,
                            "{}, Generating new token".format(error_message),
                        )
                    )
                    self.authenticate_mimecast_api()
                    return
            elif error_json:
                error_code = error_json.get("code")
                error_message = error_json.get("message")
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    error_message,
                )
            )
            raise MimecastException()
        except MimecastException:
            raise MimecastException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()

    def handle_failed_response_for_success(self, response_json):
        """Handle the failed response for a successful request.

        Check if there is failure in success response or not.

        Args:
            response_json (dict): The JSON response from the request.
        """
        __method_name = inspect.currentframe().f_code.co_name
        try:
            fail_json = response_json.get("fail", [])
            if fail_json:
                try:
                    error_message = fail_json[0].get("errors")[0].get("message")
                except (KeyError, IndexError, ValueError, TypeError):
                    error_message = fail_json
                applogger.error(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Failed response message = {}".format(error_message),
                    )
                )
                raise MimecastException()
            else:
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "No failed response found",
                    )
                )
                return
        except MimecastException:
            raise MimecastException()
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()

    def authenticate_mimecast_api(self):
        """Authenticate mimecast endpoint generate access token and update header."""
        __method_name = inspect.currentframe().f_code.co_name
        try:
            body = {
                "client_id": consts.MIMECAST_CLIENT_ID,
                "client_secret": consts.MIMECAST_CLIENT_SECRET,
                "grant_type": "client_credentials",
            }
            applogger.info(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Generating access token",
                )
            )
            self.headers = {}
            url = ("{}{}".format(consts.BASE_URL, consts.ENDPOINTS["OAUTH2"]),)
            response = self.make_rest_call(
                method="POST",
                url=url,
                data=body,
            )
            if "access_token" in response:
                access_token = response.get("access_token")
                self.headers.update(
                    {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer {}".format(access_token),
                    }
                )
                applogger.info(
                    self.log_format.format(
                        consts.LOGS_STARTS_WITH,
                        __method_name,
                        self.azure_function_name,
                        "Successfully generated access token and header updated",
                    )
                )
                return
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    "Error occurred while fetching the access token from the response = {}".format(
                        response
                    ),
                )
            )
            raise MimecastException()
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
        except Exception as error:
            applogger.error(
                self.log_format.format(
                    consts.LOGS_STARTS_WITH,
                    __method_name,
                    self.azure_function_name,
                    consts.UNEXPECTED_ERROR_MSG.format(error),
                )
            )
            raise MimecastException()
