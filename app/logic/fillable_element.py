"""FillableElement module"""
from pdfminer.pdftypes import resolve1

from app.logic.constants import CONVERT_COORD_COEF_PYPDF2
from app.logic.exceptions import FillElementParseError
from pdfminer.psparser import PSLiteral, PSKeyword
from pdfminer.utils import decode_text


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
            Allowed types is 'TEXT', 'SIGNATURE', 'CHECKBOX'

        x1 (float): coordinate
        x2 (float): coordinate
        y1 (float): coordinate
        y2 (float): coordinate
    """

    _TYPES_MAP = {
        'Tx': 'TEXT',
        'Sig': 'SIGNATURE'
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
    def create_from_field_obj(cls, field_obj, media_box, page_number):
        """
        Create instance with empty fields, then extract from field_obj
        Attributes:
            field_obj (PyPDF2.generic.DictionaryObject): PyPDF2 Field object
            media_box (PyPDF2.generic.RectangleObject): Contain pdf
                document page size
        """
        instance = cls(*[None]*7, page_number=page_number)
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

        if not self.obj_type:
            print(f'the obj_type is undefined. Take a look. General object is {field_obj}')

    @staticmethod
    def _decode_value(value):
        # decode PSLiteral, PSKeyword
        if isinstance(value, (PSLiteral, PSKeyword)):
            value = value.name

        # decode bytes
        if isinstance(value, bytes):
            value = decode_text(value)

        return value

    def _extract_coordinates(self, field_obj, media_box):
        """Set x1, x2, y1, y2 from DictionaryObject's rectangle
        y1 and y2 is inverted because PIL and pdfminer have different coordinate systems
        Args:
            field_obj (PyPDF2.generic.DictionaryObject): PyPDF2 Field object
            media_box (PyPDF2.generic.RectangleObject): Contain pdf
                document page size
        """
        if not field_obj.get('Rect'):
            raise FillElementParseError

        if not isinstance(field_obj.get('Rect'), (list, tuple)):
            raise FillElementParseError

        rect = field_obj.get('Rect')

        self.x1 = float(rect[0] - media_box[0])*CONVERT_COORD_COEF_PYPDF2
        self.y1 = float(media_box[3] - rect[3])*CONVERT_COORD_COEF_PYPDF2
        self.x2 = float(rect[2] - media_box[0])*CONVERT_COORD_COEF_PYPDF2
        self.y2 = float(media_box[3] - rect[1])*CONVERT_COORD_COEF_PYPDF2

    def _extract_name(self, field_obj):
        """Extract and set 'name' property
        Args:
            field_obj (PyPDF2.generic.DictionaryObject)
        """
        name = None
        if field_obj.get('TU'):
            name = decode_text(field_obj.get('TU'))  # form has name
        self.name = name

    def _extract_value(self, field_obj):
        """Extract and set 'value' property
        Args:
            field_obj (PyPDF2.generic.DictionaryObject)
        """
        # resolve indirect obj
        values = resolve1(field_obj.get('V'))

        # decode value(s)
        if isinstance(values, list):
            values = [self._decode_value(v) for v in values]
        else:
            values = self._decode_value(values)

        self.value = values

    def _extract_obj_type(self, field_obj):
        """Extract and set 'obj_type' property from _TYPES_MAP dict
        Args:
            field_obj (PyPDF2.generic.DictionaryObject)
        """
        field_type = field_obj.get('FT').name if field_obj.get('FT') else None
        if field_type in self._TYPES_MAP:
            self.obj_type = self._TYPES_MAP[field_type]
        else:
            self.obj_type = None

    def _extract_checkbox(self, field_obj):
        """Check and set 'obj_type' property to 'CHECKBOX'
        v - value
        mk - appearance characteristics
        Args:
            field_obj (PyPDF2.generic.DictionaryObject)
        """
        if field_obj.get('FT').name == 'Btn' and (
                field_obj.get('V') or len(field_obj.get('MK')) <= 1
        ):
            self.obj_type = 'CHECKBOX'
