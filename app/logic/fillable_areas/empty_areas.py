"""Logic for getting fillable areas in empty regions."""

import copy

import cv2
import numpy as np

from app.logic.fillable_areas.constants import ColorGray, ColorRGB
from app.logic.fillable_areas.geometry.shapes import Rectangle

OUTER_FIELD_WIDTH = 150
GAUSSIAN_BLUR_KERNEL = (15, 15)
DILATE_KERNEL = (7, 7)


def find_empty_fillable_areas(gray, line_rectangles, fillable_area_limits):
    """Find fillable areas on empty spots in the image.

    Args:
        gray (numpy.ndarray): Gray scale representation of the source image.
        line_rectangles (list): List of the rectangles tied to horizontal
            lines on the image.
        fillable_area_limits (dict): Dimension limits for fillable areas.

    Returns:
        list: List of fillable areas on empty areas.
    """
    prepared_image = _mark_unfillable_areas(gray, line_rectangles)
    contours = _get_empty_areas_contours(prepared_image)
    prepared_image = _exclude_line_areas(gray, line_rectangles)
    found_rectangles = _find_fillable_areas(
        prepared_image, contours, fillable_area_limits)
    return merge_found_rectangles(found_rectangles, fillable_area_limits)


def _mark_unfillable_areas(gray, line_rectangles):
    """Mark all occupied areas with black color."""
    image_height, image_width = gray.shape[:2]
    blur = cv2.GaussianBlur(gray, GAUSSIAN_BLUR_KERNEL, 0)
    thresh_lines = cv2.threshold(
        blur, ColorGray.WHITE.value - 1, ColorGray.WHITE.value,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Create rectangular structuring element and dilate
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, DILATE_KERNEL)
    dilate = cv2.dilate(thresh_lines, kernel, iterations=5)
    # Draw doc borders TODO: detect borders automatically
    invert = cv2.bitwise_not(dilate)
    cv2.rectangle(
        invert, (0, 0), (image_width, OUTER_FIELD_WIDTH),
        ColorRGB.BLACK.value, -1)
    cv2.rectangle(
        invert, (0, 0), (OUTER_FIELD_WIDTH, image_height),
        ColorRGB.BLACK.value, -1)
    cv2.rectangle(
        invert, (0, image_height - OUTER_FIELD_WIDTH),
        (image_width, image_height),
        ColorRGB.BLACK.value, -1)
    cv2.rectangle(
        invert, (image_width - OUTER_FIELD_WIDTH, 0),
        (image_width, image_height),
        ColorRGB.BLACK.value, -1)
    # add line rectangles
    for line in line_rectangles:
        cv2.rectangle(
            invert, (line.x1, line.y1), (line.x2, line.y2),
            ColorGray.BLACK.value, -1)
    # remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, GAUSSIAN_BLUR_KERNEL)
    opening = cv2.morphologyEx(invert, cv2.MORPH_OPEN, kernel)
    return opening.copy()


def _get_empty_areas_contours(prepared_image):
    """Get rectangles around empty areas."""
    imghsv = cv2.cvtColor(prepared_image, cv2.COLOR_GRAY2BGR)
    imghsv = cv2.cvtColor(imghsv, cv2.COLOR_BGR2HSV)
    sensitivity = 1
    lower_white = np.array([0, 0, 255 - sensitivity])
    upper_white = np.array([255, sensitivity, 255])
    mask_white = cv2.inRange(imghsv, lower_white, upper_white)
    contours, _ = cv2.findContours(
        mask_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def _exclude_line_areas(gray, line_rectangles):
    """Get image with excluded previously found areas."""
    image = gray.copy()
    for line in line_rectangles:
        cv2.rectangle(
            image, (line.x1, line.y1), (line.x2, line.y2),
            ColorRGB.BLACK.value, -1)
    return image


def _find_fillable_areas(
        prepared_image, contours, fillable_area_limits):
    """Split found areas by lines."""
    min_height = fillable_area_limits['min_height']
    found_rectangles = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        found_rectangles += _find_fillable_areas_within_contour(
            prepared_image, x, y, x + w, y + h, min_height)
    return found_rectangles


def _find_fillable_areas_within_contour(gray_image, x1, y1, x2, y2, edge):
    """Split contour by lines."""
    image_height, image_width = gray_image.shape[:2]
    rectangles = []
    for y in range(y1, y2, edge):
        current_rectangle = None
        for x in range(x1, x2, edge):
            # TODO: find some more elegant way
            if x + edge > image_width - OUTER_FIELD_WIDTH:
                continue
            current_area = gray_image[y:y + edge, x:x + edge]
            current_cell_fillable = np.amin(current_area) != 0
            if current_cell_fillable:
                if not current_rectangle:
                    current_rectangle = Rectangle(x, y, x + edge, y + edge)
                else:
                    current_rectangle.x2 = x + edge
                    current_rectangle.y2 = y + edge
            else:
                if current_rectangle:
                    rectangles.append(current_rectangle)
                    current_rectangle = None
            cv2.rectangle(
                gray_image, (x, y), (x + edge - 1, y + edge - 1),
                ColorRGB.BLACK.value, -1)
        if current_rectangle:
            rectangles.append(current_rectangle)
    return rectangles


def merge_found_rectangles(found_rectangles, fillable_area_limits):
    """Merge nearby areas if possible."""
    step = fillable_area_limits['min_height']
    sorted_rectangles = {
        r.coordinates: r
        for r in sorted(found_rectangles, key=lambda r: (r.y1, r.x1))
    }
    processed_retangles = set()
    merged_rectangles = []
    for coordinates, rectangle in sorted_rectangles.items():
        if rectangle not in processed_retangles:
            processed_retangles.add(rectangle)
            r = copy.copy(rectangle)
            i = 1
            while new_rectangle := sorted_rectangles.get(
                    (rectangle.x1, rectangle.y1 + step * i,
                     rectangle.x2, rectangle.y2 + step * i)
            ):
                r.y2 = new_rectangle.y2
                processed_retangles.add(new_rectangle)
                i += 1
            merged_rectangles.append(r)
    return merged_rectangles
