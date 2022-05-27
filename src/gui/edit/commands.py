import tkinter as tk

from src.common import config
from src.routine.components import Point
from src.gui.interfaces import Frame


class Commands(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.label = tk.Label(self, text='Commands')
        self.label.pack(fill='x', padx=5)

        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill='y', pady=(0, 5))

        self.listbox = tk.Listbox(self, width=25,
                                  listvariable=parent.parent.commands_var,
                                  exportselection=False,
                                  activestyle='none',
                                  yscrollcommand=self.scroll.set)
        self.listbox.bind('<Up>', lambda e: 'break')
        self.listbox.bind('<Down>', lambda e: 'break')
        self.listbox.bind('<Left>', lambda e: 'break')
        self.listbox.bind('<Right>', lambda e: 'break')
        self.bind_select()
        self.listbox.pack(side=tk.LEFT, expand=True, fill='both', padx=(5, 0), pady=(0, 5))

        self.scroll.config(command=self.listbox.yview)

    def bind_select(self):
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

    def unbind_select(self):
        self.listbox.bind('<<ListboxSelect>>', lambda e: 'break')

    def on_select(self, e):
        routine = self.parent.parent

        selections = e.widget.curselection()
        pt_selects = routine.components.listbox.curselection()
        if len(selections) > 0 and len(pt_selects) > 0:
            c_index = int(selections[0])
            pt_index = int(pt_selects[0])
            routine.parent.editor.create_edit_ui(config.routine[pt_index].commands,
                                                 c_index, self.update_obj)
        else:
            routine.parent.editor.reset()

    def update_obj(self, arr, i, stringvars):
        def f():
            pt_selects = self.parent.parent.components.listbox.curselection()
            if len(pt_selects) > 0:
                index = int(pt_selects[0])
                new_kwargs = {k: v.get() for k, v in stringvars.items()}
                config.routine.update_command(index, i, new_kwargs)
            self.parent.parent.parent.editor.create_edit_ui(arr, i, self.update_obj)
        return f

    def update_display(self):
        parent = self.parent.parent
        pt_selects = parent.components.listbox.curselection()
        if len(pt_selects) > 0:
            index = int(pt_selects[0])
            obj = config.routine[index]
            if isinstance(obj, Point):
                parent.commands_var.set([c.id for c in obj.commands])
            else:
                parent.commands_var.set([])
        else:
            parent.commands_var.set([])

    def clear_selection(self):
        self.listbox.selection_clear(0, 'end')

    def clear_contents(self):
        self.parent.parent.commands_var.set([])

    def select(self, i):
        self.listbox.selection_clear(0, 'end')
        self.listbox.selection_set(i)
        self.listbox.see(i)
