"""Logic for getting fillable areas."""

import cv2
import numpy as np

from app.logic.fillable_areas.empty_areas import find_empty_fillable_areas
from app.logic.fillable_areas.horizonal_line_areas import find_line_fillable_areas
from app.logic.fillable_areas.checkbox_areas import find_checkbox_fillable_areas


def find_fillable_areas(image):
    """Find all fillable areas.

    Args:
        image (numpy.ndarray): Source image.

    Returns:
        dict: Lists of found fillable areas.
    """
    fillable_area_limits = _calc_fillable_area_limits(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    line_rectangles = find_line_fillable_areas(gray, fillable_area_limits)
    empty_fillable_rectangles = find_empty_fillable_areas(
        gray, line_rectangles, fillable_area_limits)
    checkbox_areas = find_checkbox_fillable_areas(gray)
    # checkbox_areas = []

    filtered_line_rectangles = _filter_areas(
        line_rectangles, fillable_area_limits)
    filtered_empty_fillable_rectangles = _filter_areas(
        empty_fillable_rectangles, fillable_area_limits)
    return {
        'line_areas': filtered_line_rectangles,
        'empty_region_areas': filtered_empty_fillable_rectangles,
        'checkbox_areas': checkbox_areas,
    }


def _calc_fillable_area_limits(image):
    """Calculate fillable area limits by image size."""
    image_height, image_width, _ = image.shape
    min_height = int(image_height * .015)
    max_height = int(min_height * 1.2)
    min_width = int(image_width * .015)
    max_width = int(image_width * 0.9)
    table_cell_min_width = int(image_width * 0.2)
    return {
        'min_height': min_height,
        'max_height': max_height,
        'min_width': min_width,
        'max_width': max_width,
        'table_cell_min_width': table_cell_min_width
    }


def _filter_areas(areas, fillable_area_limits):
    """Filter found areas."""
    # TODO: Define more rules if needed
    return [
        area for area in areas
        if area.x2 - area.x1 >= fillable_area_limits['min_width']
    ]
