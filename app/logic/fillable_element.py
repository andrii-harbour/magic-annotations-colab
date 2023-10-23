"""FillableElement module"""


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
    def __init__(self, x1, y1, x2, y2, obj_type, name, value, page_number):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.obj_type = obj_type
        self.name = name
        self.value = value
        self.page_number = page_number