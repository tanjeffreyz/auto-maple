"""
這個檔案負責處理寵物的自動餵食設定。
包含「是否啟用」的勾選框，以及「寵物數量」的選擇。
"""

import tkinter as tk
from src.gui.interfaces import LabelFrame, Frame
from src.common.interfaces import Configurable


class Pets(LabelFrame):
    def __init__(self, parent, **kwargs):
        # 設定這個區塊的標題為中文
        super().__init__(parent, '寵物自動餵食', **kwargs)

        # 載入寵物設定檔
        self.pet_settings = PetSettings('pets')
        
        # 讀取目前的設定值 (布林值代表是否勾選，整數代表寵物數量)
        self.auto_feed = tk.BooleanVar(value=self.pet_settings.get('Auto-feed'))
        self.num_pets = tk.IntVar(value=self.pet_settings.get('Num pets'))

        # --- 第一行：開關 ---
        feed_row = Frame(self)
        feed_row.pack(side=tk.TOP, fill='x', expand=True, pady=5, padx=5)
        
        # 建立一個勾選框 (Checkbutton)
        check = tk.Checkbutton(
            feed_row,
            variable=self.auto_feed,    # 綁定變數
            text='啟用自動餵食功能',      # 顯示的中文文字
            command=self._on_change     # 當勾選狀態改變時，執行 _on_change 存檔
        )
        check.pack()

        # --- 第二行：數量設定 ---
        num_row = Frame(self)
        num_row.pack(side=tk.TOP, fill='x', expand=True, pady=(0, 5), padx=5)
        
        # 顯示提示文字
        label = tk.Label(num_row, text='請選擇你有幾隻寵物：')
        label.pack(side=tk.LEFT, padx=(0, 15))
        
        # 放置圓形選項按鈕 (Radiobutton) 的容器
        radio_group = Frame(num_row)
        radio_group.pack(side=tk.LEFT)
        
        # 產生 1 到 3 的選項
        for i in range(1, 4):
            radio = tk.Radiobutton(
                radio_group,
                text=f'{i} 隻',          # 選項文字：1 隻, 2 隻...
                variable=self.num_pets,  # 綁定變數
                value=i,                 # 該選項代表的數值
                command=self._on_change  # 當選擇改變時，執行 _on_change 存檔
            )
            radio.pack(side=tk.LEFT, padx=(0, 10))

    def _on_change(self):
        """
        當使用者在介面上更改設定時，這個函式會被呼叫。
        它負責把新的設定寫入硬碟，這樣下次開程式才記得住。
        """
        self.pet_settings.set('Auto-feed', self.auto_feed.get())
        self.pet_settings.set('Num pets', self.num_pets.get())
        self.pet_settings.save_config()


class PetSettings(Configurable):
    """
    這是一個設定檔類別，負責管理寵物相關的數據。
    注意：字典裡的 Key (如 'Auto-feed') 是程式內部代號，建議保留英文，以免存檔讀取錯誤。
    """
    DEFAULT_CONFIG = {
        'Auto-feed': False,  # 預設不開啟
        'Num pets': 1        # 預設 1 隻寵物
    }

    def get(self, key):
        return self.config[key]

    def set(self, key, value):
        # 確保設定的 Key 是存在的，防止打錯字
        assert key in self.config
        self.config[key] = value
