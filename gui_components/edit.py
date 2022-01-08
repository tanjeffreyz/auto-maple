"""Allows the user to edit routines while viewing each Point's location on the minimap."""

import config
import tkinter as tk
from gui_components.interfaces import Page, Frame, LabelFrame
from routine import Component, Point


class Edit(Page):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Edit', **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(4, weight=1)

        self.minimap = Minimap(self)
        self.minimap.grid(row=0, column=3, sticky=tk.NSEW, padx=10, pady=10)

        self.status = Status(self)
        self.status.grid(row=1, column=3, sticky=tk.NSEW, padx=10, pady=10)

        self.record = Record(self)
        self.record.grid(row=2, column=3, sticky=tk.NSEW, padx=10, pady=10)

        self.routine = Routine(self)
        self.routine.grid(row=0, column=1, rowspan=3, sticky=tk.NSEW, padx=10, pady=10)

        self.editor = Editor(self)
        self.editor.grid(row=0, column=2, rowspan=3, sticky=tk.NSEW, padx=10, pady=10)


class Editor(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Editor', **kwargs)
        self.vars = {}
        self.contents = None
        self.create_default_state()

    def reset(self):
        """Resets the Editor UI to its default state."""

        self.contents.destroy()
        self.create_default_state()

    def create_default_state(self):
        self.vars = {}

        self.contents = Frame(self)
        self.contents.grid(row=0, column=0, padx=5)

        title = tk.Entry(self.contents, justify=tk.CENTER)
        title.pack(expand=True, fill='x', pady=(5, 2))
        title.insert(0, 'Nothing selected')
        title.config(state=tk.DISABLED)

        self.create_entry('', '')

    def create_entry(self, key, value):
        """
        Creates an input row for a single Component attribute. KEY is the name
        of the attribute while VALUE is its currently assigned value.
        """

        self.vars[key] = tk.StringVar(value=str(value))

        row = Frame(self.contents, highlightthickness=0)
        row.pack(expand=True, fill='x')

        label = tk.Entry(row)
        label.pack(side=tk.LEFT, expand=True)
        label.insert(0, key)
        label.config(state=tk.DISABLED)

        entry = tk.Entry(row, textvariable=self.vars[key])
        entry.pack(side=tk.RIGHT, expand=True)

    def create_edit(self, arr, i, func):
        """
        Callback that Creates a UI to edit existing routine Components.
        :param arr:     List of Components to choose from.
        :param i:       The index to choose.
        :param func:    Creates a function that can be bound to the button.
        :return:        None
        """

        self.contents.destroy()
        self.vars = {}
        self.contents = Frame(self)
        self.contents.grid(row=0, column=0, padx=5)

        title = tk.Entry(self.contents, justify=tk.CENTER)
        title.pack(expand=True, fill='x', pady=(5, 2))
        title.insert(0, f"Edit {arr[i].__class__.__name__}")
        title.config(state=tk.DISABLED)

        for key, value in arr[i].kwargs.items():
            self.create_entry(key, value)

        button = tk.Button(self.contents, text='Save', command=func(arr, i, self.vars))
        button.pack(pady=5)


class Routine(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Routine', **kwargs)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.list_frame = Frame(self)
        self.list_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.list_frame.rowconfigure(0, weight=1)

        self.components = Components(self.list_frame)
        self.components.grid(row=0, column=0, sticky=tk.NSEW)

        self.commands_var = tk.StringVar()

        self.commands = Commands(self.list_frame)
        self.commands.grid(row=0, column=1, sticky=tk.NSEW)

        self.controls = Controls(self)
        self.controls.grid(row=1, column=0)


class Controls(Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.label = tk.Label(self, text='asdfasdfasdfasdf', relief=tk.SOLID)
        self.label.pack()


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
                                  yscrollcommand=self.scroll.set)
        # self.listbox.bind('<Up>', lambda e: 'break')
        # self.listbox.bind('<Down>', lambda e: 'break')
        self.listbox.bind('<Left>', lambda e: 'break')
        self.listbox.bind('<Right>', lambda e: 'break')
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.listbox.pack(side=tk.LEFT, expand=True, fill='both', padx=(5, 0), pady=(0, 5))

        self.scroll.config(command=self.listbox.yview)

    def on_select(self, e):         # TODO: edit gui
        self.parent.parent.commands.clear_selection()
        selections = e.widget.curselection()

        if len(selections) > 0:
            index = int(selections[0])
            obj = config.routine[index]

            if isinstance(obj, Point):
                self.parent.parent.commands_var.set([c.id for c in obj.commands])
            else:
                self.parent.parent.commands_var.set([])

            if isinstance(obj, Component):
                self.parent.parent.parent.editor.create_edit(config.routine, index, self.update_obj)
            else:
                self.parent.parent.parent.editor.reset()
        else:
            self.parent.parent.commands_var.set([])
            self.parent.parent.parent.editor.reset()

    def update_obj(self, arr, i, stringvars):
        def f():
            new_kwargs = {k: v.get() for k, v in stringvars.items()}
            config.routine.update_component(i, new_kwargs)
            self.parent.parent.parent.editor.create_edit(arr, i, self.update_obj)
        return f


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
                                  yscrollcommand=self.scroll.set)
        # self.listbox.bind('<Up>', lambda e: 'break')
        # self.listbox.bind('<Down>', lambda e: 'break')
        self.listbox.bind('<Left>', lambda e: 'break')
        self.listbox.bind('<Right>', lambda e: 'break')
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.listbox.pack(side=tk.LEFT, expand=True, fill='both', padx=(5, 0), pady=(0, 5))

        self.scroll.config(command=self.listbox.yview)

    def on_select(self, e):
        selections = e.widget.curselection()
        pt_selects = self.parent.parent.components.listbox.curselection()
        if len(selections) > 0 and len(pt_selects) > 0:
            c_index = int(selections[0])
            pt_index = int(pt_selects[0])
            self.parent.parent.parent.editor.create_edit(config.routine[pt_index].commands,
                                                         c_index, self.update_obj)
        else:
            self.parent.parent.parent.editor.reset()

    def update_obj(self, arr, i, stringvars):
        def f():
            new_kwargs = {k: v.get() for k, v in stringvars.items()}
            print('Heckya')         # TODO: Finish dis
            # config.routine.update_component(i, new_kwargs)
            self.parent.parent.parent.editor.create_edit(arr, i, self.update_obj)
        return f

    def clear_selection(self):
        self.listbox.selection_clear(0, 'end')

    def clear_contents(self):
        self.parent.parent.commands_var.set([])


class Minimap(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Minimap', **kwargs)

        self.canvas = tk.Canvas(self, bg='black',
                                width=400, height=300,
                                borderwidth=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill='both', padx=5, pady=5)


class Status(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Status', **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.cb_label = tk.Label(self, text='Command Book:')
        self.cb_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
        self.cb_entry = tk.Entry(self, textvariable=config.gui.view.status.curr_cb, state=tk.DISABLED)
        self.cb_entry.grid(row=0, column=2, padx=(0, 5), pady=5, sticky=tk.EW)


class Record(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Recorded Points', **kwargs)

        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill='y', pady=(0, 5))

        self.listbox = tk.Listbox(self, width=25,
                                  # listvariable=config.gui.routine_var,
                                  exportselection=False,
                                  yscrollcommand=self.scroll.set)
        self.listbox.bind('<Up>', lambda e: 'break')
        self.listbox.bind('<Down>', lambda e: 'break')
        self.listbox.bind('<Left>', lambda e: 'break')
        self.listbox.bind('<Right>', lambda e: 'break')
        self.listbox.pack(side=tk.LEFT, expand=True, fill='both', padx=(5, 0), pady=(0, 5))

        self.scroll.config(command=self.listbox.yview)
