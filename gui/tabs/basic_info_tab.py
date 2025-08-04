import tkinter as tk
from tkinter import ttk


class BasicInfoTab(ttk.Frame):
    """ “基本信息” 选项卡 """

    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # 使用Labelframe进行分组
        info_frame = ttk.Labelframe(self, text="服务识别信息", padding=(10, 5))
        info_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # 配置Grid布局
        info_frame.columnconfigure(1, weight=1)

        # 服务ID
        ttk.Label(info_frame, text="服务 ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_var = tk.StringVar()
        self.id_entry = ttk.Entry(info_frame, textvariable=self.id_var)
        self.id_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # 服务名称
        ttk.Label(info_frame, text="服务名称:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(info_frame, textvariable=self.name_var)
        self.name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # 服务描述
        ttk.Label(info_frame, text="服务描述:").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        self.desc_text = tk.Text(info_frame, height=5, wrap="word")
        self.desc_text.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        info_frame.rowconfigure(2, weight=1)

    def set_data(self, data: dict):
        """用字典数据填充UI"""
        self.id_var.set(data.get('id', ''))
        self.name_var.set(data.get('name', ''))
        self.desc_text.delete("1.0", tk.END)
        self.desc_text.insert("1.0", data.get('description', ''))

    def get_data(self) -> dict:
        """从UI获取数据到字典"""
        return {
            'id': self.id_var.get(),
            'name': self.name_var.get(),
            'description': self.desc_text.get("1.0", tk.END).strip()
        }
