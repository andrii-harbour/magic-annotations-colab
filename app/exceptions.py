"""Root Exceptions"""
from werkzeug.exceptions import BadRequest


class FileNotFound(BadRequest):
    """When file not found in request"""
    def __init__(self):
        super().__init__("File not found")
