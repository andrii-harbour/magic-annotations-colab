"""Main api"""
from io import BytesIO
import json

from flask import current_app, Response, request
from PyPDF2 import PdfReader

from app.debug import create_pdf_with_detections
from app.helpers import extract_binary
from app.logic import extract_elements_cv, extract_elements_pypdf2
from app.logic.pdf_utils import extract_form


def detect():
    """Detect fillable fields in pdf document
    method: POST

    FormData: [{
        'file': <input_file.pdf>
    }]

    Returns:
        flask.Response
            Content-Type: application/json
            {
                'success': bool
                'result': [{
                    'name': str
                    'value': str|dict
                    'x1': float
                    'y1': float
                    'x2': float
                    'y2': float
                    'obj_type': str
                }]
            }
    """
    current_app.logger.info('--- Detecting started ---')

    binary_file = extract_binary(request)
    bytes_file = BytesIO(binary_file)

    pdf_file = PdfReader(bytes_file)

    current_app.logger.info('--- Binary extracting finished ---')
    cv_coordinates = False

    if '/AcroForm' in pdf_file.trailer['/Root']:
        current_app.logger.info('--- Type "pdf-forms" ---')
        doc_pages = extract_form(bytes_file)
        current_app.logger.info('--- PDF forms searching finished ---')
    else:
        current_app.logger.info('--- Type "cv" ---')
        doc_pages = extract_elements_cv(bytes_file)
        cv_coordinates = True
        current_app.logger.info('--- CV searching finished ---')

    current_app.logger.info('--- Detecting finished ---')

    create_pdf_with_detections(doc_pages, bytes_file)

    result_list = [page.fillable_elements_to_dict() for page in doc_pages]  # short version of above for loop

    return Response(
            response=json.dumps({
                'success': True,
                'processing_method': 'cv' if cv_coordinates else 'pdf-form',
                'result': result_list,
            }),
            status=200,
            mimetype='application/json',
        )
