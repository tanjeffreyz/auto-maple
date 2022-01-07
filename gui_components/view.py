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

        self.canvas = tk.Canvas(self, bg='black', borderwidth=0, highlightthickness=0)
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

        config.curr_cb = tk.StringVar()
        config.curr_routine = tk.StringVar()

        self.cb_label = tk.Label(self, text='Commands:')
        self.cb_label.grid(row=0, column=1, padx=5, sticky=tk.E)
        self.cb_entry = tk.Entry(self, textvariable=config.curr_cb, state=tk.DISABLED)
        self.cb_entry.grid(row=0, column=2, padx=(0, 5), sticky=tk.EW)

        self.r_label = tk.Label(self, text='Routine:')
        self.r_label.grid(row=1, column=1, padx=5, sticky=tk.E)
        self.r_entry = tk.Entry(self, textvariable=config.curr_routine, state=tk.DISABLED)
        self.r_entry.grid(row=1, column=2, padx=(0, 5), sticky=tk.EW)


class Details(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Details', **kwargs)

        config.view_details = tk.Label(self)
        config.view_details.pack(expand=True, fill='both', padx=5, pady=5)


class Routine(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Routine', **kwargs)

        self.scroll = tk.Scrollbar(self)
        self.scroll.pack(side=tk.RIGHT, fill='both', pady=5)

        config.view_listbox = tk.Listbox(self, width=25,
                                         listvariable=config.routine_var,
                                         yscrollcommand=self.scroll.set)
        config.view_listbox.bind('<Up>', lambda e: 'break')
        config.view_listbox.bind('<Down>', lambda e: 'break')
        config.view_listbox.bind('<Left>', lambda e: 'break')
        config.view_listbox.bind('<Right>', lambda e: 'break')
        config.view_listbox.pack(side=tk.LEFT, expand=True, fill='both', padx=(5, 0), pady=5)

        self.scroll.config(command=config.view_listbox.yview)


