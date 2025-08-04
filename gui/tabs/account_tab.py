import tkinter as tk
from tkinter import ttk


class AccountTab(ttk.Frame):
    """ “服务账户” 选项卡 """
    BUILTIN_ACCOUNTS = {
        "Local System": "LocalSystem",
        "Local Service": "NT AUTHORITY\\LocalService",
        "Network Service": "NT AUTHORITY\\NetworkService"
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        account_frame = ttk.Labelframe(self, text="服务运行账户", padding=(10, 5))
        account_frame.pack(expand=True, fill="x", padx=10, pady=10, anchor="n")

        self.account_type_var = tk.StringVar(value="Local System")

        # 创建单选按钮
        for i, (text, value) in enumerate(self.BUILTIN_ACCOUNTS.items()):
            rb = ttk.Radiobutton(
                account_frame,
                text=text,
                variable=self.account_type_var,
                value=text,  # 用显示文本作为值，方便切换
                command=self.toggle_custom_user_frame
            )
            rb.pack(anchor="w", padx=5, pady=2)

        custom_rb = ttk.Radiobutton(
            account_frame,
            text="自定义账户",
            variable=self.account_type_var,
            value="Custom",
            command=self.toggle_custom_user_frame
        )
        custom_rb.pack(anchor="w", padx=5, pady=2)

        # 自定义账户的输入框
        self.custom_user_frame = ttk.Frame(account_frame, padding=(10, 5))
        self.custom_user_frame.pack(fill="x", padx=15, pady=5)
        self.custom_user_frame.columnconfigure(1, weight=1)

        ttk.Label(self.custom_user_frame, text="用户名:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(self.custom_user_frame, textvariable=self.username_var)
        self.username_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(self.custom_user_frame, text="密码:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.custom_user_frame, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        self.allow_logon_var = tk.BooleanVar()
        self.allow_logon_check = ttk.Checkbutton(
            self.custom_user_frame,
            text="授予 '作为服务登录' 权限",
            variable=self.allow_logon_var
        )
        self.allow_logon_check.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        self.toggle_custom_user_frame()  # 初始化状态

    def toggle_custom_user_frame(self):
        """根据单选按钮状态启用或禁用自定义账户输入框"""
        state = "normal" if self.account_type_var.get() == "Custom" else "disabled"
        for child in self.custom_user_frame.winfo_children():
            child.configure(state=state)

    def set_data(self, data: dict):
        service_account = data.get('serviceaccount', {})
        username = service_account.get('username', 'LocalSystem')

        account_type = "Custom"
        for display_name, internal_name in self.BUILTIN_ACCOUNTS.items():
            if internal_name.lower() == username.lower():
                account_type = display_name
                break

        self.account_type_var.set(account_type)
        self.username_var.set(service_account.get('username', '') if account_type == "Custom" else "")
        self.password_var.set(service_account.get('password', ''))
        self.allow_logon_var.set(service_account.get('allowservicelogon', False))

        self.toggle_custom_user_frame()

    def get_data(self) -> dict:
        account_type = self.account_type_var.get()
        if account_type == "Custom":
            username = self.username_var.get()
            if not username:
                return {}  # 如果自定义但没填用户名，则不生成该节
            return {
                'serviceaccount': {
                    'username': username,
                    'password': self.password_var.get(),
                    'allowservicelogon': self.allow_logon_var.get()
                }
            }
        else:
            internal_name = self.BUILTIN_ACCOUNTS[account_type]
            return {
                'serviceaccount': {
                    'username': internal_name
                }
            }
