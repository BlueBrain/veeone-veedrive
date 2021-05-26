import logging
import os

import pytz

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 4444

SANDBOX_PATH = os.getenv("VEEDRIVE_MEDIA_PATH", "~/")
STATIC_CONTENT_URL = os.getenv(
    "VEEDRIVE_STATIC_CONTENT_URL", f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/static"
)
CONTENT_URL = os.getenv(
    "VEEDRIVE_CONTENT_URL", f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/content"
)
DB_NAME = os.getenv("VEEDRIVE_DB_NAME", "test_database")
DB_HOST = os.getenv("VEEDRIVE_DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("VEEDRIVE_DB_PORT", 27017)

if os.getenv("VEEDRIVE_LOG_LEVEL") == "DEBUG":
    logger_level = logging.DEBUG
else:
    logger_level = logging.INFO

TIMEZONE = pytz.timezone(os.getenv("VEEDRIVE_TIMEZONE", "CET"))

# Constants.  Don't change!

SUPPORTED_IMAGE_EXTENSIONS = [".png", ".jpg", ".gif", ".tiff"]
IMAGE_EXTENSIONS_TO_ENCODE_TO_JPG = [".jpg", ".tiff"]
IMAGE_EXTENSIONS_TO_ENCODE_TO_PNG = [".png"]
SUPPORTED_VIDEO_EXTENSIONS = [".avi", ".mp4"]

FIT_TRANSFORM_IMAGE = "fit"
FILL_TRANSFORM_IMAGE = "fill"

MALFORMED_REQUEST = 0
PERMISSION_DENIED = 1
PATH_NOT_FOUND = 2
WRONG_FILE_TYPE_REQUESTED = 5
SCENE_NOT_FOUND = 11
SCENE_DB_ISSUE = 12
