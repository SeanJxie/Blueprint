from tkinter import Tk
import math
import os

def get_display_size():
    root = Tk()
    return root.winfo_screenwidth(), root.winfo_screenheight()


def distance(a, b):
    """Custon integer-based distance function"""
    return ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5


def get_zoom_cycle(a, b):
    """Generate the valid values of cell size"""
    zc = []
    d = 1

    while a % d == 0:
        if a // d <= math.gcd(a, b):
            zc.append(a // d)
        d *= 2

    return zc


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # May not exist
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



#def scale_coord(c, s):
#    return [c[i] * s[i] for i in range(2)]