import tkinter as tk
from tkinter import ttk


class AdvancedTab(ttk.Frame):
    """ “高级” 选项卡 """

    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # --- 进程优先级 ---
        priority_frame = ttk.Labelframe(self, text="进程优先级", padding=(10, 5))
        priority_frame.pack(fill="x", padx=10, pady=10)
        priority_frame.columnconfigure(1, weight=1)

        ttk.Label(priority_frame, text="优先级:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.priority_var = tk.StringVar()
        self.priority_combo = ttk.Combobox(
            priority_frame,
            textvariable=self.priority_var,
            values=["normal", "idle", "belownormal", "abovenormal", "high", "realtime"],
            state="readonly"
        )
        self.priority_combo.grid(row=0, column=1, sticky="ew", padx=5)

        # --- 停止超时 ---
        stop_frame = ttk.Labelframe(self, text="超时与交互", padding=(10, 5))
        stop_frame.pack(fill="x", padx=10, pady=10)
        stop_frame.columnconfigure(1, weight=1)

        ttk.Label(stop_frame, text="停止超时:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.stop_timeout_var = tk.StringVar()
        self.stop_timeout_entry = ttk.Entry(stop_frame, textvariable=self.stop_timeout_var)
        self.stop_timeout_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(stop_frame, text="(例如: 15 sec, 1 min)").grid(row=0, column=2, sticky="w", padx=5)

        # --- 桌面交互 ---
        self.interactive_var = tk.BooleanVar()
        self.interactive_check = ttk.Checkbutton(
            stop_frame,
            text="允许服务与桌面交互",
            variable=self.interactive_var
        )
        self.interactive_check.grid(row=1, column=0, columnspan=3, sticky="w", padx=5, pady=5)

    def set_data(self, data: dict):
        self.priority_var.set(data.get('priority', 'normal'))
        self.stop_timeout_var.set(data.get('stoptimeout', '15 sec'))
        self.interactive_var.set(data.get('interactive', False))

    def get_data(self) -> dict:
        return {
            'priority': self.priority_var.get(),
            'stoptimeout': self.stop_timeout_var.get(),
            'interactive': self.interactive_var.get()
        }
