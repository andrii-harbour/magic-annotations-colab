import re

import cv2
from PIL import Image, ImageDraw


def get_field_name_from_the_sides(box_related_words: dict):
    supported_field_names = {
        'date', 'name', 'address', 'city', 'state', 'country', 'zip',
        'phone', 'email', 'signature', 'initials', 'ssn', 'title', 'company'
    }
    has_text_left = len(box_related_words['left']) > 0
    has_text_right = len(box_related_words['right']) > 0
    has_text_top = len(box_related_words['top']) > 0
    has_text_bottom = len(box_related_words['bottom']) > 0
    total_words = (
        len(box_related_words['left'])
        + len(box_related_words['right'])
        + len(box_related_words['top'])
        + len(box_related_words['bottom'])
    )
    field_names = []
    if total_words == 0 or total_words > 5:
        return None
    elif not has_text_left and not has_text_right:
        if has_text_top:
            field_names = list(set(box_related_words['top']) & supported_field_names)
        if has_text_bottom and len(field_names) == 0:
            field_names = list(set(box_related_words['bottom']) & supported_field_names)
    else:
        if has_text_left:
            field_names = list(set(box_related_words['left']) & supported_field_names)
        if has_text_right and len(field_names) == 0:
            field_names = list(set(box_related_words['right']) & supported_field_names)

    if len(field_names) > 0:
        return field_names[0]
    return None


def is_valid_text(text):
    # Check if the text contains only certain characters and has a minimum length of 4
    # Allowed characters are alphabets, space, hyphen, apostrophe, double quotation mark, and parentheses
    return bool(re.match(r"^[a-zA-Z '\(\)\"“”:-]{4,}$", text))


def clean_word(word):
    # Remove non-alphabetic characters from the word
    return re.sub(r"[^a-zA-Z]", "", word).lower()


def word_near_box_side(word_coords, extended_coords):
    # Check if the word is in any of the extended areas
    for side, coords in extended_coords.items():
        if (
            coords[0] <= word_coords[0] <= coords[2]
            and coords[1] <= word_coords[1] <= coords[3]
        ):
            return side  # The word is in this extended area

    return None  # The word is not in any of the extended areas


def get_box_related_words(ocr_data, extended_box_coords) -> dict:
    box_related_words = {
        "top": [],
        "bottom": [],
        "left": [],
        "right": [],
    }
    for i in range(len(ocr_data['text'])):
        word = ocr_data['text'][i]
        if not is_valid_text(word):
            continue
        word_coords = (ocr_data['left'][i], ocr_data['top'][i])
        position = word_near_box_side(word_coords, extended_box_coords)
        if position:
            box_related_words[position].append(clean_word(ocr_data['text'][i]))

    return box_related_words


def get_field_name(field, page_text, debug_image):
    # return 'test'
    w, h = field.x2-field.x1, field.y2-field.y1
    # draw_image = Image.fromarray(debug_image)
    # draw = ImageDraw.Draw(draw_image)
    # draw.rectangle((x, y, x+w, y+h), outline='red', width=10)
    extended_areas = {
        "left": (field.x1 - w, field.y1, field.x1, field.y2),
        "right": (field.x2, field.y1, field.x2 + w, field.y2),
        "top": (field.x1, field.y1 - h, field.x2, field.y1),
        "bottom": (field.x1, field.y2, field.x2, field.y2 + h),
    }
    box_related_words = get_box_related_words(page_text, extended_areas)
    cleaned_field_name = get_field_name_from_the_sides(box_related_words)
    # _debug_draw_boxes((field.x1, field.y1, field.x2, field.y2), extended_areas, debug_image)
    # draw_image.show()
    return cleaned_field_name


def _debug_draw_boxes(box_coords, extended_box_coords, image):
    image = Image.fromarray(image)
    draw = ImageDraw.Draw(image)
    draw.rectangle(box_coords, outline='red', width=10)
    for coords in extended_box_coords.values():
        draw.rectangle(coords, outline='blue', width=10)
    # draw.rectangle(extended_box_coords, outline='blue', width=10)
    image.show()
    return


def preprocess_image(page_image):
    gray = cv2.cvtColor(page_image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1]

    result = cv2.GaussianBlur(thresh, (5, 5), 0)
    result = 255 - result

    # im = Image.fromarray(result)
    # im.show()

    # cv2.imshow('thresh', thresh)
    # # cv2.imshow('result', result)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return result


