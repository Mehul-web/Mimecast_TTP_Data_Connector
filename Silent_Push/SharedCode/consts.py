"""Module with constants and configurations for the SilentPush integration."""

import os


LOG_LEVEL = os.environ.get("LogLevel", "INFO")
LOGS_STARTS_WITH = "SilentPush"
LOG_FORMAT = "{}(method = {}) : {} : {}"


# *Sentinel related constants
AZURE_CLIENT_ID = os.environ.get("Azure_Client_Id", "")
AZURE_CLIENT_SECRET = os.environ.get("Azure_Client_Secret", "")
AZURE_TENANT_ID = os.environ.get("Azure_Tenant_Id", "")
WORKSPACE_KEY = os.environ.get("WorkspaceKey", "")
WORKSPACE_ID = os.environ.get("WorkspaceID", "")
SILENTPUSH_API_Key = os.environ.get("SilentPush_API_Key", "")


BASE_URL = os.environ.get("BaseURL", "https://app.silentpush.com")
ENDPOINTS = {
    "THREAT_RANKING_COUNT": "/api/v2/iocs/threat-ranking-count",
    "THREAT_RANKING": "/api/v2/iocs/threat-ranking",
}

MAX_PAGE_SIZE = 100
TABLE_NAME = {"THREAT_RANKING": "Threat_ranking"}
IOFA_FUNCTION_NAME = "IOFA_FEED"
FUNCTION_APP_TIMEOUT_SECONDS = 570
SOURCE_UUID = os.environ.get("SourceUUID", "")

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
CONN_STRING = os.environ.get("AzureWebJobsStorage")
FILE_PATH = "SilentPushIOFA"
FILE_SHARE_NAME = os.environ.get("FileShareName", "silentpush-checkpoints")


# *Extra constants
MAX_FILE_SIZE = 20 * 1024 * 1024
MAX_CHUNK_SIZE = 1024 * 1024
MAX_RETRIES = 3
