from tkinter import ttk


class ActionsPanel(ttk.Frame):
    """ 包含所有操作按钮的面板 """

    def __init__(self, parent, callbacks: dict):
        super().__init__(parent)

        # 第一行：配置管理按钮
        config_frame = ttk.Labelframe(self, text="配置管理")
        config_frame.pack(side="top", fill="x", padx=5, pady=(5, 2))

        # 内部按钮横向排列，并允许拉伸
        ttk.Button(config_frame, text="新建", command=callbacks['new']).pack(side="left", expand=True, fill="x", padx=5,
                                                                             pady=2)
        ttk.Button(config_frame, text="保存", command=callbacks['save']).pack(side="left", expand=True, fill="x",
                                                                              padx=5, pady=2)
        ttk.Button(config_frame, text="导入...", command=callbacks['import']).pack(side="left", expand=True, fill="x",
                                                                                   padx=5, pady=2)
        ttk.Button(config_frame, text="删除", command=callbacks['delete']).pack(side="left", expand=True, fill="x",
                                                                                padx=5, pady=2)

        # 第二行：服务控制按钮
        control_frame = ttk.Labelframe(self, text="服务控制")
        control_frame.pack(side="top", fill="x", padx=5, pady=(2, 5))

        # 内部按钮横向排列，并允许拉伸
        ttk.Button(control_frame, text="安装", command=callbacks['install']).pack(side="left", expand=True, fill="x",
                                                                                  padx=5, pady=2)
        ttk.Button(control_frame, text="卸载", command=callbacks['uninstall']).pack(side="left", expand=True, fill="x",
                                                                                    padx=5, pady=2)
        ttk.Button(control_frame, text="启动", command=callbacks['start']).pack(side="left", expand=True, fill="x",
                                                                                padx=5, pady=2)
        ttk.Button(control_frame, text="停止", command=callbacks['stop']).pack(side="left", expand=True, fill="x",
                                                                               padx=5, pady=2)
        ttk.Button(control_frame, text="重启", command=callbacks['restart']).pack(side="left", expand=True, fill="x",
                                                                                  padx=5, pady=2)
        ttk.Button(control_frame, text="刷新", command=callbacks['refresh']).pack(side="left", expand=True, fill="x",
                                                                                  padx=5, pady=2)
        ttk.Button(control_frame, text="状态", command=callbacks['status']).pack(side="left", expand=True, fill="x",
                                                                                 padx=5, pady=2)
