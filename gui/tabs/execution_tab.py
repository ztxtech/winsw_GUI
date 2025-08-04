import tkinter as tk
from tkinter import ttk, filedialog


class ExecutionTab(ttk.Frame):
    """ “执行与参数” 选项卡 """

    def __init__(self, parent, autofill_callback):
        super().__init__(parent)
        self.autofill_callback = autofill_callback
        self.create_widgets()

    def create_widgets(self):
        exec_frame = ttk.Labelframe(self, text="执行配置", padding=(10, 5))
        exec_frame.pack(expand=True, fill="both", padx=10, pady=10)
        exec_frame.columnconfigure(1, weight=1)

        # 可执行文件
        ttk.Label(exec_frame, text="可执行文件:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.executable_var = tk.StringVar()
        self.executable_entry = ttk.Entry(exec_frame, textvariable=self.executable_var)
        self.executable_entry.grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(exec_frame, text="...", width=3, command=self.browse_executable).grid(row=0, column=2, sticky="w",
                                                                                         padx=(0, 5))

        # 工作目录
        ttk.Label(exec_frame, text="工作目录:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.workdir_var = tk.StringVar()
        self.workdir_entry = ttk.Entry(exec_frame, textvariable=self.workdir_var)
        self.workdir_entry.grid(row=1, column=1, sticky="ew", padx=5)
        ttk.Button(exec_frame, text="...", width=3, command=self.browse_workdir).grid(row=1, column=2, sticky="w",
                                                                                      padx=(0, 5))

        # 参数
        ttk.Label(exec_frame, text="参数:").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        self.args_text = tk.Text(exec_frame, height=8, wrap="word")
        self.args_text.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=5, pady=5)
        exec_frame.rowconfigure(2, weight=1)

    def browse_executable(self):
        path = filedialog.askopenfilename()
        if path:
            self.executable_var.set(path)
            # 调用回调函数，尝试自动填充ID和名称
            if self.autofill_callback:
                self.autofill_callback(path)

    def browse_workdir(self):
        path = filedialog.askdirectory()
        if path:
            self.workdir_var.set(path)

    def set_data(self, data: dict):
        self.executable_var.set(data.get('executable', ''))
        self.workdir_var.set(data.get('workingdirectory', ''))
        self.args_text.delete("1.0", tk.END)
        self.args_text.insert("1.0", data.get('arguments', ''))

    def get_data(self) -> dict:
        return {
            'executable': self.executable_var.get(),
            'workingdirectory': self.workdir_var.get(),
            'arguments': self.args_text.get("1.0", tk.END).strip()
        }
