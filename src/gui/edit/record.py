import tkinter as tk
from src.routine.components import Point
from src.gui.interfaces import LabelFrame


class Record(LabelFrame):
    MAX_SIZE = 20

    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Recorded Positions', **kwargs)

        self.entries = []
        self.display_var = tk.StringVar()

        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill='y', pady=5)

        self.listbox = tk.Listbox(self, width=25,
                                  listvariable=self.display_var,
                                  exportselection=False,
                                  activestyle='none',
                                  yscrollcommand=self.scroll.set)
        self.listbox.bind('<Up>', lambda e: 'break')
        self.listbox.bind('<Down>', lambda e: 'break')
        self.listbox.bind('<Left>', lambda e: 'break')
        self.listbox.bind('<Right>', lambda e: 'break')
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.listbox.pack(side=tk.LEFT, expand=True, fill='both', padx=(5, 0), pady=5)

        self.scroll.config(command=self.listbox.yview)

    def add_entry(self, time, location):
        """
        Adds a new recorded location to the Listbox. Pops the oldest entry if
        Record.MAX_SIZE has been reached.
        """

        if len(self.entries) > Record.MAX_SIZE:
            self.entries.pop()
        self.entries.insert(0, (time, location))
        self.display_var.set(tuple(f'{x[0]}  -  ({x[1][0]}, {x[1][1]})' for x in self.entries))
        self.listbox.see(0)

    def on_select(self, e):
        selects = e.widget.curselection()
        if len(selects) > 0:
            index = int(selects[0])
            pos = self.entries[index][1]
            self.parent.minimap.draw_point(tuple(float(x) for x in pos))

            routine = self.parent.routine
            routine.components.clear_selection()
            routine.commands.clear_selection()
            routine.commands.clear_contents()

            kwargs = {'x': pos[0], 'y': pos[1]}
            self.parent.editor.create_add_ui(Point, kwargs=kwargs)

    def clear_selection(self):
        self.listbox.selection_clear(0, 'end')
