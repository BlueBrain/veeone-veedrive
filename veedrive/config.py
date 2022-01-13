import logging
import os

import pytz

DEFAULT_HOST = os.getenv("VEEDRIVE_DEFAULT_HOST", "0.0.0.0")
DEFAULT_PORT = os.getenv("VEEDRIVE_DEFAULT_PORT", 4444)

SANDBOX_PATH = os.path.normpath(os.getenv("VEEDRIVE_MEDIA_PATH", "~/"))
THUMBNAIL_CACHE_PATH = os.path.join(SANDBOX_PATH, "cache")

STATIC_CONTENT_URL = os.getenv(
    "VEEDRIVE_STATIC_CONTENT_URL", f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/static"
)
CONTENT_URL = os.getenv(
    "VEEDRIVE_CONTENT_URL", f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/content"
)
DB_NAME = os.getenv("VEEDRIVE_DB_NAME", "test_database")
DB_HOST = os.getenv("VEEDRIVE_DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("VEEDRIVE_DB_PORT", 27017)

SEARCH_FS_KEEP_FINISHED_INTERVAL = int(
    os.getenv("VEEDRIVE_SEARCH_FS_KEEP_FINISHED_INTERVAL", 10)
)
SEARCH_FS_THREAD_TIMEOUT = int(os.getenv("VEEDRIVE_SEARCH_FS_THREAD_TIMEOUT", 600))
SEARCH_FS_PURGE_LOOP_INTERVAL = int(
    os.getenv("VEEDRIVE_SEARCH_FS_PURGE_LOOP_INTERVAL", 60)
)

if os.getenv("VEEDRIVE_LOG_LEVEL") == "DEBUG":
    logger_level = logging.DEBUG
else:
    logger_level = logging.INFO

TIMEZONE = pytz.timezone(os.getenv("VEEDRIVE_TIMEZONE", "CET"))

# Constants.  Don't change!

IMAGE_EXTENSIONS_TO_ENCODE_TO_JPG = [".jpg", ".tiff"]
IMAGE_EXTENSIONS_TO_ENCODE_TO_PNG = [".png"]

SUPPORTED_IMAGE_EXTENSIONS = [".png", ".jpg", ".gif", ".tiff", ".jpeg", ".dsc"]
SUPPORTED_VIDEO_EXTENSIONS = [".avi", ".mp4", ".webm", ".mkv", ".mov"]
SUPPORTED_DOC_EXTENSIONS = [".pdf"]
SUPPORTED_THUMBNAIL_EXTENSIONS = (
    SUPPORTED_IMAGE_EXTENSIONS + SUPPORTED_VIDEO_EXTENSIONS + SUPPORTED_DOC_EXTENSIONS
)

FIT_TRANSFORM_IMAGE = "fit"
FILL_TRANSFORM_IMAGE = "fill"

MALFORMED_REQUEST = 0
PERMISSION_DENIED = 1
PATH_NOT_FOUND = 2
WRONG_FILE_TYPE_REQUESTED = 5
PRESENTATION_NOT_FOUND = 11
PRESENTATION_DB_ISSUE = 12
