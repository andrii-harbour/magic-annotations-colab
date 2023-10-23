"""App's entrypoint"""
import os
from app.init import app
from app.api import detect


@app.route('/api/v1/detect', methods=['POST'])
def some_detection():
    return detect()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 4999)))
