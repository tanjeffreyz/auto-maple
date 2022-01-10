"""Displays Auto Maple's current settings and allows the user to edit them."""

import config
import utils
import vkeys
import tkinter as tk
from gui_components.interfaces import Page, Frame, LabelFrame


class Settings(Page):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Settings', **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

        self.keybindings = KeyBindings(self)
        self.keybindings.grid(row=0, column=1, sticky=tk.NSEW)


class KeyBindings(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Key Bindings', **kwargs)

        self.columnconfigure(0, minsize=300)

        self.vars = {}
        self.contents = None
        self.create_edit_ui()

    def create_edit_ui(self):
        self.vars = {}
        self.contents = Frame(self)
        self.contents.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        if config.listener is not None:         # For when running GUI only
            for key, value in config.listener.key_bindings.items():
                self.create_entry(key, value)
        else:
            self.create_disabled_entry()

        button = tk.Button(self.contents, text='Save', command=self.save)
        button.pack(pady=5)

    def refresh_edit_ui(self):
        self.contents.destroy()
        self.create_edit_ui()

    def save(self):
        utils.print_separator()
        print('[~] Saving key bindings...')

        failures = 0
        for key, var in self.vars.items():
            value = var.get().lower()
            if value in vkeys.KEY_MAP:
                config.listener.key_bindings[key] = value
            else:
                print(f" !  Error while binding '{key}': '{value}' is not a valid key.")
                failures += 1

        if failures == 0:
            print('[~] Successfully saved all key bindings.')
        else:
            print(f'[~] Found {failures} errors, successfully saved the rest.')
        self.create_edit_ui()

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
        Creates an input row for a single key bind. KEY is the name of its action
        while VALUE is its currently assigned key.
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
        entry.bind('<FocusIn>', lambda _: entry.selection_range(0, 'end'))
