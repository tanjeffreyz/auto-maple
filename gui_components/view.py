"""Displays the current minimap as well as various information regarding the current routine."""

import config
import utils
import cv2
import tkinter as tk
from gui_components.interfaces import LabelFrame, Page
from capture import Capture
from PIL import Image, ImageTk


class View(Page):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'View', **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.minimap = Minimap(self)
        self.minimap.grid(row=0, column=2, sticky=tk.NSEW, padx=10, pady=10)

        self.status = Status(self)
        self.status.grid(row=1, column=2, sticky=tk.NSEW, padx=10, pady=10)

        self.details = Details(self)
        self.details.grid(row=2, column=2, sticky=tk.NSEW, padx=10, pady=10)

        self.routine = Routine(self)
        self.routine.grid(row=0, column=1, rowspan=3, sticky=tk.NSEW, padx=10, pady=10)


class Minimap(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Minimap', **kwargs)

        self.canvas = tk.Canvas(self, bg='black',
                                width=400, height=300,
                                borderwidth=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill='both', padx=5, pady=5)

    def display_minimap(self):
        """Updates the Main page with the current minimap."""

        if config.minimap:
            rune_active = config.minimap['rune_active']
            rune_pos = config.minimap['rune_pos']
            path = config.minimap['path']
            player_pos = config.minimap['player_pos']

            img = cv2.cvtColor(config.minimap['minimap'], cv2.COLOR_BGR2RGB)
            height, width, _ = img.shape
            c_height, c_width = self.canvas.winfo_height(), self.canvas.winfo_width()

            # Resize minimap to fit the Canvas
            ratio = min(c_width / width, c_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            if new_height * new_width > 0:
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

            # Mark the position of the active rune
            if rune_active:
                cv2.circle(img,
                           utils.convert_to_absolute(rune_pos, img),
                           5,
                           (128, 0, 128),
                           -1)

            # Draw the current path that the program is taking
            if config.enabled and len(path) > 1:
                for i in range(len(path) - 1):
                    start = utils.convert_to_absolute(path[i], img)
                    end = utils.convert_to_absolute(path[i + 1], img)
                    cv2.line(img, start, end, (0, 255, 255), 1)

            # Draw each Point in the routine as a circle
            for p in config.routine.sequence:
                Capture.draw_point(img,
                                   p,
                                   (0, 255, 0) if config.enabled else (255, 0, 0))

            # Display the current Layout
            if config.layout:
                config.layout.draw(img)

            # Draw the player's position on top of everything
            cv2.circle(img,
                       utils.convert_to_absolute(player_pos, img),
                       3,
                       (0, 0, 255),
                       -1)

            # Display the minimap in the Canvas
            img = ImageTk.PhotoImage(Image.fromarray(img))
            self.canvas.create_image(c_width // 2,
                                     c_height // 2,
                                     image=img, anchor=tk.CENTER)
            self._img = img                 # Prevent garbage collection
        self.after(33, self.display_minimap)


class Status(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Status', **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.curr_cb = tk.StringVar()
        self.curr_routine = tk.StringVar()

        self.cb_label = tk.Label(self, text='Command Book:')
        self.cb_label.grid(row=0, column=1, padx=5, pady=(5, 0), sticky=tk.E)
        self.cb_entry = tk.Entry(self, textvariable=self.curr_cb, state=tk.DISABLED)
        self.cb_entry.grid(row=0, column=2, padx=(0, 5), pady=(5, 0), sticky=tk.EW)

        self.r_label = tk.Label(self, text='Routine:')
        self.r_label.grid(row=1, column=1, padx=5, pady=(0, 5), sticky=tk.E)
        self.r_entry = tk.Entry(self, textvariable=self.curr_routine, state=tk.DISABLED)
        self.r_entry.grid(row=1, column=2, padx=(0, 5), pady=(0, 5), sticky=tk.EW)

    def update_cb(self, string):
        self.curr_cb.set(string)

    def update_routine(self, string):
        self.curr_routine.set(string)


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

    def update_details(self, e):
        """Callback for updating the Details section everytime Listbox selection changes."""

        selections = e.widget.curselection()
        if len(selections) > 0:
            index = int(selections[0])
            self.display_info(index)

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


class Routine(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Routine', **kwargs)

        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill='both', pady=5)

        self.listbox = tk.Listbox(self, width=25,
                                  listvariable=config.gui.routine_var,
                                  exportselection=False,
                                  yscrollcommand=self.scroll.set)
        self.listbox.bind('<Up>', lambda e: 'break')
        self.listbox.bind('<Down>', lambda e: 'break')
        self.listbox.bind('<Left>', lambda e: 'break')
        self.listbox.bind('<Right>', lambda e: 'break')
        self.listbox.bind('<<ListboxSelect>>', parent.details.update_details)
        self.listbox.pack(side=tk.LEFT, expand=True, fill='both', padx=(5, 0), pady=5)

        self.scroll.config(command=self.listbox.yview)

    def select(self, i, end):
        self.listbox.selection_clear(0, end)
        self.listbox.selection_set(i)
        self.listbox.activate(i)
