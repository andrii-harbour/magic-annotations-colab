import cv2
import numpy as np

from app.logic.fillable_areas.geometry.shapes import Rectangle

MIN_SIDE_LENGTH = 15
HORIZONTAL_KERNEL = (1, MIN_SIDE_LENGTH)
VERTICAL_KERNEL = (MIN_SIDE_LENGTH, 1)


def find_checkbox_fillable_areas(gray):
    _, img_bin = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    img_bin = 255 - img_bin

    # kernel to detect horizontal lines
    kernal_h = np.ones(HORIZONTAL_KERNEL, np.uint8)

    # kernel to detect vertical lines
    kernal_v = np.ones((MIN_SIDE_LENGTH, 1), np.uint8)

    # horizontal kernel on the image
    img_bin_h = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_h)

    # verical kernel on the image
    img_bin_v = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_v)

    # combining the image
    img_bin_final = img_bin_h | img_bin_v
    _, labels, stats, _ = cv2.connectedComponentsWithStats(~img_bin_final, connectivity=8, ltype=cv2.CV_32S)

    checkboxes = []
    for x, y, w, h, area in stats[2:]:
        if np.abs(x - (x + w)) > MIN_SIDE_LENGTH and np.abs(y - (y + h)) > MIN_SIDE_LENGTH:
            ratio = np.sqrt(w ** 2) / np.sqrt(h ** 2)
            if 0.9 <= ratio <= 1.1:
                checkboxes.append(Rectangle(x, y, x + w, y + h))
    return checkboxes
