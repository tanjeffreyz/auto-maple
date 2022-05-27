import tkinter as tk
import cv2
from PIL import ImageTk, Image
from src.common import config, utils
from src.routine.components import Point
from src.gui.interfaces import LabelFrame


class Minimap(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Minimap', **kwargs)

        self.WIDTH = 400
        self.HEIGHT = 300
        self.canvas = tk.Canvas(self, bg='black',
                                width=self.WIDTH, height=self.HEIGHT,
                                borderwidth=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill='both', padx=5, pady=5)
        self.container = None

        self.draw_default()

    def draw_point(self, location):
        """Draws a circle representing a Point centered at LOCATION."""

        if config.capture.minimap_sample is not None:
            minimap = cv2.cvtColor(config.capture.minimap_sample, cv2.COLOR_BGR2RGB)
            img = self.resize_to_fit(minimap)
            utils.draw_location(img, location, (0, 255, 0))
            self.draw(img)

    def draw_default(self):
        """Displays just the minimap sample without any markings."""

        if config.capture.minimap_sample is not None:
            minimap = cv2.cvtColor(config.capture.minimap_sample, cv2.COLOR_BGR2RGB)
            img = self.resize_to_fit(minimap)
            self.draw(img)

    def redraw(self):
        """Re-draws the current point if it exists, otherwise resets to the default state."""

        selects = self.parent.routine.components.listbox.curselection()
        if len(selects) > 0:
            index = int(selects[0])
            obj = config.routine[index]
            if isinstance(obj, Point):
                self.draw_point(obj.location)
                self.parent.record.clear_selection()
            else:
                self.draw_default()
        else:
            self.draw_default()

    def resize_to_fit(self, img):
        """Returns a copy of IMG resized to fit the Canvas."""

        height, width, _ = img.shape
        ratio = min(self.WIDTH / width, self.HEIGHT / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        if new_height * new_width > 0:
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return img

    def draw(self, img):
        """Draws IMG onto the Canvas."""

        if config.layout:
            config.layout.draw(img)     # Display the current Layout

        img = ImageTk.PhotoImage(Image.fromarray(img))
        if self.container is None:
            self.container = self.canvas.create_image(self.WIDTH // 2,
                                                      self.HEIGHT // 2,
                                                      image=img, anchor=tk.CENTER)
        else:
            self.canvas.itemconfig(self.container, image=img)
        self._img = img                 # Prevent garbage collection
