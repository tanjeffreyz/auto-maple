import git
import tkinter as tk
from src.common import config
from src.gui.interfaces import MenuBarItem, LabelFrame, Frame
from tkinter.messagebox import askyesno


class Update(MenuBarItem):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Update', **kwargs)

        for path in config.bot.submodules:
            name = path.capitalize()
            self.add_command(
                label=name,
                command=lambda: UpdatePrompt(self, name, path)
            )


class UpdatePrompt(tk.Toplevel):
    RESOLUTION = '500x400'

    def __init__(self, parent, name, path, **kwargs):
        super().__init__(parent, **kwargs)

        self.path = path

        self.grab_set()
        self.title(f'Update {name}')
        icon = tk.PhotoImage(file='assets/icon.png')
        self.iconphoto(False, icon)
        self.geometry(UpdatePrompt.RESOLUTION)
        self.resizable(False, False)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, weight=1)
        self.list_var = tk.StringVar(value=[])
        self.dirty = False

        # Display local changes
        display_frame = LabelFrame(self, 'Local Changes')
        display_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=(10, 0), pady=10)
        self.scroll = tk.Scrollbar(display_frame)
        self.scroll.pack(side=tk.RIGHT, fill='both', pady=5)
        self.listbox = tk.Listbox(display_frame,
                                  width=40,
                                  height=15,
                                  listvariable=self.list_var,
                                  exportselection=False,
                                  activestyle='none',
                                  yscrollcommand=self.scroll.set)
        self.listbox.pack(side=tk.LEFT, expand=True, fill='both', padx=(5, 0), pady=5)

        # Controls
        controls_frame = Frame(self)
        controls_frame.grid(row=0, column=2, sticky=tk.NSEW, padx=10, pady=10)
        self.refresh = tk.Button(controls_frame, text='Refresh', command=self._refresh_display)
        self.refresh.pack(side=tk.TOP, pady=(10, 5))
        self.soft_update = tk.Button(
            controls_frame,
            text='Update',
            command=self._update
        )
        self.soft_update.pack(side=tk.BOTTOM)
        self.force_update = tk.Button(
            controls_frame,
            text='Rebuild',
            command=lambda: self._update(force=True)
        )
        self.force_update.pack(side=tk.BOTTOM, pady=(0, 5))

        self.listbox.bindtags((self.listbox, config.gui.root, "all"))       # Unbind all events
        self.bind('<FocusIn>', lambda *_: self._refresh_display())
        self.focus()

    def _update(self, force=False):
        if force and self.dirty:
            if not askyesno(title='Overwrite Local Changes',
                            message=f"Rebuilding '{self.path}' will overwrite all local changes. "
                                    'Do you wish to proceed?',
                            icon='warning'):
                return
        config.bot.update_submodules(force=force)
        self._close()

    def _refresh_display(self):
        self.list_var.set(['Searching for local changes...'])
        self.update()
        repo = git.Repo(self.path)
        diffs = []
        paths = set()
        for item in repo.index.diff(None) + repo.index.diff('HEAD'):        # Unstaged and staged changes
            path = item.a_path
            if path not in paths:       # Only show changes once per file, unstaged has precedence over staged
                diffs.append(f'{item.change_type} - {path}')
                paths.add(path)
        self.dirty = len(diffs) > 0
        if len(diffs) == 0:
            diffs.append('No local changes found, safe to update')
        self.list_var.set(diffs)

    def _close(self):
        self.destroy()
        self.update()
