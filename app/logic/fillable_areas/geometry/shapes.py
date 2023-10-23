"""Shape primitives."""


class Rectangle:
    """Rectangle representation."""

    def __init__(self, x1, y1, x2, y2):
        """Rectangle class initialization.

        Args:
            x1 (int): First point x coordinate.
            y1 (int): First point y coordinate.
            x2 (int): Second point x coordinate.
            y2 (int): Second point y coordinate.
        """
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)

    def __hash__(self):
        """Hash method implementation."""
        return hash((self.x1, self.y1, self.x2, self.y2))

    @property
    def coordinates(self):
        """Rectangle coordinates.

        Returns:
            tuple: Rectangle coordinates.
        """
        return self.x1, self.y1, self.x2, self.y2


# Line has the same implementation as Rectangle
Line = Rectangle
