import os
import tkinter as tk
from tkinter import ttk


class ServiceListView(ttk.Frame):
    """ 左侧的服务列表视图 """

    def __init__(self, parent, select_callback):
        super().__init__(parent)
        self.select_callback = select_callback
        self.service_dir = "services"

        # --- UI Elements ---
        self.listbox = tk.Listbox(self, exportselection=False)
        self.listbox.pack(expand=True, fill="both", padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        self.refresh_list()

    def refresh_list(self):
        """刷新服务列表，扫描services目录"""
        self.listbox.delete(0, tk.END)
        try:
            files = [f for f in os.listdir(self.service_dir) if f.endswith(".xml")]
            for filename in sorted(files):
                self.listbox.insert(tk.END, filename)
        except FileNotFoundError:
            # services目录可能不存在
            pass

    def on_select(self, event):
        """当用户在列表中选择一项时调用"""
        selection_indices = self.listbox.curselection()
        if not selection_indices:
            return

        selected_index = selection_indices[0]
        filename = self.listbox.get(selected_index)

        # 调用主窗口传递的回调函数
        if self.select_callback:
            self.select_callback(filename)

    def get_selected_filename(self):
        """获取当前选中的文件名"""
        selection_indices = self.listbox.curselection()
        if not selection_indices:
            return None
        return self.listbox.get(selection_indices[0])
