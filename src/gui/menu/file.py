import os
import tkinter as tk
from src.common import config, utils
from src.gui.interfaces import MenuBarItem
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno


class File(MenuBarItem):
    def __init__(self, parent, **kwargs):
        # 將選單名稱改為「檔案」
        super().__init__(parent, '檔案 (File)', **kwargs)

        self.add_command(
            label='新建腳本 (New Routine)',
            command=utils.async_callback(self, File._new_routine),
            state=tk.DISABLED
        )
        self.add_command(
            label='儲存腳本 (Save Routine)',
            command=utils.async_callback(self, File._save_routine),
            state=tk.DISABLED
        )
        self.add_separator()
        self.add_command(
            label='讀取職業指令 (Load Command Book)', # 關鍵第一步
            command=utils.async_callback(self, File._load_commands)
        )
        self.add_command(
            label='載入腳本 (Load Routine)', # 關鍵第二步
            command=utils.async_callback(self, File._load_routine),
            state=tk.DISABLED
        )

    def enable_routine_state(self):
        """當成功讀取職業後，解鎖其他按鈕"""
        self.entryconfig('新建腳本 (New Routine)', state=tk.NORMAL)
        self.entryconfig('儲存腳本 (Save Routine)', state=tk.NORMAL)
        self.entryconfig('載入腳本 (Load Routine)', state=tk.NORMAL)

    @staticmethod
    @utils.run_if_disabled('\n[!] 錯誤：請先停止機器人再執行此動作')
    def _new_routine():
        if config.routine.dirty:
            if not askyesno(title='新建腳本',
                            message='目前的腳本尚未儲存，確定要開新檔案嗎？',
                            icon='warning'):
                return
        config.routine.clear()

    @staticmethod
    @utils.run_if_disabled('\n[!] 錯誤：請先停止機器人再存檔')
    def _save_routine():
        file_path = asksaveasfilename(initialdir=get_routines_dir(),
                                      title='儲存腳本',
                                      filetypes=[('CSV 檔案', '*.csv')],
                                      defaultextension='*.csv')
        if file_path:
            config.routine.save(file_path)

    @staticmethod
    @utils.run_if_disabled('\n[!] 錯誤：請先停止機器人再載入腳本')
    def _load_routine():
        if config.routine.dirty:
            if not askyesno(title='載入腳本',
                            message='目前的腳本尚未儲存，確定要載入新檔案嗎？',
                            icon='warning'):
                return
        file_path = askopenfilename(initialdir=get_routines_dir(),
                                    title='選擇腳本檔案',
                                    filetypes=[('CSV 檔案', '*.csv')])
        if file_path:
            config.routine.load(file_path)

    @staticmethod
    @utils.run_if_disabled('\n[!] 錯誤：請先停止機器人再載入指令')
    def _load_commands():
        if config.routine.dirty:
            if not askyesno(title='讀取職業指令',
                            message='讀取新的職業將會清空目前腳本，確定要繼續嗎？',
                            icon='warning'):
                return
        file_path = askopenfilename(initialdir=os.path.join(config.RESOURCES_DIR, 'command_books'),
                                    title='選擇職業指令書 (.py)',
                                    filetypes=[('Python 檔案', '*.py')])
        if file_path:
            config.bot.load_commands(file_path)


def get_routines_dir():
    """取得腳本存放路徑，如果沒有就自動建立"""
    target = os.path.join(config.RESOURCES_DIR, 'routines', config.bot.command_book.name)
    if not os.path.exists(target):
        os.makedirs(target)
    return target
