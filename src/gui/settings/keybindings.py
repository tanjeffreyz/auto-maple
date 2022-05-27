import tkinter as tk
import keyboard as kb
from src.gui.interfaces import LabelFrame, Frame
from src.common import utils
from src.common.interfaces import Configurable


class KeyBindings(LabelFrame):
    def __init__(self, parent, label, target, **kwargs):
        super().__init__(parent, label, **kwargs)
        assert isinstance(target, Configurable)
        self.target = target

        self.columnconfigure(0, minsize=300)

        self.displays = {}          # Holds each action's display variable
        self.forward = {}           # Maps actions to keys
        self.backward = {}          # Maps keys to actions
        self.prev_a = ''
        self.prev_k = ''

        self.contents = None
        self.create_edit_ui()

    def create_edit_ui(self):
        self.displays = {}
        self.forward = {}
        self.backward = {}
        self.prev_a = ''
        self.prev_k = ''

        self.contents = Frame(self)
        self.contents.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)

        if self.target is not None:         # For when running GUI only
            for action, key in self.target.config.items():
                self.forward[action] = key
                self.backward[key] = action
                self.create_entry(action, key)
            self.focus()
        else:
            self.create_disabled_entry()

        reset = tk.Button(self.contents, text='Reset', command=self.refresh_edit_ui, takefocus=False)
        reset.pack(side=tk.LEFT, pady=5)

        save = tk.Button(self.contents, text='Save', command=self.save, takefocus=False)
        save.pack(side=tk.RIGHT, pady=5)

    def refresh_edit_ui(self):
        self.contents.destroy()
        self.create_edit_ui()

    @utils.run_if_disabled('\n[!] Cannot save key bindings while Auto Maple is enabled')
    def save(self):
        utils.print_separator()
        print(f"[~] Saving key bindings to '{self.target.TARGET}':")

        failures = 0
        for action, key in self.forward.items():
            if key != '':
                self.target.config[action] = key
            else:
                print(f" !  Action '{action}' was not bound to a key")
                failures += 1

        self.target.save_config()
        if failures == 0:
            print(' ~  Successfully saved all key bindings')
        else:
            print(f' ~  Successfully saved all except for {failures} key bindings')
        self.create_edit_ui()

    def create_entry(self, action, key):
        """
        Creates an input row for a single key bind. ACTION is assigned to KEY.
        """

        display_var = tk.StringVar(value=key)
        self.displays[action] = display_var

        row = Frame(self.contents, highlightthickness=0)
        row.pack(expand=True, fill='x')

        label = tk.Entry(row)
        label.grid(row=0, column=0, sticky=tk.EW)
        label.insert(0, action)
        label.config(state=tk.DISABLED)

        def on_key_press(_):
            k = kb.read_key()
            if action != self.prev_a:
                self.prev_k = ''
                self.prev_a = action
            if k != self.prev_k:
                prev_key = self.forward[action]
                self.backward.pop(prev_key, None)
                if k in self.backward:
                    prev_action = self.backward[k]
                    self.forward[prev_action] = ''
                    self.displays[prev_action].set('')
                display_var.set(k)
                self.forward[action] = k
                self.backward[k] = action
                self.prev_k = k

        def validate(d):
            """Blocks user insertion, but allows StringVar set()."""

            if d == '-1':
                return True
            return False

        reg = (self.register(validate), '%d')
        entry = tk.Entry(row, textvariable=display_var,
                         validate='key', validatecommand=reg,
                         takefocus=False)
        entry.bind('<KeyPress>', on_key_press)
        entry.grid(row=0, column=1, sticky=tk.EW)

    def create_disabled_entry(self):
        row = Frame(self.contents, highlightthickness=0)
        row.pack(expand=True, fill='x')

        label = tk.Entry(row)
        label.grid(row=0, column=0, sticky=tk.EW)
        label.config(state=tk.DISABLED)

        entry = tk.Entry(row)
        entry.grid(row=0, column=1, sticky=tk.EW)
        entry.config(state=tk.DISABLED)
