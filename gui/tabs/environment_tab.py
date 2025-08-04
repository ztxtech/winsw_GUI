import tkinter as tk
from tkinter import ttk, messagebox


class EnvironmentTab(ttk.Frame):
    """ “环境变量” 选项卡 """

    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        env_frame = ttk.Labelframe(self, text="为服务进程设置环境变量", padding=(10, 5))
        env_frame.pack(expand=True, fill="both", padx=10, pady=10)
        env_frame.columnconfigure(0, weight=1)
        env_frame.rowconfigure(0, weight=1)

        # --- Treeview for displaying variables ---
        self.tree = ttk.Treeview(env_frame, columns=("Name", "Value"), show="headings", height=8)
        self.tree.heading("Name", text="变量名")
        self.tree.heading("Value", text="变量值")
        self.tree.column("Name", width=200)
        self.tree.column("Value", width=400)
        self.tree.grid(row=0, column=0, sticky="nsew", pady=5)

        # --- Frame for input controls and buttons ---
        input_frame = ttk.Frame(env_frame)
        input_frame.grid(row=1, column=0, sticky="ew", pady=5)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=2)

        # Input widgets
        ttk.Label(input_frame, text="变量名:").grid(row=0, column=0, padx=(0, 5))
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(input_frame, textvariable=self.name_var)
        self.name_entry.grid(row=0, column=1, sticky='ew')

        ttk.Label(input_frame, text="变量值:").grid(row=0, column=2, padx=(10, 5))
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(input_frame, textvariable=self.value_var)
        self.value_entry.grid(row=0, column=3, sticky='ew')

        # Action buttons
        add_button = ttk.Button(input_frame, text="添加", command=self.add_variable)
        add_button.grid(row=0, column=4, padx=(10, 5))

        remove_button = ttk.Button(input_frame, text="移除选中项", command=self.remove_variable)
        remove_button.grid(row=0, column=5, padx=5)

    def add_variable(self):
        name = self.name_var.get().strip()
        value = self.value_var.get()
        if not name:
            messagebox.showwarning("警告", "变量名不能为空。")
            return
        self.tree.insert("", "end", values=(name, value))
        self.name_var.set("")
        self.value_var.set("")

    def remove_variable(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要移除的变量。")
            return
        for item in selected_items:
            self.tree.delete(item)

    def set_data(self, data: dict):
        for item in self.tree.get_children():
            self.tree.delete(item)

        environments = data.get('environments', [])
        for env in environments:
            self.tree.insert("", "end", values=(env.get('name', ''), env.get('value', '')))

    def get_data(self) -> dict:
        environments = []
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            environments.append({'name': values[0], 'value': values[1]})

        return {'environments': environments}
