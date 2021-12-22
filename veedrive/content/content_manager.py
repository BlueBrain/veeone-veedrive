import logging
import os
import os.path
from pathlib import Path

import cv2
import numpy

from .. import config
from ..utils.asynchro import run_async
from . import utils
from .image import generate_pdf, resize_image
from .utils import sanitize_path, validate_path
from .video import get_video_thumbnail

logger = logging.getLogger(__name__)


@sanitize_path
def get_image_urls(path, client_size=None):
    """Get URLs of an image

    :param path: relative to sandboxpath path of the image
    :type path: str
    :param client_size: client's display size (used to generate optimal, scaled image), defaults to None
    :type client_size: dict, optional
    :return: a dictionnary with all available URLs which can be used to fetch the image
    :rtype: dict
    """

    response = _create_file_url_response(path)
    if client_size:
        response = _add_scaled_url(response, path, client_size)

    return response


@sanitize_path
def get_file_urls(path):
    """Get URLs of a file

    :param path: relative to sandboxpath path of the file
    :type path: str
    :return: a dictionnary with all available URLs which can be used to fetch the file
    :rtype: dict
    """

    return _create_file_url_response(path)


@sanitize_path
async def get_scaled_image(path, client_width, client_height, scaling_mode="fit"):
    """Get a scaled image, fitting or filling client's display

    :param path: relative to sandboxpath path of object
    :type path: str
    :param client_width: width of client's display
    :type client_width: int
    :param client_height: height of client's display
    :type client_height: int
    :param scaling_mode: mode to scale an image. 'Fit' will not crop the image if requested sizebox
        aspect ratio differs from object aspect ratio and may fill sizebox in only one axis.
        'Fill' will fill sizebox in both axis, cropping may be applied, defaults to 'fit'
    :type scaling_mode: str
    :return: a scaled image and its http content-type
    :rtype: tuple(binary, str)
    """
    absolute_path = os.path.join(config.SANDBOX_PATH, path)
    validate_path(absolute_path)
    for ext in config.SUPPORTED_IMAGE_EXTENSIONS:
        if os.path.splitext(path)[1] == ext:
            scaled_image, file_format = await run_async(
                resize_image,
                absolute_path,
                client_width,
                client_height,
                scaling_mode,
                ext,
            )

            return scaled_image, "image/" + file_format


def cache_thumbnail(file, cache_folder):
    dir_hash, filename_hash = utils.get_dir_file_hash_pair(file)
    thumbnail_path = Path(os.path.join(cache_folder, dir_hash, filename_hash))
    if os.path.exists(thumbnail_path):
        logger.info(f"[INFO] Skipping thumbnail generation of: {file}")
        raise FileExistsError
    try:
        thumbnail = get_thumbnail(file)
    except cv2.error as e:
        logger.error(f"[ERROR] opencv issue with {file}, message {str(e)}")
        raise
    except Exception as e:
        logger.error(
            f"[ERROR] issue with {file}, exception {type(e).__name__}, message: {str(e)}",
            flush=True,
        )
        raise
    try:
        buf = numpy.frombuffer(thumbnail[0], numpy.uint8)
        buf.tofile(str(thumbnail_path))
        logger.info(f"[INFO] Generated thumbnail of: {file}")
    except Exception as e:
        logger.error(f"[ERROR] Saving exception: {str(e)} on {file}")
        raise
    return thumbnail_path


@sanitize_path
def get_thumbnail(path, width=256, height=256, scaling_mode="fit"):
    """Get a thumbnail of an object (image, video, document)

    :param path: relative to sandboxpath path of object
    :type path: str
    :param width: width of a sizebox, defaults to 256
    :type width: int
    :param height: height of a sizebox, defaults to 256
    :type height: int
    :param scaling_mode: mode to generate a thumbnail. 'Fit' will not crop the image if requested sizebox
        aspect ratio differs from object aspect ratio and may fill sizebox in only one axis.
        'Fill' will fill sizebox in both axis, cropping may be applied, defaults to 'fit'
    :type scaling_mode: str

    :return: a thumbnail and its http content-type
    :rtype: tuple(binary, str)
    """
    absolute_path = os.path.join(config.SANDBOX_PATH, path)
    validate_path(absolute_path)

    file_extension = os.path.splitext(path)[1].lower()

    if file_extension not in config.SUPPORTED_THUMBNAIL_EXTENSIONS:
        raise TypeError(
            f"Extension {file_extension} not supported for thumbnail generation"
        )

    if file_extension in config.SUPPORTED_IMAGE_EXTENSIONS:
        thumbnail, image_format = resize_image(
            absolute_path, width, height, scaling_mode, ".jpg"
        )
        return thumbnail, "image/" + image_format
    if file_extension == ".pdf":
        thumbnail, image_format = generate_pdf(
            absolute_path, width, height, scaling_mode
        )
        return thumbnail, "image/" + image_format
    if file_extension in config.SUPPORTED_VIDEO_EXTENSIONS:
        thumbnail = get_video_thumbnail(absolute_path, width, height, scaling_mode)
        return thumbnail, "image/gif"


def _create_file_url_response(path):
    absolute_path = os.path.join(config.SANDBOX_PATH, path)
    validate_path(absolute_path)
    ext = os.path.splitext(path)[1]
    thubmnail_url = (
        f"{config.CONTENT_URL}/thumb/{path}"
        if ext in config.SUPPORTED_THUMBNAIL_EXTENSIONS
        else None
    )

    response = {
        "url": f"{config.STATIC_CONTENT_URL}/{path}",
        "thumbnail": thubmnail_url,
        "size": os.path.getsize(absolute_path),
    }
    return response


def _add_scaled_url(response, path, client_size):
    ext = os.path.splitext(path)[1]
    scaled_url = (
        f"{config.CONTENT_URL}/scaled/{path}?width={client_size['width']}&height={client_size['height']}"
        if ext in config.SUPPORTED_THUMBNAIL_EXTENSIONS
        else None
    )

    response["scaled"] = scaled_url
    return response
