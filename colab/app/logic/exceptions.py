"""Exceptions for working with fillable elements"""


class FillElementParseError(Exception):
    """When some error occurs on creation logic.classes.FillableElement"""
    def __init__(self):
        super().__init__("Error on fillable element parsing")
