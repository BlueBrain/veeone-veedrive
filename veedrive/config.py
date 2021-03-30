import logging
import os

import pytz

SANDBOX_PATH = os.getenv("VEEDRIVE_MEDIA_PATH", "~/")
STATIC_CONTENT_URL = os.getenv(
    "VEEDRIVE_STATIC_CONTENT_URL", "http://localhost:4444/static"
)
CONTENT_URL = os.getenv("VEEDRIVE_CONTENT_URL", "http://localhost:4444/content")
DB_NAME = os.getenv("VEEDRIVE_DB_NAME", "test_database")

if os.getenv("VEEDRIVE_LOG_LEVEL") == "DEBUG":
    logger_level = logging.DEBUG
else:
    logger_level = logging.INFO

TIMEZONE = pytz.timezone(os.getenv("VEEDRIVE_TIMEZONE", "CET"))

SUPPORTED_IMAGE_EXTENSIONS = [".png", ".jpg", ".gif", ".tiff"]
IMAGE_EXTENSIONS_TO_ENCODE_TO_JPG = [".jpg", ".tiff"]
IMAGE_EXTENSIONS_TO_ENCODE_TO_PNG = [".png"]
SUPPORTED_VIDEO_EXTENSIONS = [".avi", ".mp4"]

FIT_TRANSFORM_IMAGE = "fit"
FILL_TRANSFORM_IMAGE = "fill"
