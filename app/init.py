"""Init Flask app"""
import logging
from logging.handlers import SysLogHandler
import json
import os
from flask import Flask, Response
from werkzeug.exceptions import HTTPException


def create_app():
    """Create Flask app"""
    app = Flask(__name__)

    handler = SysLogHandler()
    log_level = os.environ.get('LOGGING_LEVEL', 'INFO')
    handler.setLevel(getattr(logging, log_level))
    app.logger.addHandler(handler)

    @app.errorhandler(Exception)
    def error_handler(exc):
        error_message = str(exc)
        status_code = 500
        app.logger.error(error_message)
        if isinstance(exc, HTTPException):
            status_code = exc.code
        return Response(
            response=json.dumps({
                'success': False,
                'message': error_message,
            }),
            status=status_code,
            mimetype='application/json',
        )

    return app


app = create_app()
