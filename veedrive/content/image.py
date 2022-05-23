import logging
import subprocess

import cv2
import numpy

import veedrive.config as config


def resize_image(path, box_width, box_height, scaling_mode, ext):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    return transform_image(img, box_width, box_height, scaling_mode, ext)


def generate_pdf(path, box_width, box_height, scaling_mode):
    im_args = ["convert", "-background", "white", path + "[0]", "bmp:-"]
    process = subprocess.Popen(im_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    buf = numpy.frombuffer(stdout, numpy.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
    return transform_image(img, box_width, box_height, scaling_mode, ".jpg")


def transform_image(img: numpy.ndarray, box_width, box_height, scaling_mode, ext):
    image_height, image_width = img.shape[:2]
    image_aspect = image_width / image_height

    image_smaller_than_box = (
        image_aspect > 1.0 and box_width >= image_width
    ) or (image_aspect <= 1.0 and box_height >= image_height)
    if image_smaller_than_box:
        return _encode_image(img, ext)

    if scaling_mode == config.FIT_TRANSFORM_IMAGE:
        resized_image = _resize_to_fit(
            img, image_width, image_height, box_width, box_height
        )
    elif scaling_mode == config.FILL_TRANSFORM_IMAGE:
        resized_image = _resize_to_fill(
            img, image_width, image_height, box_width, box_height
        )
    elif scaling_mode == config.PRESERVE_ASPECT:
        resized_image = _resize(img, box_width, box_height)
    else:
        raise Exception("Not supported scaling_mode")

    return _encode_image(resized_image, ext)


def _resize(img: numpy.ndarray, box_width, box_height):
    image_height, image_width = img.shape[:2]
    image_aspect = image_width / image_height

    try:
        if image_aspect > 1.0:
            if round(box_width / image_aspect) > box_height:
                target_size = (round(box_height * image_aspect), box_height)
            else:
                target_size = (box_width, round(box_width / image_aspect))
            return cv2.resize(
                img,
                target_size,
                interpolation=cv2.INTER_AREA,
            )
        else:
            if round(box_height * image_aspect) > box_width:
                target_size = (box_width, round(box_width / image_aspect))
            else:
                target_size = (round(box_height * image_aspect), box_height)
            return cv2.resize(
                img,
                target_size,
                interpolation=cv2.INTER_AREA,
            )
    except Exception as e:
        logging.error(f"ERORR: {str(e)}")


def _resize_to_fit(img: numpy.ndarray, image_width, image_height, box_width, box_height):
    requested_aspect = box_width / box_height
    image_aspect = image_width / image_height

    if requested_aspect > image_aspect:
        logging.debug(
            f"requested box is wider than image: {requested_aspect} : {image_aspect}"
        )
        logging.debug("so we take height and use it as a basis for calculation")

        requested_aspect = (round(box_height * image_aspect), box_height)
    else:
        logging.debug(
            f"requested box is higher or eq to image: {requested_aspect} : {image_aspect}"
        )
        logging.debug("so we take width and use it as a basis for calculation")
        requested_aspect = (box_width, round(box_width / image_aspect))
    return cv2.resize(img, requested_aspect, interpolation=cv2.INTER_AREA)


def _resize_to_fill(img: numpy.ndarray, image_width, image_height, box_width, box_height):
    """fill the specified box with the output (cropping possible)"""

    ratio = max(box_width / image_width, box_height / image_height)
    width = round(image_width * ratio)
    height = round(image_height * ratio)

    resized_image = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    left = (width - box_width) / 2
    top = (height - box_height) / 2
    right = width - left
    bottom = height - top

    left, top, right, bottom = [round(x) for x in (left, top, right, bottom)]

    return resized_image[top:bottom, left:right]


def _encode_image(image: numpy.ndarray, extensions):
    if extensions in config.IMAGE_EXTENSIONS_TO_ENCODE_TO_JPG:
        encoded = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])[1]
        file_format = "jpg"
    elif extensions in config.IMAGE_EXTENSIONS_TO_ENCODE_TO_PNG:
        encoded = cv2.imencode(".png", image, [int(cv2.IMWRITE_PNG_COMPRESSION), 90])[1]
        file_format = "png"
    else:
        raise Exception("Unsupported extension")
    return encoded.tobytes(), file_format
