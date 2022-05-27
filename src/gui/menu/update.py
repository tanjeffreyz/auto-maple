import tkinter as tk
from src.gui.interfaces import MenuBarItem


class Update(MenuBarItem):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Update', **kwargs)

        self.add_command(label='Resources', command=self._resources)

    def _resources(self):
        prompt = ResourcesPrompt(self)


class ResourcesPrompt(tk.Toplevel):
    RESOLUTION = '400x300'

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.grab_set()
        self.wm_title('Update Resources')
        self.geometry(ResourcesPrompt.RESOLUTION)
        self.resizable(False, False)
        self.label = tk.Label(self, text='asdf')
        self.label.pack()

    def _close(self):
        self.destroy()
        self.update()
