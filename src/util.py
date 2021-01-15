from tkinter import Tk
import math

def get_display_size():
    root = Tk()
    return root.winfo_screenwidth(), root.winfo_screenheight()


def distance(a, b):
    """Custon integer-based distance function"""
    return math.ceil(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5)


def get_all_cd(min_cd, a, b):
    """Get all common denominators of a and b"""
    cd = []
    for i in range(min_cd, min(a, b)):
        if a % i == 0 and b % i == 0:
            cd.append(i)

    return cd