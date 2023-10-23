import cv2

from PIL import Image, ImageDraw


def find_related_text(x, y, w, h, ocr_data):
    # Calculate the center of the underline for distance comparisons
    underline_center_y = y + h / 2
    allowed_distance = 50

    # Placeholder boundaries
    placeholder_left = x

    left_text = ""

    # Variables to keep track of the closest text on left and right
    left_dist = float('inf')

    # Iterate over each text item from the OCR data
    for text, left, top, width, height in zip(
            ocr_data['text'],
            ocr_data['left'],
            ocr_data['top'],
            ocr_data['width'],
            ocr_data['height']
    ):

        # Check if the text's vertical boundary overlaps with the placeholder's vertical boundary
        if text and abs(top+height/2-underline_center_y) <= allowed_distance:

            # Check left side
            if left + width < placeholder_left:
                dist = placeholder_left - (left + width)
                if dist < left_dist:
                    left_dist = dist
                    left_text = text
        # draw.rectangle((left, top, left+width, top+height), outline='yellow', width=10)

    return left_text


def preprocess_image(page_image):
    gray = cv2.cvtColor(page_image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1]

    result = cv2.GaussianBlur(thresh, (5, 5), 0)
    result = 255 - result

    # cv2.imshow('thresh', thresh)
    # cv2.imshow('result', result)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    return result


def clean_field_name(field_name):
    cleaned_field_name = field_name.replace(':', '')
    supported_field_names = [
        'date', 'name', 'address', 'city', 'state', 'country', 'zip',
        'phone', 'email', 'signature', 'initials', 'ssn', 'title', 'company'
    ]
    if cleaned_field_name.lower() in supported_field_names:
        return cleaned_field_name.lower()
    return None


def get_field_name(field, page_text, debug_image):
    x, y, w, h = field.x1, field.y1, field.x2-field.x1, field.y2-field.y1
    # draw_image = Image.fromarray(debug_image)
    # draw = ImageDraw.Draw(draw_image)
    # draw.rectangle((x, y, x+w, y+h), outline='red', width=10)
    field_name = find_related_text(x, y, w, h, page_text)
    cleaned_field_name = clean_field_name(field_name)
    # draw_image.show()
    return cleaned_field_name

