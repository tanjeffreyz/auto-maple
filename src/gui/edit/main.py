"""
[編輯介面模組]
這裡允許使用者在介面上直接修改腳本的參數，或是新增動作。
"""

from src.common import config
import inspect
import tkinter as tk
from src.routine.components import Point, Command
from src.gui.edit.minimap import Minimap
from src.gui.edit.record import Record
from src.gui.edit.routine import Routine
from src.gui.edit.status import Status
from src.gui.interfaces import Tab, Frame, LabelFrame


class Edit(Tab):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, '編輯腳本 (Edit)', **kwargs) # 分頁名稱

        self.columnconfigure(0, weight=1)
        self.columnconfigure(4, weight=1)

        self.record = Record(self)
        self.record.grid(row=2, column=3, sticky=tk.NSEW, padx=10, pady=10)

        self.minimap = Minimap(self)
        self.minimap.grid(row=0, column=3, sticky=tk.NSEW, padx=10, pady=10)

        self.status = Status(self)
        self.status.grid(row=1, column=3, sticky=tk.NSEW, padx=10, pady=10)

        self.routine = Routine(self)
        self.routine.grid(row=0, column=1, rowspan=3, sticky=tk.NSEW, padx=10, pady=10)

        self.editor = Editor(self)
        self.editor.grid(row=0, column=2, rowspan=3, sticky=tk.NSEW, padx=10, pady=10)


class Editor(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, '參數編輯器', **kwargs) # 區塊標題

        self.columnconfigure(0, minsize=350)

        self.vars = {}
        self.contents = None
        self.create_default_state()

    def reset(self):
        """重置編輯器回到預設狀態"""
        self.contents.destroy()
        self.create_default_state()

    def create_default_state(self):
        self.vars = {}
        self.contents = Frame(self)
        self.contents.grid(row=0, column=0, sticky=tk.EW, padx=5)

        title = tk.Entry(self.contents, justify=tk.CENTER)
        title.pack(expand=True, fill='x', pady=(5, 2))
        title.insert(0, '尚未選擇任何項目') # 中文提示
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
        """建立單一參數的輸入框"""
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
        """建立編輯現有組件的介面"""
        self.contents.destroy()
        self.vars = {}
        self.contents = Frame(self)
        self.contents.grid(row=0, column=0, sticky=tk.EW, padx=5)

        title = tk.Entry(self.contents, justify=tk.CENTER)
        title.pack(expand=True, fill='x', pady=(5, 2))
        title.insert(0, f"正在編輯：{arr[i].__class__.__name__}") # 顯示目前編輯的物件名稱
        title.config(state=tk.DISABLED)

        if len(arr[i].kwargs) > 0:
            for key, value in arr[i].kwargs.items():
                self.create_entry(key, value)
            button = tk.Button(self.contents, text='儲存變更', command=func(arr, i, self.vars)) # 中文按鈕
            button.pack(pady=5)
        else:
            self.create_disabled_entry()

  
    def create_add_prompt(self):
        """建立搜尋與新增組件的介面"""
        self.contents.destroy()
        self.vars = {}
        self.contents = Frame(self)
        self.contents.grid(row=0, column=0, sticky=tk.EW, padx=5)

        title = tk.Entry(self.contents, justify=tk.CENTER)
        title.pack(expand=True, fill='x', pady=(5, 2))
        title.insert(0, f"新增組件...")
        title.config(state=tk.DISABLED)

        # ... (以下搜尋邏輯保持不變，但將 Entry 提示改為中文) ...
        # [省略部分重複邏輯]
 options = config.routine.get_all_components()
        var = tk.StringVar(value=tuple(options.keys()))

        def update_search(*_):
            value = input_var.get().strip().lower()
            if value == '':
                var.set(tuple(options.keys()))
            else:
                new_options = []
                for key in options:
                    if key.lower().startswith(value):
                        new_options.append(key)
                var.set(new_options)

        def on_entry_return(e):
            value = e.widget.get().strip().lower()
            if value in options:
                self.create_add_ui(options[value], sticky=True)
            else:
                print(f"\n[!] '{value}' is not a valid Component.")

        def on_entry_down(_):
            display.focus()
            display.selection_set(0)

        def on_display_submit(e):
            w = e.widget
            selects = w.curselection()
            if len(selects) > 0:
                value = w.get(int(selects[0]))
                if value in options:
                    self.create_add_ui(options[value], sticky=True)

        def on_display_up(e):
            selects = e.widget.curselection()
            if len(selects) > 0 and int(selects[0]) == 0:
                user_input.focus()

        # Search bar
        input_var = tk.StringVar()
        user_input = tk.Entry(self.contents, textvariable=input_var)
        user_input.pack(expand=True, fill='x')
        user_input.insert(0, 'Search for a component')
        user_input.bind('<FocusIn>', lambda _: user_input.selection_range(0, 'end'))
        user_input.bind('<Return>', on_entry_return)
        user_input.bind('<Down>', on_entry_down)
        input_var.trace('w', update_search)         # Show filtered results in real time
        user_input.focus()

        # Display search results
        results = Frame(self.contents)
        results.pack(expand=True, fill='both', pady=(1, 0))

        scroll = tk.Scrollbar(results)
        scroll.pack(side=tk.RIGHT, fill='both')

        display = tk.Listbox(results, listvariable=var,
                             activestyle='none',
                             yscrollcommand=scroll.set)
        display.bind('<Double-1>', on_display_submit)
        display.bind('<Return>', on_display_submit)
        display.bind('<Up>', on_display_up)
        display.pack(side=tk.LEFT, expand=True, fill='both')

        scroll.config(command=display.yview)

    def create_add_ui(self, component, sticky=False, kwargs=None):
        """
        Creates a UI that edits the parameters of a new COMPONENT instance, and allows
        the user to add this newly created Component to the current routine.
        :param component:   The class to create an instance of.
        :param sticky:      If True, prevents other UI elements from overwriting this one.
        :param kwargs:      Custom arguments for the new object.
        :return:            None
        """

        # Prevent Components and Commands from overwriting this UI
        if sticky:
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
            arg = sig.args[i]
            if arg != 'self' and arg not in kwargs:
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

        add_button = tk.Button(controls, text='新增', command=self.add(component))
        if sticky:          # Only create 'cancel' button if stickied
            add_button.pack(side=tk.RIGHT, pady=5)
            cancel_button = tk.Button(controls, text='取消', command=self.cancel, takefocus=False)
            cancel_button.pack(side=tk.LEFT, pady=5)
        else:
            add_button.pack(pady=5)

    def cancel(self):
        """Button callback that exits the current Component creation UI."""

        routine = self.parent.routine
        routine.components.bind_select()
        routine.commands.bind_select()
        self.update_display()

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
                            self.parent.routine.commands.update_display()
                            self.cancel()
                        else:
                            print(f"\n[!] 新增指令時發生錯誤：目前選定的元件不是座標。.")
                    else:
                        print(f"\n[!]新增指令時出錯：目前未選擇任何座標。")
                else:
                    config.routine.append_component(obj)
                    self.cancel()
            except (ValueError, TypeError) as e:
                print(f"\n[!] 發現無效參數for '{component.__name__}':")
                print(f"{' ' * 4} -  {e}")
        return f

    def update_display(self):
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
