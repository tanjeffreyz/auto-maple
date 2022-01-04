"""Allows the user to edit routines while viewing each Point's location on the minimap."""

import tkinter as tk
from gui_components.interfaces import Frame, Tab


class Edit(Tab):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Edit', **kwargs)
