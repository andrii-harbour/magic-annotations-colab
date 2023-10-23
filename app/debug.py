import os
import numpy
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw, ImageFont

from app.logic.constants import PDF_DOCUMENT_SIZE, RECTANGLES_OUTLINE_COLOR_1, RECTANGLES_OUTLINE_WIDTH


def draw_founded_areas(image, fillable_element, cv_coordinates):
    """Draw founded areas on image
    Args:
        image (PIL.Image)
        file_name (str)
        x1 (float)
        y1 (float)
        x2 (float)
        y2 (float)
        color (tuple)
    """
    draw = ImageDraw.Draw(image)
    # if cv_coordinates or True:
    draw.rectangle(
        (fillable_element['x1'], fillable_element['y1'], fillable_element['x2'], fillable_element['y2']),
        outline=RECTANGLES_OUTLINE_COLOR_1,
        width=RECTANGLES_OUTLINE_WIDTH
    )
    # Custom font style and font size
    roboto_font = ImageFont.truetype('Roboto-Regular.ttf', size=30)
    draw.text((fillable_element['x1']+10, fillable_element['y1']+5), fillable_element['obj_type'], 'red', font=roboto_font)
    # else:
    #     draw.rectangle(
    #         (fillable_element['x1'], fillable_element['y2'], fillable_element['x2'], fillable_element['y1']),
    #         outline=RECTANGLES_OUTLINE_COLOR_1,
    #         width=RECTANGLES_OUTLINE_WIDTH
    #     )


def create_pdf_with_detections(doc_pages, pdf_binary, cv_coordinates):
    page_bytes = pdf_binary.getvalue()
    page_images = convert_from_bytes(page_bytes, PDF_DOCUMENT_SIZE)
    for doc_page in doc_pages:
        page_image_converted = page_images[doc_page.page_num]
        cv_image = numpy.array(page_image_converted)
        image = Image.fromarray(cv_image)
        for fillable_element in doc_page.fillable_elements_to_dict():
            draw_founded_areas(image, fillable_element, cv_coordinates)

        image.save(f'output/debug{doc_page.page_num}.png')
