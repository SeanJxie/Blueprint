from tkinter import Tk

def get_display_size():
    root = Tk()
    return root.winfo_screenwidth(), root.winfo_screenheight()


