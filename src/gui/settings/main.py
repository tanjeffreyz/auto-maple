"""
這個檔案是「設定」分頁的主程式。
它負責把「按鍵設定」、「寵物設定」和「職業專屬設定」組合在一起顯示。
"""

import tkinter as tk
from src.gui.interfaces import KeyBindings
from src.gui.settings.pets import Pets
from src.gui.interfaces import Tab, Frame
from src.common import config


class Settings(Tab):
    def __init__(self, parent, **kwargs):
        # 這裡設定分頁的標題，原本是 'Settings'，現在改為 '系統設定'
        super().__init__(parent, '系統設定', **kwargs)

        # 設定版面配置 (Layout)，這就像是把畫面切成格子
        # weight=1 表示該欄位會隨著視窗拉大而跟著變寬
        self.columnconfigure(0, weight=1)
        self.columnconfigure(3, weight=1)

        # --- 左半邊：一般設定區 ---
        self.column1 = Frame(self)
        self.column1.grid(row=0, column=1, sticky=tk.N, padx=10, pady=10)
        
        # 1. 程式本身的快捷鍵 (例如：F6 重載、Insert 啟動)
        # KeyBindings 是一個幫忙產生按鍵輸入框的工具
        self.controls = KeyBindings(self.column1, '程式快捷鍵控制', config.listener)
        self.controls.pack(side=tk.TOP, fill='x', expand=True)
        
        # 2. 遊戲內的按鍵對應 (例如：撿東西是 Y，跳躍是 Space)
        # 這裡會讀取 config.bot 裡面的設定
        self.common_bindings = KeyBindings(self.column1, '遊戲內按鍵設定', config.bot)
        self.common_bindings.pack(side=tk.TOP, fill='x', expand=True, pady=(10, 0))
        
        # 3. 寵物設定模組 (我們會從 pets.py 引入)
        self.pets = Pets(self.column1)
        self.pets.pack(side=tk.TOP, fill='x', expand=True, pady=(10, 0))

        # --- 右半邊：職業專屬設定區 ---
        self.column2 = Frame(self)
        self.column2.grid(row=0, column=2, sticky=tk.N, padx=10, pady=10)
        
        # 預設顯示「尚未讀取職業指令」，等到使用者載入指令書後會自動更新
        self.class_bindings = KeyBindings(self.column2, '尚未讀取職業指令', None)
        self.class_bindings.pack(side=tk.TOP, fill='x', expand=True)

    def update_class_bindings(self):
        """
        這個功能會在使用者載入新的職業指令書 (例如 kanna.py) 時被呼叫。
        它會刷新右邊的欄位，顯示該職業專屬的技能按鍵。
        """
        # 先把舊的介面刪掉
        self.class_bindings.destroy()
        
        # 取得目前載入的職業名稱 (例如 Kanna) 並將首字母大寫
        class_name = config.bot.command_book.name.capitalize()
        
        # 建立新的按鍵設定區塊，標題顯示為中文
        self.class_bindings = KeyBindings(self.column2, f'{class_name} 職業按鍵', config.bot.command_book)
        self.class_bindings.pack(side=tk.TOP, fill='x', expand=True)
