"""Logic for getting fillable areas based on horizontal lines."""

import itertools

import cv2
import numpy as np
from PIL import Image, ImageDraw

from app.logic.fillable_areas.constants import ColorGray
from app.logic.fillable_areas.geometry.shapes import Line
from app.logic.fillable_areas.geometry.shapes import Rectangle
from app.logic.fillable_areas.geometry.utils import find_intersection

MARGIN = 5
TOLERANCE = 5
VERTICAL_GROW_STEP = 1
HORIZONTAL_GROW_STEP = 5

HORIZONTAL_KERNEL = (30, 1)
VERTICAL_KERNEL = (1, 50)


def find_line_fillable_areas(gray, fillable_area_limits):
    """Find fillable areas based on horizontal lines.

    Args:
        gray (numpy.ndarray): Gray scale representation of the source image.
        line_rectangles (list): List of the rectangles tied to horizontal
            lines on the image.
        fillable_area_limits (dict): Dimension limits for fillable areas.

    Returns:
        list: List of fillable areas on empty areas.
    """
    thresh = cv2.threshold(
        gray, ColorGray.BLACK.value, ColorGray.WHITE.value,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]
    # Image.fromarray(thresh).show()
    # Horizontal lines
    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, HORIZONTAL_KERNEL
    )
    detect_horizontal = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2
    )
    # Image.fromarray(detect_horizontal).show()
    cnts = cv2.findContours(
        detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    horizontal_lines = []

    # image_with_horizontal_boxes = Image.fromarray(detect_horizontal)
    # draw = ImageDraw.Draw(image_with_horizontal_boxes)
    for i, c in enumerate(cnts):
        x, y, w, h = cv2.boundingRect(c)
        # draw.rectangle((x, y, x + w, y), outline='white', width=10)
        horizontal_lines.append(Line(x, y, x + w, y))
    # image_with_horizontal_boxes.show()

    # Vertical lines
    vertical_lines = []
    vertical_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, VERTICAL_KERNEL
    )
    detect_vertical = cv2.morphologyEx(
        thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2
    )
    # Image.fromarray(detect_vertical).show()
    cnts = cv2.findContours(
        detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # image_with_vertical_boxes = Image.fromarray(detect_vertical)
    # draw = ImageDraw.Draw(image_with_vertical_boxes)
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        # draw.rectangle((x + w, y, x + w, y + h), outline='white', width=10)
        vertical_lines.append(Line(x + w, y, x + w, y + h))
    # image_with_vertical_boxes.show()

    # Split lines
    lines = []
    # image_with_segments = Image.fromarray(thresh)
    # draw = ImageDraw.Draw(image_with_segments)
    for i, hl in enumerate(horizontal_lines):
        split_points = []
        for vl in vertical_lines:
            x, y = find_intersection(hl, vl)
            if hl.x1 - TOLERANCE <= x <= hl.x2 + TOLERANCE and vl.y1 - TOLERANCE <= y <= vl.y2 + TOLERANCE:
                split_points.append((x, y))
        if split_points:
            all_points = sorted(
                list(set([hl.x1, hl.x2] + [x for x, y in split_points]))
            )
            segments = _in_pairs(all_points)
            for segment in segments:
                x_start, x_end = segment
                if x_end - x_start >= fillable_area_limits['table_cell_min_width']:
                    line = Line(x_start, hl.y1, x_end, hl.y2)
                    # draw.rectangle((x_start, hl.y1, x_end, hl.y2), outline='white', width=10)
                    lines.append(line)
        else:
            lines.append(hl)
    # image_with_segments.show()
    # Horizontal line rectangles
    line_rectangles = []
    tables_upper_borders = _find_tables_upper_lines(gray)

    # debug
    # image_with_fillable_areas = Image.fromarray(gray)
    # draw = ImageDraw.Draw(image_with_fillable_areas)
    for i, line in enumerate(lines):
        if i>=0:  # todo: change i to line number (from bottom to top) -> debug
            rectangle = _find_fillable_line_area(
                thresh, line, fillable_area_limits, tables_upper_borders
            )
            if rectangle:
                x1, y1, x2, y2 = rectangle
                r = Rectangle(x1, y1, x2, y2)
                line_rectangles.append(r)
                # draw.rectangle((x1, y1, x2, y2), outline='black', width=10)
                # draw.text((x1+10, y1+10), str(i), fill='black')
    # draw.rectangle(tables_upper_borders[0], outline='black', width=10)
    # image_with_fillable_areas.show()
    return line_rectangles


def _in_pairs(iterable):
    """Pairs of values from the iterable object."""
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def _find_tables_upper_lines(gray):
    # ToDo: add multiple tables support
    """
    Find upper lines of tables.
    We need to find upper lines of tables to avoid detecting upper border as a line.
    """
    # return []
    table_coords = None
    upper_borders_coordinates = []
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    detect_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    detect_vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Combine horizontal and vertical lines in a new third image, with an intersection point at each cell
    mask = cv2.addWeighted(detect_horizontal, 0.5, detect_vertical, 0.5, 0.0)

    # Find the contours in the combined image
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Assuming the table is the largest rectangle-like contour, find the largest area contour
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        # ToDo: use table_min_cell_width here
        if h > 200 and w > 200:
            table_coords = (x, y, x + w, y + h)

    # Draw the largest contour (table border) on the original image for visualization
    if table_coords:
        upper_borders_coordinates.append((x, y, x + w, y))
    return upper_borders_coordinates


def _find_fillable_line_area(image, line, fillable_area_limits, tables_upper_borders):
    """Find fillable area above the line."""
    min_height = fillable_area_limits['min_height']
    max_height = fillable_area_limits['max_height']

    for table_upper_border in tables_upper_borders:
        if table_upper_border[1] == line.y1 and line.x2-line.x1 <= table_upper_border[2]-table_upper_border[0]:
            return None

    all_min_area = image[line.y1 - min_height:line.y1, line.x1 + MARGIN:line.x2 - MARGIN]
    # is_suitable_area means that there are all black pixels in the area (0 because of binary image)
    is_suitable_area = (
            all_min_area.shape[0] and
            all_min_area.shape[1] and
            np.amax(all_min_area) == 0
    )
    if is_suitable_area:
        for i in range(1, max_height - min_height + 1, VERTICAL_GROW_STEP):
            current_area = (
                image[
                line.y1 - min_height - i:line.y1,
                line.x1 + MARGIN:line.x2 - MARGIN]
            )
            is_current_area_suitable = (
                    current_area.shape[0] and
                    current_area.shape[1] and
                    np.amax(current_area) == 0
            )
            if not is_current_area_suitable:
                return (
                    line.x1 + MARGIN,
                    line.y1 - min_height - i + VERTICAL_GROW_STEP,
                    line.x2 - MARGIN,
                    line.y1)
        return (
            line.x1 + MARGIN, line.y1 - max_height,
            line.x2 - MARGIN, line.y1)
    return None