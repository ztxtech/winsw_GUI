import tkinter as tk
from tkinter import ttk, filedialog


class LoggingTab(ttk.Frame):
    """ “日志记录” 选项卡 """

    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        log_frame = ttk.Labelframe(self, text="日志配置", padding=(10, 5))
        log_frame.pack(expand=True, fill="both", padx=10, pady=10)
        log_frame.columnconfigure(1, weight=1)

        # 日志模式
        ttk.Label(log_frame, text="日志模式:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.log_mode_var = tk.StringVar()
        self.log_mode_combo = ttk.Combobox(
            log_frame,
            textvariable=self.log_mode_var,
            values=["append", "roll", "reset", "ignore"],
            state="readonly"
        )
        self.log_mode_combo.grid(row=0, column=1, sticky="ew", padx=5)

        # 日志目录
        ttk.Label(log_frame, text="日志目录:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.log_path_var = tk.StringVar()
        self.log_path_entry = ttk.Entry(log_frame, textvariable=self.log_path_var)
        self.log_path_entry.grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(log_frame, text="...", width=3, command=self.browse_log_path).grid(row=1, column=2, sticky="w",
                                                                                      padx=(0, 5))

    def browse_log_path(self):
        path = filedialog.askdirectory()
        if path:
            self.log_path_var.set(path)

    def set_data(self, data: dict):
        self.log_mode_var.set(data.get('log_mode', 'append'))
        self.log_path_var.set(data.get('logpath', ''))

    def get_data(self) -> dict:
        return {
            'log_mode': self.log_mode_var.get(),
            'logpath': self.log_path_var.get()
        }
