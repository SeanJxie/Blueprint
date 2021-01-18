from tkinter import Tk
import math

def get_display_size():
    root = Tk()
    return root.winfo_screenwidth(), root.winfo_screenheight()


def distance(a, b):
    """Custon integer-based distance function"""
    return math.ceil(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5)

#1002.3971
def get_zoom_cycle(a, b):
    """Get all common denominators of a and b"""
    zc = []
    d = 1

    while a % d == 0:
        if a // d <= math.gcd(a, b):
            zc.append(a // d)
        d *= 2

    return zc