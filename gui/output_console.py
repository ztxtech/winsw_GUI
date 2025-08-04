import tkinter as tk
from tkinter import ttk


class OutputConsole(ttk.Labelframe):
    """ 显示程序日志的控制台 """

    def __init__(self, parent):
        super().__init__(parent, text="程序输出", padding=(10, 5))

        self.text = tk.Text(self, height=8, wrap="word", state="disabled")
        self.text.pack(expand=True, fill="both")

    def log(self, message):
        """向控制台添加一条日志"""
        self.text.config(state="normal")
        self.text.insert(tk.END, message + "\n")
        self.text.see(tk.END)  # 自动滚动到底部
        self.text.config(state="disabled")
