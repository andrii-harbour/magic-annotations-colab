"""Geometry util funtions."""


def find_intersection(l1, l2):
    """Find intersection between two lines.

    Args:
        l1 (shapes.Lines): First line.
        l2 (shapes.Lines): Second line.

    Returns:
        tuple: Coordinates of the intersection.

    """
    try:
        x = (
                ((l1.x1 * l1.y2 - l1.y1 * l1.x2) * (l2.x1 - l2.x2) - (
                        l1.x1 - l1.x2) * (l2.x1 * l2.y2 - l2.y1 * l2.x2)) /
                ((l1.x1 - l1.x2) * (l2.y1 - l2.y2) - (l1.y1 - l1.y2) * (
                        l2.x1 - l2.x2))
        )
        y = (
                ((l1.x1 * l1.y2 - l1.y1 * l1.x2) * (l2.y1 - l2.y2) - (
                        l1.y1 - l1.y2) * (l2.x1 * l2.y2 - l2.y1 * l2.x2)) /
                ((l1.x1 - l1.x2) * (l2.y1 - l2.y2) - (l1.y1 - l1.y2) * (
                        l2.x1 - l2.x2))
        )
        return int(x), int(y)
    except ZeroDivisionError:
        # TODO: double check if this error relevant.
        return None



# def custom_intersection(line1, line2):
#     # The intersection point of the example below should be (0,0)
#
#     # Vertices for the first line
#     p1_start = np.asarray([line1.x1, line1.y1])
#     p1_end = np.asarray([line1.x2, line1.y2])
#
#     # Vertices for the second line
#     p2_start = np.asarray([line2.x1, line2.y1])
#     p2_end = np.asarray([line2.x2, line2.y2])
#
#     p = p1_start
#     r = (p1_end - p1_start)
#
#     q = p2_start
#     s = (p2_end - p2_start)
#
#     t = np.cross(q - p, s) / (np.cross(r, s))
#
#     # This is the intersection point
#     i = p + t * r
#     return i