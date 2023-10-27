"""PDF fillable elements classes"""
import os
if os.getenv('COLAB'):
    from colab.flask import current_app as app
else:
    from flask import current_app as app

from app.logic.fillable_element import FillableElement


class DocumentPage:
    """List wrapper for FillableElement
    Attributes:
        page_num (int): Number of current page in pdf document
        _list (list): For storing FillableElement
        _media_box (PyPDF2.generic.RectangleObject): Needed for
            creating FillableElement instance
    """
    def __init__(self, page_num, media_box):
        """
        Attributes:
            page_num (int): Number of current page in pdf document
            media_box (PyPDF2.generic.RectangleObject): Needed for
                creating FillableElement instance
        """
        self.page_num = page_num
        self._list = []
        self._media_box = media_box

    @property
    def fillable_elements(self):
        """Get list of FillableElement
        Returns:
            list<FillableElement>
        """
        return self._list

    def _from_pdfminer(self, widget):
        try:
            fillable_element = FillableElement.create_from_field_obj(
                widget,
                self._media_box,
                self.page_num
            )
            if fillable_element.obj_type and fillable_element.obj_type.lower() in [
                'text', 'signature', 'checkbox'
            ]:
                self._list.append(fillable_element)
        except:
            app.logger.exception('FillElementParseError')

    def _from_cv(self, **field_args):
        """Create and add FillableElement in to _list.
        Create from FillableElement's arguments
        Args:
            field_args (dict) {
                x1 (float)
                y1 (float)
                x2 (float)
                y2 (float)
                obj_type (str)
                name (str)
                value (str)
            }
        """
        fillable_element = FillableElement(**field_args, page_number=self.page_num)
        self._list.append(fillable_element)

    def add_element(self, widget=None, **field_args):
        """Create and add FillableElement in to _list
        Args:
            field (PyPDF2.generic.IndirectObject)
            field_args (dict) {
                x1 (float)
                y1 (float)
                x2 (float)
                y2 (float)
                obj_type (str)
                name (str)
                value (str)
            }
        """
        if widget:
            # self._from_fitz(widget)
            self._from_pdfminer(widget)
        else:
            self._from_cv(**field_args)

    def fillable_elements_to_dict(self):
        """Convert each FillableElement to dict and add to list
        Returns:
            list<dict>
            [{
                'name': str
                'value': str|dict
                'x1': float
                'y1': float
                'x2': float
                'y2': float
                'obj_type': str
                'page_number': int
            }]
        """
        return [el.__dict__ for el in self._list]
