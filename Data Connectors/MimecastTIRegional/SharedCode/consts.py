"""Module with constants and configurations for the Mimecast integration."""

import os

LOG_LEVEL = os.environ.get("LogLevel", "INFO")
LOGS_STARTS_WITH = "Mimecast"
LOG_FORMAT = "{}(method = {}) : {} : {}"


# *Sentinel related constants
AZURE_CLIENT_ID = os.environ.get("Azure_Client_Id", "")
AZURE_CLIENT_SECRET = os.environ.get("Azure_Client_Secret", "")
AZURE_TENANT_ID = os.environ.get("Azure_Tenant_Id", "")
WORKSPACE_KEY = os.environ.get("Workspace_Key", "")
WORKSPACE_ID = os.environ.get("Workspace_Id", "")

# *Mimecast related constants
MIMECAST_CLIENT_ID = os.environ.get("Mimecast_client_id")
MIMECAST_CLIENT_SECRET = os.environ.get("Mimecast_client_secret")

BASE_URL = os.environ.get("BaseUrl")
ENDPOINTS = {
    "OAUTH2": "/oauth/token",
    "TTP_URL": "/api/ttp/url/get-logs",
    "SEG_DLP": "/api/dlp/get-logs",
}

TABLE_NAME = {"TTP_URL": "Ttp_Url", "SEG_DLP": "Seg_Dlp"}
TTP_URL_FUNCTION_NAME = "TTP_URL"
SEG_DLP_FUNCTION_NAME = "SEG_DLP"


# *Error Messages for Exception
UNEXPECTED_ERROR_MSG = "Unexpected error : Error-{}"
HTTP_ERROR_MSG = "HTTP error : Error-{}"
REQUEST_ERROR_MSG = "Request error : Error-{}"
CONNECTION_ERROR_MSG = "Connection error : Error-{}"
KEY_ERROR_MSG = "Key error : Error-{}"
TYPE_ERROR_MSG = "Type error : Error-{}"
VALUE_ERROR_MSG = "Value error : Error-{}"
JSON_DECODE_ERROR_MSG = "JSONDecode error : Error-{}"

# *checkpoint related constants
CONN_STRING = os.environ.get("Connection_String")
FILE_SHARE_NAME = os.environ.get("File_Share_Name")

# *Extra constants
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_CHUNK_SIZE = 1024 * 1024
MAX_RETRIES = 3
