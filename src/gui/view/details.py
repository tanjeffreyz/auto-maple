import tkinter as tk
from src.gui.interfaces import LabelFrame
from src.common import config


class Details(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Details', **kwargs)
        self.name_var = tk.StringVar()

        self.name = tk.Entry(self, textvariable=self.name_var, justify=tk.CENTER, state=tk.DISABLED)
        self.name.pack(pady=(5, 2))

        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.text = tk.Text(self, width=1, height=10,
                            yscrollcommand=self.scroll.set,
                            state=tk.DISABLED, wrap=tk.WORD)
        self.text.pack(side=tk.LEFT, expand=True, fill='both', padx=(5, 0), pady=(0, 5))

        self.scroll.config(command=self.text.yview)

    def show_details(self, e):
        """Callback for updating the Details section everytime Listbox selection changes."""

        selections = e.widget.curselection()
        if len(selections) > 0:
            index = int(selections[0])
            self.display_info(index)

    def update_details(self):
        """Updates Details to show info about the current selection."""

        selects = self.parent.routine.listbox.curselection()
        if len(selects) > 0:
            self.display_info(int(selects[0]))
        else:
            self.clear_info()

    def display_info(self, index):
        """Updates the Details section to show info about the Component at position INDEX."""

        self.text.config(state=tk.NORMAL)

        info = config.routine[index].info()
        self.name_var.set(info['name'])
        arr = []
        for key, value in info['vars'].items():
            arr.append(f'{key}: {value}')
        self.text.delete(1.0, 'end')
        self.text.insert(1.0, '\n'.join(arr))

        self.text.config(state=tk.DISABLED)

    def clear_info(self):
        self.name_var.set('')
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, 'end')
        self.text.config(state=tk.DISABLED)
