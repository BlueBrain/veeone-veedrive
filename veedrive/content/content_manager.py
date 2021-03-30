import logging
import os
import os.path

from .. import config
from ..utils.asynchro import run_async
from . import image, video
from .fs_manager import validate_path

logger = logging.getLogger(__name__)


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
        response[
            "scaled"
        ] = f"{config.CONTENT_URL}/scaled/{path}?width={client_size['width']}&height={client_size['height']}"
    return response


def get_file_urls(path):
    """Get URLs of a file

    :param path: relative to sandboxpath path of the file
    :type path: str
    :return: a dictionnary with all available URLs which can be used to fetch the file
    :rtype: dict
    """
    return _create_file_url_response(path)


async def get_scaled_image(path, client_width, client_height, scaling_mode="fit"):
    """[summary]

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
                image.resize_image,
                absolute_path,
                client_width,
                client_height,
                scaling_mode,
                ext,
            )

            return scaled_image, "image/" + file_format


async def get_thumbnail(path, width=256, height=256, scaling_mode="fit"):
    """Get a thumbnail of object (image, video, document)

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

    file_extension = os.path.splitext(path)[1]
    if file_extension in config.SUPPORTED_IMAGE_EXTENSIONS:
        thumbnail, image_format = await run_async(
            image.resize_image, absolute_path, width, height, scaling_mode, ".jpg"
        )
        return thumbnail, "image/" + image_format
    if file_extension == ".pdf":
        thumbnail, image_format = await image.generate_pdf(
            absolute_path, width, height, scaling_mode
        )
        return thumbnail, "image/" + image_format
    if file_extension in config.SUPPORTED_VIDEO_EXTENSIONS:
        thumbnail = await video.get_video_thumbnail(
            absolute_path, width, height, scaling_mode
        )
        return thumbnail, "image/gif"


def _create_file_url_response(path):
    absolute_path = os.path.join(config.SANDBOX_PATH, path)
    validate_path(absolute_path)
    response = {
        "url": f"{config.STATIC_CONTENT_URL}/{path}",
        "thumbnail": f"{config.CONTENT_URL}/thumb/{path}",
        "size": os.path.getsize(absolute_path),
    }
    return response
