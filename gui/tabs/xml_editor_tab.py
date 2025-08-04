import tkinter as tk
from tkinter import ttk, messagebox


class XmlEditorTab(ttk.Frame):
    """ 直接编辑XML源码的选项卡 """

    def __init__(self, parent, main_window_callbacks):
        super().__init__(parent)
        self.get_config_from_ui = main_window_callbacks['get_config']
        self.set_config_to_ui = main_window_callbacks['set_config']
        self.config_manager_to_xml_string = main_window_callbacks['to_xml_string']
        self.config_manager_from_xml_string = main_window_callbacks['from_xml_string']

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=5)
        main_frame.pack(expand=True, fill="both")
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, sticky="ew", pady=5)

        load_button = ttk.Button(button_frame, text="从UI字段加载XML", command=self.load_from_ui)
        load_button.pack(side="left", padx=5)

        apply_button = ttk.Button(button_frame, text="应用XML到UI字段", command=self.apply_to_ui)
        apply_button.pack(side="left", padx=5)

        self.text_widget = tk.Text(main_frame, wrap="none", font=("Courier New", 10))
        v_scroll = ttk.Scrollbar(main_frame, orient="vertical", command=self.text_widget.yview)
        h_scroll = ttk.Scrollbar(main_frame, orient="horizontal", command=self.text_widget.xview)
        self.text_widget.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.text_widget.grid(row=1, column=0, sticky="nsew")
        v_scroll.grid(row=1, column=1, sticky="ns")
        h_scroll.grid(row=2, column=0, columnspan=2, sticky="ew")

    def load_from_ui(self):
        """根据当前所有UI字段生成XML并显示。"""
        config = self.get_config_from_ui()
        xml_string = self.config_manager_to_xml_string(config)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", xml_string)

    def apply_to_ui(self):
        """将当前文本框中的XML应用到所有UI字段。"""
        if not messagebox.askyesno("确认", "此操作将用XML源码覆盖所有UI字段的当前值。\n确定要继续吗？"):
            return

        xml_string = self.text_widget.get("1.0", tk.END)
        try:
            config = self.config_manager_from_xml_string(xml_string)
            self.set_config_to_ui(config)
            messagebox.showinfo("成功", "XML已成功应用到UI字段。")
        except Exception as e:
            messagebox.showerror("解析失败", f"无法解析XML，请检查语法。\n错误: {e}")
