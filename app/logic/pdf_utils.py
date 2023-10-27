"""Functions for working with pdf documents"""
import json
from io import BytesIO

import pytesseract
import os
if os.getenv('COLAB'):
    from colab.flask import current_app as app
else:
    from flask import current_app as app
import cv2
import numpy
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PdfReadError
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from pytesseract import Output
from werkzeug.exceptions import BadRequest

from app.logic.constants import (
    PDF_DOCUMENT_SIZE,
    RECTANGLES_OUTLINE_COLOR_1,
    RECTANGLES_OUTLINE_COLOR_2,
    RECTANGLES_OUTLINE_WIDTH,
)
from app.logic.document_page import DocumentPage
from app.logic.fillable_areas.fillable_areas import find_fillable_areas
from app.logic.text_processing import get_field_name, preprocess_image


def extract_elements_cv(pdf_binary):
    """Find fillable areas with cv2 lib
    Args:
       pdf_binary (io.BytesIO)
    Returns:
        list<logic.classes.DocumentPage>
    """
    pdf_file = PdfReader(pdf_binary)
    app.logger.info('--- CV: pdf created ---')

    if pdf_file.is_encrypted:
        try:
            pdf_file.decrypt('')
        except NotImplementedError as e:
            raise BadRequest('File is encrypted') from e

    pages = []

    for page_num in range(len(pdf_file.pages)):
        # if page_num != 0:
        #     continue
        app.logger.info(f'--- CV: Page{page_num} ---')
        page = pdf_file.pages[page_num]
        doc_page = DocumentPage(page_num, None)

        tmp = BytesIO()
        stream = PdfWriter()
        stream.add_page(page)
        stream.write(tmp)
        page_bytes = tmp.getvalue()

        page_images = convert_from_bytes(page_bytes, PDF_DOCUMENT_SIZE)
        page_image_converted = page_images[0]
        cv_image = numpy.array(page_image_converted)

        # image = Image.fromarray(cv_image)
        # image.show()

        fillable_areas = find_fillable_areas(cv_image)
        app.logger.info(f'--- CV: fillable areas sear complete on page {page_num} ---')

        line_areas = fillable_areas['line_areas']
        checkbox_areas = fillable_areas['checkbox_areas']

        # ToDo: make more accurate check
        if len(line_areas) == 0 and len(checkbox_areas) == 0:
            pages.append(doc_page)
            continue

        processed_image_for_tesseract = preprocess_image(cv_image)
        page_text = pytesseract.image_to_data(
            processed_image_for_tesseract, output_type=Output.DICT, config='--psm 3', lang='eng'
        )
        # debug
        # with open(f'page{page_num}_text.json', 'w') as f:
        #     json.dump(page_text, f, indent=4)


        for i, line in enumerate(line_areas):
            # draw line on image with PIL
            # debug
            # draw = ImageDraw.Draw(image)
            # draw.rectangle((line.x1, line.y1, line.x2, line.y2), outline=RECTANGLES_OUTLINE_COLOR_1, width=RECTANGLES_OUTLINE_WIDTH)
            # image.save(f'page{page_num}_line.png')

            field_name = get_field_name(line, page_text, cv_image)  # todo: cv image is just for debug

            obj_type = 'TEXT'
            if field_name:
                if field_name == 'signature':
                    obj_type = 'SIGNATURE'
                elif field_name == 'date':
                    obj_type = 'DATE'

            doc_page.add_element(
                x1=line.x1,
                y1=line.y1,
                x2=line.x2,
                y2=line.y2,
                obj_type=obj_type,
                name=field_name,
                value=None
            )

        for i, checkbox in enumerate(checkbox_areas):
            doc_page.add_element(
                x1=checkbox.x1,
                y1=checkbox.y1,
                x2=checkbox.x2,
                y2=checkbox.y2,
                obj_type='CHECKBOX',
                name=field_name,
                value=None
            )

        # temporary disabled because of unstable results
        # for region in fillable_areas['empty_region_areas']:
        #     doc_page.add_element(
        #         x1=region.x1,
        #         y1=region.y1,
        #         x2=region.x2,
        #         y2=region.y2,
        #         obj_type='EMPTY_REGIONS',
        #         name=None,
        #         value=None,
        #     )

        pages.append(doc_page)

    return pages


def extract_widgets_pdfminer(pdf_binary):
    parser = PDFParser(pdf_binary)
    doc = PDFDocument(parser)
    pages = []
    try:
        pdf_pages = list(PDFPage.create_pages(doc))
    except KeyError as e:
        app.logger.exception('KeyError:', e)
        return pages

    for page_number, page in enumerate(pdf_pages):
        page_obj = resolve1(page).attrs
        if 'Annots' not in page_obj.keys():
            continue
        media_box = page_obj['MediaBox']
        widgets = resolve1(page_obj['Annots'])
        doc_page = DocumentPage(page_number, media_box)
        for widget in widgets:
            doc_page.add_element(widget=resolve1(widget))
        pages.append(doc_page)

    return pages


# def extract_elements_pypdf2(pdf_binary):
#     """Read pdf binary and return list of fillable elements
#     Args:
#        pdf_binary (io.BytesIO)
#     Returns:
#         list<logic.classes.DocumentPage>
#     Raises:
#         werkzeug.exceptions.BadRequest: when can't read file with PyPDF2
#     """
#     pdf_file = PdfReader(pdf_binary, strict=False)
#
#     if pdf_file.is_encrypted:
#         try:
#             pdf_file.decrypt('')
#         except NotImplementedError as e:
#             raise BadRequest('File is encrypted') from e
#
#     media_box = pdf_file.pages[0].mediabox
#     pages = []
#
#     try:
#         catalog = pdf_file.trailer['/Root']
#         kids = catalog['/Pages']['/Kids']
#     except KeyError as e:
#         app.logger.exception('KeyError:', e)
#         return pages
#
#     # page_bytes = pdf_binary.getvalue()
#     # page_images = convert_from_bytes(page_bytes, PDF_DOCUMENT_SIZE)
#
#     for page_num, page in enumerate(kids):
#         page_obj = page.get_object()
#
#         # page_image_converted = page_images[page_num]
#         # cv_image = numpy.array(page_image_converted)
#         # image = Image.fromarray(cv_image)
#         # image.save(f'test{page_num}.png')
#
#         if '/Annots' not in page_obj:
#             continue
#
#         fields = extract_nested_elements(page_obj['/Annots'])
#
#         doc_page = DocumentPage(page_num, media_box)
#
#         for field_obj in fields:
#             doc_page.add_element(field_obj=field_obj)
#
#         pages.append(doc_page)
#
#     return pages
#
#
# def extract_nested_elements(fields):
#     """Sometimes pdf elements could have deep nested structure
#     This function makes a flat structure instead of a nested
#     Args:
#        fields (list<PyPDF2.generic.IndirectObject>)
#     Returns:
#         list<PyPDF2.generic.IndirectObject>
#     """
#
#     fields_list = []
#
#     try:
#         for field in fields:
#             field_obj = field.get_object()
#             fields_list.append(field_obj)
#
#             if field_obj.get('/Kids'):
#                 fields_list += extract_nested_elements(field_obj['/Kids'])
#     except (TypeError, PdfReadError) as e:
#         app.logger.exception(f'{type(e)}: {e}')
#
#     return fields_list
