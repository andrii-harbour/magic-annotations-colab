"""FillableElement module"""
import datetime

from PyPDF2.generic import IndirectObject

from app.logic.constants import CONVERT_COORD_COEF_PYPDF2
from app.logic.exceptions import FillElementParseError


class FillableElement:
    """
    Element contained in DocumentPage
    Attributes:
        name (str|None): Name of pdf element field
        value (str|dict|None): Value of pdf element field
            With value == 'SIGNATURE' structure is:
            {
                'autor_name': (str)
                'sign_date': (datetime.datetime)
            }

        obj_type (str): custom defined object type
            Allowed types is 'TEXT', 'SIGNATURE', 'SELECT',
            'CHECKBOX', 'RADIOBUTTON'

        x1 (float): coordinate
        x2 (float): coordinate
        y1 (float): coordinate
        y2 (float): coordinate
    """

    _TYPES_MAP = {
        '/Tx': 'TEXT',
        '/Sig': 'SIGNATURE',
        '/Ch': 'SELECT',
    }

    def __init__(self, x1, y1, x2, y2, obj_type, name, value, page_number):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.obj_type = obj_type
        self.name = name
        self.value = value
        self.page_number = page_number

    @classmethod
    def create_from_field_obj(cls, field_obj, media_box):
        """
        Create instance with empty fields, then extract from field_obj
        Attributes:
            field_obj (PyPDF2.generic.DictionaryObject): PyPDF2 Field object
            media_box (PyPDF2.generic.RectangleObject): Contain pdf
                document page size
        """
        instance = cls(*[None]*7)
        instance.extract_from_field_obj(field_obj, media_box)

        return instance

    def extract_from_field_obj(self, field_obj, media_box):
        """
        Attributes:
            field_obj (PyPDF2.generic.DictionaryObject): PyPDF2 Field object
            media_box (PyPDF2.generic.RectangleObject): Contain pdf
                document page size
        """
        self._extract_name(field_obj)
        self._extract_value(field_obj)
        self._extract_coordinates(field_obj, media_box)
        self._extract_obj_type(field_obj)
        self._extract_checkbox(field_obj)
        self._extract_signature_value()
        self._check_value()

        if not self.obj_type:
            raise FillElementParseError

    def _check_value(self):
        if self.value and not isinstance(self.value, (str, dict)):
            self.value = None

    def _extract_signature_value(self):
        """Set self.value when self.obj_type == 'SIGNATURE'
        Args:
            field_obj (PyPDF2.generic.DictionaryObject):
                PyPDF2 Field object
        """
        if self.obj_type == 'SIGNATURE' and \
                isinstance(self.value, IndirectObject):
            try:
                time_str = self.value.get_object().get('/M').replace('\'', '')
                date_obj = datetime.datetime.strptime(
                    time_str,
                    'D:%Y%m%d%H%M%S%z'
                )
                self.value = {
                    'autor_name': self.value.get_object().get('/Name'),
                    'sign_date': date_obj.strftime('%m/%d/%Y, %H:%M:%S'),
                }
            except (ValueError, AttributeError):
                self.value = None

    def _extract_coordinates(self, field_obj, media_box):
        """Set x1, x2, y1, y2 from DictionaryObject's rectangle
        Args:
            field_obj (PyPDF2.generic.DictionaryObject): PyPDF2 Field object
            media_box (PyPDF2.generic.RectangleObject): Contain pdf
                document page size
        """
        if not field_obj.get('/Rect'):
            raise FillElementParseError

        if isinstance(field_obj.get('/Rect'), IndirectObject):
            rect = field_obj['/Rect'].get_object()
        else:
            rect = field_obj['/Rect']

        self.x1 = float(rect[0] - media_box[0])*CONVERT_COORD_COEF_PYPDF2
        self.y1 = float(media_box[3] - rect[1])*CONVERT_COORD_COEF_PYPDF2
        self.x2 = float(rect[2] - media_box[0])*CONVERT_COORD_COEF_PYPDF2
        self.y2 = float(media_box[3] - rect[3])*CONVERT_COORD_COEF_PYPDF2


    def _extract_name(self, field_obj):
        """Extract and set 'name' property
        Args:
            field_obj (PyPDF2.generic.DictionaryObject)
        """
        self.name = field_obj.get('/T')

    def _extract_value(self, field_obj):
        """Extract and set 'value' property
        Args:
            field_obj (PyPDF2.generic.DictionaryObject)
        """
        self.value = field_obj.get('/V')

    def _extract_checkbox(self, field_obj):
        """Check and set 'obj_type' property to 'CHECKBOX'
        Args:
            field_obj (PyPDF2.generic.DictionaryObject)
        """
        if field_obj.get('/FT') == '/Btn' and not field_obj.get('/A'):
            self.obj_type = 'CHECKBOX'

    def _extract_obj_type(self, field_obj):
        """Extract and set 'obj_type' property from _TYPES_MAP dict
        Args:
            field_obj (PyPDF2.generic.DictionaryObject)
        """
        field_type = field_obj.get('/FT')
        if field_type in self._TYPES_MAP:
            self.obj_type = self._TYPES_MAP[field_type]
        else:
            self.obj_type = None
