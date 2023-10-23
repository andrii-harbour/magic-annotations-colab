"""Root helpers functions"""
from werkzeug.exceptions import BadRequest

from app.exceptions import FileNotFound


def allowed_file(filename):
    """Validate filename and filetype
    Args:
       filename (str): Input filename
    Returns:
        str
    """
    return filename.lower().endswith('.pdf')


def extract_binary(request):
    """Get binary file from request
    Args:
       request (flask.Request): Input filename
    Returns:
        bytes
    Raises:
        werkzeug.exceptions.BadRequest: when can't get file
    """

    # check if the post request has the file part
    if 'file' not in request.files:
        raise FileNotFound
    file_storage = request.files['file']

    # if user does not select file, browser also
    # submit an empty part without filename
    if not file_storage.filename:
        raise FileNotFound
    if file_storage and allowed_file(file_storage.filename):
        return file_storage.stream.read()

    raise BadRequest('Bad file format')
