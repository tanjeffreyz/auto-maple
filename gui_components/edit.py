"""Allows the user to edit routines while viewing each Point's location on the minimap."""

import config
import inspect
import tkinter as tk
from routine import Component, Point, Command
from gui_components.interfaces import Page, Frame, LabelFrame


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

        self.columnconfigure(0, minsize=300)

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
        self.contents.grid(row=0, column=0, sticky=tk.EW, padx=5)

        title = tk.Entry(self.contents, justify=tk.CENTER)
        title.pack(expand=True, fill='x', pady=(5, 2))
        title.insert(0, 'Nothing selected')
        title.config(state=tk.DISABLED)

        self.create_disabled_entry()

    def create_disabled_entry(self):
        row = Frame(self.contents, highlightthickness=0)
        row.pack(expand=True, fill='x')

        label = tk.Entry(row)
        label.pack(side=tk.LEFT, expand=True, fill='x')
        label.config(state=tk.DISABLED)

        entry = tk.Entry(row)
        entry.pack(side=tk.RIGHT, expand=True, fill='x')
        entry.config(state=tk.DISABLED)

    def create_entry(self, key, value):
        """
        Creates an input row for a single Component attribute. KEY is the name
        of the attribute while VALUE is its currently assigned value.
        """

        self.vars[key] = tk.StringVar(value=str(value))

        row = Frame(self.contents, highlightthickness=0)
        row.pack(expand=True, fill='x')

        label = tk.Entry(row)
        label.pack(side=tk.LEFT, expand=True, fill='x')
        label.insert(0, key)
        label.config(state=tk.DISABLED)

        entry = tk.Entry(row, textvariable=self.vars[key])
        entry.pack(side=tk.RIGHT, expand=True, fill='x')

    def create_edit_ui(self, arr, i, func):
        """
        Creates a UI to edit existing routine Components.
        :param arr:     List of Components to choose from.
        :param i:       The index to choose.
        :param func:    When called, creates a function that can be bound to the button.
        :return:        None
        """

        self.contents.destroy()
        self.vars = {}
        self.contents = Frame(self)
        self.contents.grid(row=0, column=0, sticky=tk.EW, padx=5)

        title = tk.Entry(self.contents, justify=tk.CENTER)
        title.pack(expand=True, fill='x', pady=(5, 2))
        title.insert(0, f"Editing {arr[i].__class__.__name__}")
        title.config(state=tk.DISABLED)

        if len(arr[i].kwargs) > 0:
            for key, value in arr[i].kwargs.items():
                self.create_entry(key, value)
            button = tk.Button(self.contents, text='Save', command=func(arr, i, self.vars))
            button.pack(pady=5)
        else:
            self.create_disabled_entry()

    def create_add_prompt(self):
        """Creates a UI that asks the user to select a class to create."""

        self.contents.destroy()
        self.vars = {}
        self.contents = Frame(self)
        self.contents.grid(row=0, column=0, sticky=tk.EW, padx=5)

        title = tk.Entry(self.contents, justify=tk.CENTER)
        title.pack(expand=True, fill='x', pady=(5, 2))
        title.insert(0, f"Creating new ...")
        title.config(state=tk.DISABLED)

        options = config.routine.get_all_components()
        var = tk.StringVar(value=tuple(options.keys()))

        def update_search(e):
            value = e.widget.get().strip().lower()
            if value == '':
                var.set(tuple(options.keys()))
            else:
                new_options = []
                for key in options:
                    if key.lower().startswith(value):
                        new_options.append(key)
                var.set(new_options)

        def on_return(e):
            value = e.widget.get().strip().lower()
            if value in options:
                self.create_add_ui(options[value])
            else:
                print(f"\n[!] '{value}' is not a valid Component.")

        def on_double_click(e):
            w = e.widget
            selects = w.curselection()
            if len(selects) > 0:
                value = w.get(int(selects[0]))
                if value in options:
                    self.create_add_ui(options[value])

        # Search bar
        user_input = tk.Entry(self.contents)
        user_input.pack(expand=True, fill='x')
        user_input.insert(0, 'Search for a component')
        user_input.bind('<FocusIn>', lambda _: user_input.selection_range(0, 'end'))
        user_input.bind('<Return>', on_return)
        user_input.bind('<KeyPress>', update_search)
        user_input.bind('<KeyRelease>', update_search)

        # Display search results
        results = Frame(self.contents)
        results.pack(expand=True, fill='both', pady=(1, 0))

        scroll = tk.Scrollbar(results)
        scroll.pack(side=tk.RIGHT, fill='both')

        display = tk.Listbox(results, listvariable=var,
                             activestyle='none',
                             yscrollcommand=scroll.set)
        display.bind('<Double-1>', on_double_click)
        display.pack(side=tk.LEFT, expand=True, fill='both')

        scroll.config(command=display.yview)

    def create_add_ui(self, component, kwargs=None):
        """
        Creates a UI that edits the parameters of a new COMPONENT instance, and allows
        the user to add this newly created Component to the current routine.
        """

        # Prevent Components and Commands from overwriting this UI
        routine = self.parent.routine
        routine.components.unbind_select()
        routine.commands.unbind_select()

        self.contents.destroy()
        self.vars = {}
        self.contents = Frame(self)
        self.contents.grid(row=0, column=0, sticky=tk.EW, padx=5)

        title = tk.Entry(self.contents, justify=tk.CENTER)
        title.pack(expand=True, fill='x', pady=(5, 2))
        title.insert(0, f"Creating new {component.__name__}")
        title.config(state=tk.DISABLED)

        sig = inspect.getfullargspec(component.__init__)
        if sig.defaults is None:
            diff = len(sig.args)
        else:
            diff = len(sig.args) - len(sig.defaults)

        # Populate args
        if kwargs is None:
            kwargs = {}
        for i in range(diff):
            if sig.args[i] != 'self':
                kwargs[sig.args[i]] = ''

        # Populate kwargs
        for i in range(diff, len(sig.args)):
            kwargs[sig.args[i]] = sig.defaults[i-diff]

        if len(kwargs) > 0:
            for key, value in kwargs.items():
                self.create_entry(key, value)
        else:
            self.create_disabled_entry()

        controls = Frame(self.contents)
        controls.pack(expand=True, fill='x')

        cancel_button = tk.Button(controls, text='Cancel', command=self.cancel)
        cancel_button.pack(side=tk.LEFT, pady=5)

        add_button = tk.Button(controls, text='Add', command=self.add(component))
        add_button.pack(side=tk.RIGHT, pady=5)

    def cancel(self):
        """Button callback that exits the current Component creation UI."""

        routine = self.parent.routine
        routine.components.bind_select()
        routine.commands.bind_select()
        self.display_current()

    def add(self, component):
        """Returns a Button callback that appends the current Component to the routine."""

        def f():
            new_kwargs = {k: v.get() for k, v in self.vars.items()}
            selects = self.parent.routine.components.listbox.curselection()

            try:
                obj = component(**new_kwargs)
                if isinstance(obj, Command):
                    if len(selects) > 0:
                        index = int(selects[0])
                        if isinstance(config.routine[index], Point):
                            config.routine.append_command(index, obj)
                            self.cancel()
                        else:
                            print(f"\n[!] Error while adding Command: currently selected Component is not a Point.")
                    else:
                        print(f"\n[!] Error while adding Command: nothing is currently selected.")
                else:
                    config.routine.append_component(obj)
                    self.cancel()
            except (ValueError, TypeError) as e:
                print(f"\n[!] Found invalid arguments for '{component.__name__}':")
                print(f"{' ' * 4} -  {e}")
        return f

    def display_current(self):
        """
        Displays an edit UI for the currently selected Command if there is one, otherwise
        displays an edit UI for the current Component. If nothing is selected, displays the
        default UI.
        """

        routine = self.parent.routine
        components = routine.components.listbox.curselection()
        commands = routine.commands.listbox.curselection()
        if len(components) > 0:
            p_index = int(components[0])
            if len(commands) > 0:
                c_index = int(commands[0])
                self.create_edit_ui(config.routine[p_index].commands, c_index,
                                    routine.commands.update_obj)
            else:
                self.create_edit_ui(config.routine, p_index,
                                    routine.components.update_obj)
        else:
            self.contents.destroy()
            self.create_default_state()


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

        self.up_arrow = tk.Button(self, text='▲', width=6, command=self.move_up)
        self.up_arrow.grid(row=0, column=0)

        self.down_arrow = tk.Button(self, text='▼', width=6, command=self.move_down)
        self.down_arrow.grid(row=0, column=1, padx=(5, 0))

        self.delete = tk.Button(self, text='\U00002715', width=3, command=self.delete)
        self.delete.grid(row=0, column=2, padx=(5, 0))

        self.new = tk.Button(self, text='\U00002795', width=6, command=self.new)
        self.new.grid(row=0, column=3, padx=(5, 0))

    def move_up(self):
        components = self.parent.components.listbox.curselection()
        commands = self.parent.commands.listbox.curselection()
        if len(components) > 0:
            p_index = int(components[0])
            if len(commands) > 0:
                c_index = int(commands[0])
                config.routine.move_command_up(p_index, c_index)
            else:
                config.routine.move_component_up(p_index)

    def move_down(self):
        components = self.parent.components.listbox.curselection()
        commands = self.parent.commands.listbox.curselection()
        if len(components) > 0:
            p_index = int(components[0])
            if len(commands) > 0:
                c_index = int(commands[0])
                config.routine.move_command_down(p_index, c_index)
            else:
                config.routine.move_component_down(p_index)

    def delete(self):
        components = self.parent.components.listbox.curselection()
        commands = self.parent.commands.listbox.curselection()
        if len(components) > 0:
            p_index = int(components[0])
            if len(commands) > 0:
                c_index = int(commands[0])
                config.routine.delete_command(p_index, c_index)
            else:
                config.routine.delete_component(p_index)

    def new(self):
        self.parent.parent.editor.create_add_prompt()


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
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

    def unbind_select(self):
        def callback(_):
            commands = self.parent.parent.commands
            commands.clear_selection()
            commands.update_display()

        self.listbox.bind('<<ListboxSelect>>', callback)

    def on_select(self, e):
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
                self.parent.parent.parent.editor.create_edit_ui(config.routine, index, self.update_obj)
            else:
                self.parent.parent.parent.editor.reset()
        else:
            self.parent.parent.commands_var.set([])
            self.parent.parent.parent.editor.reset()

    def update_obj(self, arr, i, stringvars):
        def f():
            new_kwargs = {k: v.get() for k, v in stringvars.items()}
            config.routine.update_component(i, new_kwargs)
            self.parent.parent.parent.editor.create_edit_ui(arr, i, self.update_obj)
        return f

    def select(self, i):
        self.listbox.selection_clear(0, 'end')
        self.listbox.selection_set(i)
        self.listbox.see(i)

    def clear_selection(self):
        self.listbox.selection_clear(0, 'end')


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
        selections = e.widget.curselection()
        pt_selects = self.parent.parent.components.listbox.curselection()
        if len(selections) > 0 and len(pt_selects) > 0:
            c_index = int(selections[0])
            pt_index = int(pt_selects[0])
            self.parent.parent.parent.editor.create_edit_ui(config.routine[pt_index].commands,
                                                            c_index, self.update_obj)
        else:
            self.parent.parent.parent.editor.reset()

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
        super().__init__(parent, 'Recorded Locations', **kwargs)

        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill='y', pady=(0, 5))

        self.listbox = tk.Listbox(self, width=25,
                                  # listvariable=config.gui.routine_var,
                                  exportselection=False,
                                  activestyle='none',
                                  yscrollcommand=self.scroll.set)
        self.listbox.bind('<Up>', lambda e: 'break')
        self.listbox.bind('<Down>', lambda e: 'break')
        self.listbox.bind('<Left>', lambda e: 'break')
        self.listbox.bind('<Right>', lambda e: 'break')
        self.listbox.pack(side=tk.LEFT, expand=True, fill='both', padx=(5, 0), pady=(0, 5))

        self.scroll.config(command=self.listbox.yview)
