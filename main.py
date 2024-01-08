import os
import sys
import ttkbootstrap as ttk

from UI.UIComponents import create_ui


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    logo_path = resource_path('Icon/logo.png')
    root = ttk.Window(title='CAPWizard for IAEA MESSAGE', themename='sandstone')
    root.iconphoto(True, ttk.PhotoImage(file=logo_path))
    create_ui(root)
