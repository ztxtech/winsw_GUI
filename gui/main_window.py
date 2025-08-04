import os
import shutil
import sys
import tkinter as tk
import webbrowser
from tkinter import ttk, messagebox, filedialog

# 模块导入
from core.config_manager import ConfigManager
from core.winsw_manager import WinSWManager
from gui.actions_panel import ActionsPanel
from gui.output_console import OutputConsole
from gui.service_list_view import ServiceListView
from gui.settings_window import SettingsWindow
from gui.tabs.account_tab import AccountTab
from gui.tabs.advanced_tab import AdvancedTab
from gui.tabs.basic_info_tab import BasicInfoTab
from gui.tabs.environment_tab import EnvironmentTab
from gui.tabs.execution_tab import ExecutionTab
from gui.tabs.log_viewer_tab import LogViewerTab
from gui.tabs.logging_tab import LoggingTab
from gui.tabs.recovery_tab import RecoveryTab
from gui.tabs.xml_editor_tab import XmlEditorTab


class MainWindow(ttk.Frame):
    def __init__(self, parent, settings_manager, app_version):
        super().__init__(parent)
        self.parent = parent
        self.settings_manager = settings_manager
        self.app_version = app_version

        self.console = OutputConsole(self)
        self.config_manager = ConfigManager()
        self.winsw_manager = WinSWManager(self.console.log, self.settings_manager)

        self.current_config = self.config_manager.get_default_config()
        self.current_filepath = None

        self.create_menu(parent)
        self.create_widgets()
        self.apply_stored_settings()

        # 在UI创建完毕后，设置回调和重定向输出
        self.setup_console_redirect()

        self.service_list.refresh_list()
        # 这条 print 现在会安全地输出到UI控制台
        print("WinSW GUI 初始化完成。")

    def create_menu(self, root):
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)

        tools_menu = tk.Menu(self.menubar, tearoff=0)
        tools_menu.add_command(label="设置...", command=self.open_settings_window)
        self.menubar.add_cascade(label="工具", menu=tools_menu)

        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="项目主页 (GitHub)", command=self.open_link)
        help_menu.add_separator()
        help_menu.add_command(label="关于", command=self.show_about_dialog)
        self.menubar.add_cascade(label="帮助", menu=help_menu)

    def setup_console_redirect(self):
        """
        将标准输出和错误安全地重定向到UI控制台。
        这样可以确保 print() 在任何情况下（包括打包后）都能正常工作。
        """
        self.winsw_manager.log = self.console.log

        # 定义一个拥有 write 方法的类，用于替换 sys.stdout
        class ConsoleRedirector:
            def __init__(self, console_log_method):
                self.console_log_method = console_log_method

            def write(self, message):
                # 调用UI控制台的log方法来显示信息
                self.console_log_method(message)

            def flush(self):
                # 在此场景下，flush方法无需任何操作
                pass

        # 创建重定向器实例并替换
        redirector = ConsoleRedirector(self.console.log)
        sys.stdout = redirector
        sys.stderr = redirector

    def open_link(self):
        webbrowser.open_new(r"https://github.com/ztxtech/winsw_GUI")

    def show_about_dialog(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于 WinSW 图形化管理工具",
            f"版本: {self.app_version}\n"
            "作者: ztxtech\n"
            "这是一个用于管理 WinSW 服务的图形化界面工具。"
        )

    def open_settings_window(self):
        SettingsWindow(self.parent, self.settings_manager)

    def create_widgets(self):
        self.main_paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned_window.pack(expand=True, fill="both")

        left_frame = ttk.Frame(self.main_paned_window)
        self.service_list = ServiceListView(left_frame, self.on_service_selected)
        self.service_list.pack(expand=True, fill="both")
        self.main_paned_window.add(left_frame, weight=1)

        right_container_frame = ttk.Frame(self.main_paned_window)
        self.main_paned_window.add(right_container_frame, weight=4)

        self.right_paned_window = ttk.PanedWindow(right_container_frame, orient=tk.VERTICAL)
        self.right_paned_window.pack(expand=True, fill="both")

        right_top_frame = ttk.Frame(self.right_paned_window)
        self.right_paned_window.add(right_top_frame, weight=4)

        callbacks = {
            'new': self.new_service, 'save': self.save_service, 'import': self.import_service_xml,
            'delete': self.delete_service_config, 'install': self.install_service,
            'uninstall': self.uninstall_service, 'start': self.start_service, 'stop': self.stop_service,
            'restart': self.restart_service, 'status': self.status_service, 'refresh': self.refresh_service
        }
        self.actions_panel = ActionsPanel(right_top_frame, callbacks)
        self.actions_panel.pack(fill="x", padx=5, pady=5)

        notebook = ttk.Notebook(right_top_frame)
        notebook.pack(expand=True, fill="both", padx=5, pady=(0, 5))

        # 实例化所有Tab
        self.basic_info_tab, self.execution_tab, self.environment_tab = BasicInfoTab(notebook), ExecutionTab(notebook,
                                                                                                             self.autofill_from_executable), EnvironmentTab(
            notebook)
        self.logging_tab, self.recovery_tab, self.account_tab = LoggingTab(notebook), RecoveryTab(notebook), AccountTab(
            notebook)
        self.advanced_tab = AdvancedTab(notebook)
        xml_editor_callbacks = {'get_config': self._get_current_config_from_ui,
                                'set_config': self._set_current_config_to_ui,
                                'to_xml_string': self.config_manager.save_to_xml_string,
                                'from_xml_string': self.config_manager.load_from_xml_string}
        self.xml_editor_tab = XmlEditorTab(notebook, xml_editor_callbacks)
        self.log_viewer_tab = LogViewerTab(notebook)

        tabs = {"基本信息": self.basic_info_tab, "执行与参数": self.execution_tab, "环境变量": self.environment_tab,
                "日志记录": self.logging_tab, "恢复机制": self.recovery_tab,
                "服务账户": self.account_tab, "高级选项": self.advanced_tab, "XML源码": self.xml_editor_tab,
                "日志查看": self.log_viewer_tab}
        for text, tab in tabs.items(): notebook.add(tab, text=text)

        self.console = OutputConsole(self.right_paned_window)
        self.right_paned_window.add(self.console, weight=1)

    def apply_stored_settings(self):
        try:
            self.parent.geometry(self.settings_manager.get('window_geometry'))
            self.parent.after(100,
                              lambda: self.main_paned_window.sashpos(0, self.settings_manager.get('main_sash_pos')))
            self.parent.after(100,
                              lambda: self.right_paned_window.sashpos(0, self.settings_manager.get('right_sash_pos')))
        except tk.TclError as e:
            print(f"应用保存的设置时出错 (可能是首次启动): {e}")

    def save_current_settings(self):
        self.settings_manager.set('window_geometry', self.parent.winfo_geometry())
        self.settings_manager.set('main_sash_pos', self.main_paned_window.sashpos(0))
        self.settings_manager.set('right_sash_pos', self.right_paned_window.sashpos(0))
        self.settings_manager.save_settings()
        print("窗口状态已保存。")

    def _get_current_config_from_ui(self) -> dict:
        config = self.basic_info_tab.get_data()
        config.update(self.execution_tab.get_data())
        config.update(self.environment_tab.get_data())
        config.update(self.logging_tab.get_data())
        config.update(self.recovery_tab.get_data())
        config.update(self.account_tab.get_data())
        config.update(self.advanced_tab.get_data())
        return config

    def _set_current_config_to_ui(self, config):
        self.current_config = config
        self.basic_info_tab.set_data(self.current_config)
        self.execution_tab.set_data(self.current_config)
        self.environment_tab.set_data(self.current_config)
        self.logging_tab.set_data(self.current_config)
        self.recovery_tab.set_data(self.current_config)
        self.account_tab.set_data(self.current_config)
        self.advanced_tab.set_data(self.current_config)

    def on_service_selected(self, filename: str):
        self.log_viewer_tab.stop_monitoring()
        self.current_filepath = os.path.join("services", filename)
        print(f"已选择服务: {filename}")
        self.current_config = self.config_manager.load_from_xml(self.current_filepath)
        self._set_current_config_to_ui(self.current_config)
        print("配置已加载到UI。")
        self.xml_editor_tab.load_from_ui()
        self.log_viewer_tab.start_monitoring(self.current_config)

    def new_service(self):
        print("正在创建新配置...")
        self.log_viewer_tab.stop_monitoring()
        self.current_filepath = None
        self.current_config = self.config_manager.get_default_config()
        self._set_current_config_to_ui(self.current_config)
        self.xml_editor_tab.load_from_ui()
        self.service_list.listbox.selection_clear(0, 'end')
        print("UI已重置为新配置。")

    def autofill_from_executable(self, exe_path: str):
        if not self.basic_info_tab.id_var.get() and not self.basic_info_tab.name_var.get():
            try:
                service_id, _ = os.path.splitext(os.path.basename(exe_path))
                self.basic_info_tab.id_var.set(service_id)
                self.basic_info_tab.name_var.set(service_id.capitalize())
                print(f"已自动填充服务ID和名称: '{service_id}'")
            except Exception as e:
                print(f"自动填充失败: {e}")

    def save_service(self):
        # 1. 从UI收集最新数据
        config_data = self._get_current_config_from_ui()

        # 2. 验证核心字段
        service_id = config_data.get('id')
        if not service_id:
            messagebox.showerror("错误", "服务 ID 不能为空！")
            return

        # --- 新增逻辑：处理默认日志路径 ---
        if not config_data.get('logpath'):
            app_root_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
            default_log_path = os.path.join(app_root_dir, 'logs', service_id)

            # 更新数据字典和UI
            config_data['logpath'] = default_log_path
            self.logging_tab.log_path_var.set(default_log_path)
            print(f"日志目录为空，已自动设置为: {default_log_path}")

        # 确保日志目录存在
        log_path_to_create = config_data.get('logpath')
        if log_path_to_create:
            os.makedirs(log_path_to_create, exist_ok=True)
        # --- 逻辑结束 ---

        # 3. 确定保存路径
        self.current_filepath = os.path.join("services", f"{service_id}.xml")

        # 4. 执行保存 (使用更新后的config_data)
        print(f"正在保存配置到: {self.current_filepath}")
        self.config_manager.save_to_xml(config_data, self.current_filepath)
        print("保存成功！")

        # 5. 刷新UI
        self.service_list.refresh_list()
        self.xml_editor_tab.load_from_ui()

    def delete_service_config(self):
        selected_file = self.service_list.get_selected_filename()
        if not selected_file:
            messagebox.showwarning("操作无效", "请先从列表中选择一个服务配置。")
            return
        if messagebox.askyesno("确认删除", f"你确定要删除配置文件 '{selected_file}' 吗？\n此操作不可恢复。"):
            try:
                os.remove(os.path.join("services", selected_file))
                print(f"配置文件 '{selected_file}' 已删除。")
                self.service_list.refresh_list()
                self.new_service()
            except OSError as e:
                messagebox.showerror("删除失败", f"无法删除文件: {e}")

    def import_service_xml(self):
        filepath = filedialog.askopenfilename(title="选择要导入的WinSW XML配置文件", filetypes=[("XML files", "*.xml")])
        if not filepath: return
        try:
            dest_path = os.path.join("services", os.path.basename(filepath))
            if os.path.exists(dest_path) and not messagebox.askyesno("文件已存在",
                                                                     f"'{os.path.basename(filepath)}' 已存在。\n要覆盖它吗？"):
                return
            shutil.copy(filepath, dest_path)
            print(f"成功导入 '{os.path.basename(filepath)}'。")
            self.service_list.refresh_list()
        except Exception as e:
            messagebox.showerror("导入失败", f"无法导入文件: {e}")

    def _execute_service_command(self, command_func):
        # 修正：在执行命令前，应先调用save_service以确保XML文件是最新的
        self.save_service()
        if not self.current_filepath or not os.path.exists(self.current_filepath):
            messagebox.showwarning("警告", "请先保存有效的服务配置。")
            return

        # save_service已经更新了self.current_config,所以这里直接用
        service_id = self._get_current_config_from_ui().get('id')
        if messagebox.askyesno("确认操作", f"你确定要对服务 '{service_id}' 执行此操作吗？"):
            command_func(self._get_current_config_from_ui())

    def install_service(self):
        self._execute_service_command(self.winsw_manager.install)

    def uninstall_service(self):
        self._execute_service_command(self.winsw_manager.uninstall)

    def start_service(self):
        self._execute_service_command(self.winsw_manager.start)

    def stop_service(self):
        self._execute_service_command(self.winsw_manager.stop)

    def restart_service(self):
        self._execute_service_command(self.winsw_manager.restart)

    def status_service(self):
        self._execute_service_command(self.winsw_manager.status)

    def refresh_service(self):
        self._execute_service_command(self.winsw_manager.refresh)
