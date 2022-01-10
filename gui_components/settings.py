"""Displays Auto Maple's current settings and allows the user to edit them."""

import config
import utils
import tkinter as tk
import keyboard as kb
from gui_components.interfaces import Tab, Frame, LabelFrame


class Settings(Tab):
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

        # self.vars = {}
        self.forward = {}
        self.backward = {}
        self.contents = None
        self.create_edit_ui()

    def create_edit_ui(self):
        # self.vars = {}
        self.forward = {}
        self.backward = {}
        self.contents = Frame(self)
        self.contents.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        if config.listener is not None:         # For when running GUI only
            for action, key in config.listener.key_bindings.items():
                self.forward[action] = key
                self.backward[key] = action
                self.create_entry(action, key)
            self.focus()
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
            if value in vkeys.KEY_MAP:          # TODO: verify using kb not vkeys
                config.listener.key_bindings[key] = value
            else:
                print(f" !  Error while binding '{key}': '{value}' is not a valid key.")
                failures += 1

        if failures == 0:
            print('[~] Successfully saved all key bindings.')
        else:
            print(f'[~] Found {failures} errors, successfully saved the rest.')
        self.create_edit_ui()

    def create_entry(self, key, value):
        """
        Creates an input row for a single key bind. KEY is the name of its action
        while VALUE is its currently assigned key.
        """


        # self.vars[key] = new_var

        row = Frame(self.contents, highlightthickness=0)
        row.pack(expand=True, fill='x')

        label = tk.Entry(row)
        label.grid(row=0, column=0, sticky=tk.EW)
        label.insert(0, key)
        label.config(state=tk.DISABLED)

        def on_click(_):
            bottom.delete(0, 'end')
            bottom.insert(0, '<Press any key>')

        def validate(text):
            print('validated')
            k = kb.read_key()
            # # entry.delete(0, 'end')
            # # entry.insert(0, k)
            display_var.set(k)
            # try:
            #     float(text)
            # except:
            #     return False
            # return True
            return False

        reg = self.register(validate)
        display_var = tk.StringVar(value=value)
        bottom = tk.Entry(row, textvariable=display_var)
        bottom.insert(0, value)
        # entry.bind('<1>', on_click)
        bottom.config(validate='key', validatecommand=(reg, '%P'))
        bottom.grid(row=0, column=1, sticky=tk.EW)

    def create_disabled_entry(self):
        row = Frame(self.contents, highlightthickness=0)
        row.pack(expand=True, fill='x')

        label = tk.Entry(row)
        label.grid(row=0, column=0, sticky=tk.EW)
        label.config(state=tk.DISABLED)

        entry = tk.Entry(row)
        entry.grid(row=0, column=1, sticky=tk.EW)
        entry.config(state=tk.DISABLED)
