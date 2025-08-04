import tkinter as tk
from tkinter import ttk, messagebox


class RecoveryTab(ttk.Frame):
    """ “恢复机制” 选项卡 """

    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # --- 失败操作配置 ---
        failure_frame = ttk.Labelframe(self, text="失败操作 (On Failure)", padding=(10, 5))
        failure_frame.pack(expand=True, fill="both", padx=10, pady=(10, 5))
        failure_frame.columnconfigure(0, weight=1)
        failure_frame.rowconfigure(0, weight=1)

        # 使用Treeview显示失败操作列表
        self.tree = ttk.Treeview(failure_frame, columns=("Action", "Delay"), show="headings", height=5)
        self.tree.heading("Action", text="操作")
        self.tree.heading("Delay", text="延迟")
        self.tree.column("Action", width=150, anchor="center")
        self.tree.column("Delay", width=150, anchor="center")
        self.tree.grid(row=0, column=0, columnspan=3, sticky="nsew", pady=5)

        # 添加和删除按钮
        add_button = ttk.Button(failure_frame, text="添加操作", command=self.add_action)
        add_button.grid(row=2, column=0, sticky='e', padx=5, pady=5)
        remove_button = ttk.Button(failure_frame, text="移除选中项", command=self.remove_action)
        remove_button.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        # 输入控件
        self.action_var = tk.StringVar(value="restart")
        self.action_combo = ttk.Combobox(failure_frame, textvariable=self.action_var,
                                         values=["restart", "reboot", "none"], state="readonly", width=10)
        self.action_combo.grid(row=1, column=0, sticky='e', padx=5, pady=5)

        self.delay_var = tk.StringVar(value="10 sec")
        self.delay_entry = ttk.Entry(failure_frame, textvariable=self.delay_var, width=15)
        self.delay_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)

        # --- 重置失败计数器配置 ---
        reset_frame = ttk.Labelframe(self, text="重置失败计数 (Reset Failure)", padding=(10, 5))
        reset_frame.pack(fill="x", padx=10, pady=(5, 10))
        reset_frame.columnconfigure(1, weight=1)

        ttk.Label(reset_frame, text="重置周期:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.reset_var = tk.StringVar()
        self.reset_entry = ttk.Entry(reset_frame, textvariable=self.reset_var)
        self.reset_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    def add_action(self):
        action = self.action_var.get()
        delay = self.delay_var.get()
        if not action:
            messagebox.showwarning("警告", "请选择一个操作。")
            return
        self.tree.insert("", "end", values=(action, delay))

    def remove_action(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要移除的操作。")
            return
        for item in selected_items:
            self.tree.delete(item)

    def set_data(self, data: dict):
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 加载失败操作
        on_failure_actions = data.get('onfailure', [])
        for action in on_failure_actions:
            self.tree.insert("", "end", values=(action.get('action', ''), action.get('delay', '')))

        # 加载重置周期
        self.reset_var.set(data.get('resetfailure', '1 day'))

    def get_data(self) -> dict:
        actions = []
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            actions.append({'action': values[0], 'delay': values[1]})

        return {
            'onfailure': actions,
            'resetfailure': self.reset_var.get()
        }
