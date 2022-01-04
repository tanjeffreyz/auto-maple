"""Interfaces that are used by various GUI pages."""

from tkinter import ttk


class Frame(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent


class Tab(Frame):
    def __init__(self, parent, name, **kwargs):
        super().__init__(parent, **kwargs)
        parent.add(self, text=name)
