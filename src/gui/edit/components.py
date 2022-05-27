import tkinter as tk
from src.common import config
from src.routine.components import Point
from src.gui.interfaces import Frame


class Components(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.label = tk.Label(self, text='Components')
        self.label.pack(fill='x', padx=5)

        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill='y', pady=(0, 5))

        self.listbox = tk.Listbox(self, width=25,
                                  listvariable=config.gui.routine_var,
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
        self.listbox.bind('<<ListboxSelect>>', self.on_select(create_ui=True))

    def unbind_select(self):
        self.listbox.bind('<<ListboxSelect>>', self.on_select(create_ui=False))

    def on_select(self, create_ui=True):
        """
        Returns an on-select callback for the Components Listbox. If CREATE_UI
        is set to True, the callback will overwrite the existing Editor UI.
        """

        def callback(e):
            routine = self.parent.parent
            edit = self.parent.parent.parent

            routine.commands.clear_selection()
            selections = e.widget.curselection()
            if len(selections) > 0:
                index = int(selections[0])
                obj = config.routine[index]

                if isinstance(obj, Point):
                    routine.commands_var.set([c.id for c in obj.commands])
                    edit.minimap.draw_point(obj.location)
                else:
                    routine.commands_var.set([])
                    edit.minimap.draw_default()
                edit.record.clear_selection()

                if create_ui:
                    edit.editor.create_edit_ui(config.routine, index, self.update_obj)
        return callback

    def update_obj(self, arr, i, stringvars):
        def f():
            new_kwargs = {k: v.get() for k, v in stringvars.items()}
            config.routine.update_component(i, new_kwargs)

            edit = self.parent.parent.parent
            edit.minimap.redraw()
            edit.editor.create_edit_ui(arr, i, self.update_obj)
        return f

    def select(self, i):
        self.listbox.selection_clear(0, 'end')
        self.listbox.selection_set(i)
        self.listbox.see(i)

    def clear_selection(self):
        self.listbox.selection_clear(0, 'end')
