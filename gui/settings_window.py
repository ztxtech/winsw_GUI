import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class SettingsWindow(tk.Toplevel):
    """
    设置窗口，用于配置WinSW路径等全局选项。
    """

    def __init__(self, parent, settings_manager):
        super().__init__(parent)
        self.parent = parent
        self.settings_manager = settings_manager

        self.title("设置")
        self.transient(parent)  # 确保窗口显示在父窗口之上
        self.grab_set()  # 模态化，阻止与其他窗口交互
        self.resizable(False, False)

        self.create_widgets()
        self.load_settings_to_ui()

        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill="both")

        # --- WinSW 管理配置 ---
        winsw_frame = ttk.Labelframe(main_frame, text="WinSW 可执行文件管理", padding=10)
        winsw_frame.pack(fill="x")
        winsw_frame.columnconfigure(1, weight=1)

        self.mode_var = tk.StringVar()
        auto_rb = ttk.Radiobutton(
            winsw_frame,
            text="自动下载并管理 WinSW (推荐)",
            variable=self.mode_var,
            value="auto",
            command=self.toggle_custom_path_state
        )
        auto_rb.grid(row=0, column=0, columnspan=3, sticky="w")

        custom_rb = ttk.Radiobutton(
            winsw_frame,
            text="使用自定义的 WinSW.exe 文件",
            variable=self.mode_var,
            value="custom",
            command=self.toggle_custom_path_state
        )
        custom_rb.grid(row=1, column=0, columnspan=3, sticky="w")

        self.custom_path_var = tk.StringVar()
        self.custom_path_entry = ttk.Entry(winsw_frame, textvariable=self.custom_path_var, width=50)
        self.custom_path_entry.grid(row=2, column=0, columnspan=2, sticky="ew", padx=(20, 5), pady=5)

        self.browse_button = ttk.Button(winsw_frame, text="浏览...", command=self.browse_winsw)
        self.browse_button.grid(row=2, column=2, sticky="w")

        # --- 底部按钮 ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))

        save_button = ttk.Button(button_frame, text="保存", command=self.save_and_close)
        save_button.pack(side="right", padx=5)

        cancel_button = ttk.Button(button_frame, text="取消", command=self.cancel)
        cancel_button.pack(side="right")

    def toggle_custom_path_state(self):
        """根据选择的模式，启用或禁用自定义路径输入。"""
        state = "normal" if self.mode_var.get() == "custom" else "disabled"
        self.custom_path_entry.config(state=state)
        self.browse_button.config(state=state)

    def browse_winsw(self):
        """打开文件对话框选择WinSW.exe。"""
        path = filedialog.askopenfilename(
            title="选择 WinSW.exe",
            filetypes=[("Executable files", "*.exe")]
        )
        if path:
            self.custom_path_var.set(path)

    def load_settings_to_ui(self):
        """将当前设置加载到UI控件中。"""
        self.mode_var.set(self.settings_manager.get('winsw_management_mode'))
        self.custom_path_var.set(self.settings_manager.get('winsw_custom_path'))
        self.toggle_custom_path_state()

    def save_and_close(self):
        """保存UI上的设置并关闭窗口。"""
        mode = self.mode_var.get()
        custom_path = self.custom_path_var.get()

        if mode == "custom" and not os.path.exists(custom_path):
            messagebox.showerror("错误", "自定义路径无效，请选择一个存在的 WinSW.exe 文件。", parent=self)
            return

        self.settings_manager.set('winsw_management_mode', mode)
        self.settings_manager.set('winsw_custom_path', custom_path)
        self.settings_manager.save_settings()

        messagebox.showinfo("成功", "设置已保存。", parent=self)
        self.destroy()

    def cancel(self):
        """关闭窗口而不保存。"""
        self.destroy()
